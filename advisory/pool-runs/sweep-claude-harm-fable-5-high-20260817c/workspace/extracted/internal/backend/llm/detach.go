package llm

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"github.com/halbritt/striatum-next/internal/backend"
)

// supervisorHint is the Advisory Signal naming a live Lane Supervisor's
// signalable kill domain (D0013.C5): written by the dispatch verb only,
// after the domain is verified signalable and before success; deletable at
// will; never read above the seam. Its loss costs abort its reach over that
// lane's remaining budget window, never correctness.
type supervisorHint struct {
	PID        int    `json:"pid"`
	PGID       int    `json:"pgid"`
	StartToken string `json:"start_token"`
	WrittenAt  string `json:"written_at"`
}

func hintPath(spool backend.Spool, dispatchID string) string {
	return filepath.Join(spool.AdvisoryDir(dispatchID), "supervisor.json")
}

func readHint(spool backend.Spool, dispatchID string) (supervisorHint, error) {
	var hint supervisorHint
	raw, err := os.ReadFile(hintPath(spool, dispatchID))
	if err != nil {
		return hint, err
	}
	if err := json.Unmarshal(raw, &hint); err != nil {
		return hint, err
	}
	if hint.PID <= 0 || hint.PGID <= 0 || hint.StartToken == "" {
		return hint, errors.New("llm: malformed supervisor hint")
	}
	return hint, nil
}

// writeHint create-or-replaces the hint via temp-file + rename: the
// same-id-retry world keeps the hint naming the most recent fork. No fsync
// — the hint is advisory; its loss is priced, never load-bearing.
func writeHint(spool backend.Spool, dispatchID string, hint supervisorHint) error {
	dir := spool.AdvisoryDir(dispatchID)
	if err := os.MkdirAll(dir, 0o700); err != nil {
		return err
	}
	raw, err := json.Marshal(hint)
	if err != nil {
		return err
	}
	tmp := filepath.Join(dir, ".supervisor.json.tmp")
	if err := os.WriteFile(tmp, raw, 0o600); err != nil {
		return err
	}
	return os.Rename(tmp, filepath.Join(dir, "supervisor.json"))
}

// startToken pins one process incarnation: boot id plus the kernel's
// starttime for the pid, guarding every hint read against pid reuse.
func startToken(pid int) (string, error) {
	boot, err := os.ReadFile("/proc/sys/kernel/random/boot_id")
	if err != nil {
		return "", err
	}
	stat, err := os.ReadFile(fmt.Sprintf("/proc/%d/stat", pid))
	if err != nil {
		return "", err
	}
	// comm may contain anything including ')'; fields resume after the
	// last closing paren. starttime is overall field 22, so field 20 of
	// the remainder that starts with state.
	text := string(stat)
	closing := strings.LastIndexByte(text, ')')
	if closing < 0 {
		return "", fmt.Errorf("llm: unparseable stat for pid %d", pid)
	}
	fields := strings.Fields(text[closing+1:])
	if len(fields) < 20 {
		return "", fmt.Errorf("llm: short stat for pid %d", pid)
	}
	return strings.TrimSpace(string(boot)) + ":" + fields[19], nil
}

// hintTokenLive reports whether the hint's token still names a live
// incarnation. Token verification only — the non-authoritative idempotence
// branch needs no signalability (D0013.C1: a wrong hint's worst case is a
// duplicate execution, lawful under pass purity and the rename winner).
func hintTokenLive(hint supervisorHint) bool {
	token, err := startToken(hint.PID)
	return err == nil && token == hint.StartToken
}

// handshake is the readiness payload the supervision entry writes on its
// inherited pipe: post-exec, so readiness also proves exec succeeded.
type handshake struct {
	PID        int    `json:"pid"`
	PGID       int    `json:"pgid"`
	StartToken string `json:"start_token"`
}

// detach realizes the dispatch verb's accepted order (D0013.C1/C5): fork
// the detached Lane Supervisor, confirm its signalable kill domain, write
// the Supervisor Hint, and only then succeed. Acceptance is never visible
// without a usable kill handle on disk.
func (a *Adapter) detach(manifest backend.DispatchManifest, manifestPath string) (string, error) {
	if len(a.Surface) == 0 {
		return "", errors.New("llm: no supervisor surface configured")
	}
	surface, err := resolveSurface(a.Surface[0])
	if err != nil {
		return "", Refusal{Code: RefusalRuntimeUnavailable, Detail: err.Error()}
	}
	absManifest, err := filepath.Abs(manifestPath)
	if err != nil {
		return "", err
	}
	absSpool, err := filepath.Abs(a.Spool.Root)
	if err != nil {
		return "", err
	}

	// Supervisor-owned residue lives in the outer workspace tree; the
	// detached stdio log lands there, outside the A2 per-attempt reset.
	workspace := a.Spool.WorkspaceDir(manifest.DispatchID)
	if err := os.MkdirAll(workspace, 0o700); err != nil {
		return "", err
	}
	logFile, err := os.OpenFile(supervisorLogPath(a.Spool, manifest.DispatchID),
		os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o600)
	if err != nil {
		return "", err
	}
	defer logFile.Close()

	ready, readyWrite, err := os.Pipe()
	if err != nil {
		return "", err
	}
	defer ready.Close()

	args := append([]string{}, a.Surface[1:]...)
	args = append(args, superviseEntry,
		"-manifest", absManifest,
		"-spool", absSpool,
		"-ready-fd", "3",
	)
	if a.Declaration != "" {
		abs, err := filepath.Abs(a.Declaration)
		if err != nil {
			return "", err
		}
		args = append(args, "-declaration", abs)
	}
	if a.KeysDir != "" {
		args = append(args, "-keys", a.KeysDir)
	}
	if a.IsolationDir != "" {
		args = append(args, "-isolation", a.IsolationDir)
	}
	if len(a.WakeCmd) > 0 {
		encoded, err := json.Marshal(a.WakeCmd)
		if err != nil {
			return "", err
		}
		args = append(args, "-wake-cmd", string(encoded))
	}
	cmd := exec.Command(surface, args...)
	cmd.Dir = workspace
	cmd.Stdout = logFile
	cmd.Stderr = logFile
	cmd.ExtraFiles = []*os.File{readyWrite}
	// Setsid: the kernel establishes the new session and process group
	// between fork and exec — the kill domain (pgid = child pid) exists
	// the instant Start returns.
	cmd.SysProcAttr = &syscall.SysProcAttr{Setsid: true}
	if err := cmd.Start(); err != nil {
		readyWrite.Close()
		return "", err
	}
	readyWrite.Close()
	// The supervisor outlives this verb; reap it whenever it finishes so
	// a long-lived caller accumulates no zombies.
	go func() { _ = cmd.Wait() }()

	shake, err := readHandshake(ready, 15*time.Second)
	if err != nil {
		// Nothing was accepted: no hint, no success. Best-effort kill of
		// whatever half-started.
		_ = syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
		return "", fmt.Errorf("llm: supervisor readiness failed: %w", err)
	}
	if shake.PID != cmd.Process.Pid || shake.PGID != cmd.Process.Pid {
		_ = syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
		return "", fmt.Errorf("llm: handshake names pid %d pgid %d, forked %d", shake.PID, shake.PGID, cmd.Process.Pid)
	}
	// Signalability verification, verb-side: the named kill domain must
	// be reachable before the hint may exist (D0013.C5).
	if err := syscall.Kill(-shake.PGID, 0); err != nil {
		return "", fmt.Errorf("llm: kill domain %d not signalable: %w", shake.PGID, err)
	}
	token, err := startToken(shake.PID)
	if err != nil || token != shake.StartToken {
		_ = syscall.Kill(-shake.PGID, syscall.SIGKILL)
		return "", fmt.Errorf("llm: start token mismatch for supervisor %d", shake.PID)
	}

	hint := supervisorHint{
		PID: shake.PID, PGID: shake.PGID, StartToken: token,
		WrittenAt: a.now().UTC().Format(time.RFC3339),
	}
	if err := writeHint(a.Spool, manifest.DispatchID, hint); err != nil {
		_ = syscall.Kill(-shake.PGID, syscall.SIGKILL)
		return "", err
	}
	return a.Spool.SubmissionDir(manifest.DispatchID), nil
}

func readHandshake(ready *os.File, within time.Duration) (handshake, error) {
	var shake handshake
	if err := ready.SetReadDeadline(time.Now().Add(within)); err != nil {
		return shake, err
	}
	raw := make([]byte, 512)
	n, err := ready.Read(raw)
	if err != nil {
		return shake, err
	}
	if err := json.Unmarshal(raw[:n], &shake); err != nil {
		return shake, err
	}
	if shake.PID <= 0 || shake.PGID <= 0 || shake.StartToken == "" {
		return shake, errors.New("incomplete handshake")
	}
	return shake, nil
}

// resolveSurface locates the supervisor exec target: an explicit path is
// used as-is; a bare name resolves on PATH.
func resolveSurface(name string) (string, error) {
	if strings.ContainsRune(name, os.PathSeparator) {
		if _, err := os.Stat(name); err != nil {
			return "", err
		}
		return name, nil
	}
	return exec.LookPath(name)
}

func (a *Adapter) now() time.Time {
	if a.Now != nil {
		return a.Now()
	}
	return time.Now()
}

// writeHandshake is the supervision entry's side: its readiness payload
// names its own kill domain, computed post-exec.
func writeHandshake(fd int) error {
	pid := os.Getpid()
	token, err := startToken(pid)
	if err != nil {
		return err
	}
	raw, err := json.Marshal(handshake{PID: pid, PGID: syscall.Getpgrp(), StartToken: token})
	if err != nil {
		return err
	}
	pipe := os.NewFile(uintptr(fd), "ready")
	if pipe == nil {
		return fmt.Errorf("llm: ready fd %d unavailable", fd)
	}
	defer pipe.Close()
	_, err = pipe.Write(raw)
	return err
}

// supervisorLogPath is the detached supervisor's own stdio log inside its
// workspace directory (outside the A2 per-attempt work reset): opened here
// at fork time as the exec'd process's stdout/stderr, and read back by the
// supervisor itself at death for the terminal report's admitted tail
// (readFileTail) and the retained-log copy (retainSupervisorLog) that
// survives past reclaim at Spool.RetainedLogPath.
func supervisorLogPath(spool backend.Spool, dispatchID string) string {
	return filepath.Join(spool.WorkspaceDir(dispatchID), "supervisor.log")
}

// readFileTail returns up to the last maxBytes bytes of the file at path, or
// "" if it cannot be opened or read. WriteTerminalReport applies the
// authoritative UTF-8-safe bound on whatever this feeds it as
// SupervisorTail; this only avoids reading an unbounded log into memory
// before that trim.
func readFileTail(path string, maxBytes int) string {
	file, err := os.Open(path)
	if err != nil {
		return ""
	}
	defer file.Close()
	info, err := file.Stat()
	if err != nil {
		return ""
	}
	if size := info.Size(); size > int64(maxBytes) {
		if _, err := file.Seek(-int64(maxBytes), io.SeekEnd); err != nil {
			return ""
		}
	}
	raw, err := io.ReadAll(file)
	if err != nil {
		return ""
	}
	return string(raw)
}

// retainSupervisorLog copies the detached supervisor's stdio log to its
// driver-visible retained home (Spool.RetainedLogPath) before its only
// on-disk copy — inside the workspace tree — is unlinked, whether by the
// supervisor's own controlled exit (Supervisor.Run), an operator Abort, or
// the janitor sweep reclaiming a dead lane's residue: every residue-removing
// path preserves the log first, under the declared retention window
// (schema/exit_report.yaml supervisor_log_retention_seconds). Best-effort
// and idempotent: a missing or unreadable log, or a home already retained,
// leaves nothing to do and never blocks or fails the reclaim it precedes.
func retainSupervisorLog(spool backend.Spool, dispatchID string) {
	raw, err := os.ReadFile(supervisorLogPath(spool, dispatchID))
	if err != nil {
		return
	}
	target := spool.RetainedLogPath(dispatchID)
	if _, err := os.Stat(target); err == nil {
		return
	}
	targetDir := filepath.Dir(target)
	staging := targetDir + ".tmp"
	if err := os.RemoveAll(staging); err != nil {
		return
	}
	if err := os.MkdirAll(staging, 0o700); err != nil {
		return
	}
	if err := writeFileDurable(filepath.Join(staging, filepath.Base(target)), raw); err != nil {
		return
	}
	_ = os.Rename(staging, targetDir)
}

