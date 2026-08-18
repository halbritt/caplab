package cli

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// armWakeTimer makes no-daemon-runtime.md's claim true: after every drive
// session the durable systemd user timer is rewritten to the session's own
// computed next horizon (plus the periodic floor), so promptness survives
// process death and reboots — liveness is the system's property, never a
// watcher's. Arming is best-effort by design: a host without a systemd user
// manager gets a session note, never a failed drive. STRIATUM_NO_WAKE_TIMER
// disables it (tests, containers).
//
// The config must be the session's resolved snapshot (the Config
// openGraphAndCatalog returned), never the raw flag parse: the timer's argv
// re-emits the effective catalog-overlay list as explicit -catalog-overlay
// pairs, so a wake from the standing timer resolves the same merged catalog
// the session did without re-reading registration
// (fleet-catalog-resolution@2).
func armWakeTimer(config Config, repoID, nextHorizon string, floor time.Duration) (string, error) {
	if os.Getenv("STRIATUM_NO_WAKE_TIMER") != "" {
		return "", nil
	}
	argv := wakeCommand(config)
	if argv == nil {
		return "", fmt.Errorf("wake argv underivable")
	}
	argv = append(argv, "-trigger", "timer")

	unitDir := filepath.Join(userConfigHome(), "systemd", "user")
	if err := os.MkdirAll(unitDir, 0o755); err != nil {
		return "", err
	}
	name := "striatum-wake-" + shortRepoID(repoID)
	service, timer := wakeTimerUnits(name, argv, nextHorizon, floor)
	if err := os.WriteFile(filepath.Join(unitDir, name+".service"), []byte(service), 0o644); err != nil {
		return "", err
	}
	if err := os.WriteFile(filepath.Join(unitDir, name+".timer"), []byte(timer), 0o644); err != nil {
		return "", err
	}
	for _, args := range [][]string{
		{"daemon-reload"},
		{"enable", "--now", name + ".timer"},
	} {
		cmd := exec.Command("systemctl", append([]string{"--user"}, args...)...)
		if out, err := cmd.CombinedOutput(); err != nil {
			return "", fmt.Errorf("systemctl --user %s: %v: %s", strings.Join(args, " "), err, strings.TrimSpace(string(out)))
		}
	}
	return name + ".timer", nil
}

// wakeTimerUnits renders the service/timer unit pair. The timer carries the
// periodic floor always, plus OnCalendar at the computed next horizon when
// one exists; Persistent fires a missed horizon at the next boot.
func wakeTimerUnits(name string, argv []string, nextHorizon string, floor time.Duration) (string, string) {
	if floor <= 0 {
		floor = 15 * time.Minute
	}
	floorSpec := fmt.Sprintf("%ds", int(floor.Seconds()))
	quoted := make([]string, len(argv))
	for i, arg := range argv {
		quoted[i] = strings.ReplaceAll(arg, `"`, ``)
		if quoted[i] == "" {
			// An empty argv element must survive the space-join below:
			// rendered bare it vanishes, and systemd would parse the next
			// token as the value of the preceding flag — a corrupted
			// invocation. systemd's ExecStart empty-argument form is a
			// literal "" (checks-resolve-to-repo@2 pins an explicit-empty
			// -checks decision on this surface).
			quoted[i] = `""`
		}
	}
	service := "" +
		"[Unit]\n" +
		"Description=Striatum liveness wake (" + name + ")\n\n" +
		"[Service]\n" +
		"Type=oneshot\n" +
		"ExecStart=" + strings.Join(quoted, " ") + "\n" +
		// Exit 5 (quiescent-blocked) and 4 (lease busy) are healthy wakes.
		"SuccessExitStatus=4 5\n"

	timerLines := []string{
		"[Unit]",
		"Description=Striatum liveness floor (" + name + ")",
		"",
		"[Timer]",
		"OnActiveSec=" + floorSpec,
		"OnUnitInactiveSec=" + floorSpec,
		"Persistent=true",
	}
	if horizon := parseHorizon(nextHorizon); horizon != "" {
		timerLines = append(timerLines, "OnCalendar="+horizon)
	}
	timerLines = append(timerLines, "", "[Install]", "WantedBy=timers.target", "")
	return service, strings.Join(timerLines, "\n")
}

// parseHorizon renders an RFC3339 horizon as a systemd OnCalendar timestamp
// (UTC); anything unparseable yields no calendar entry — the floor stands.
func parseHorizon(horizon string) string {
	if horizon == "" {
		return ""
	}
	at, err := time.Parse(time.RFC3339, horizon)
	if err != nil {
		return ""
	}
	return at.UTC().Format("2006-01-02 15:04:05 UTC")
}

func shortRepoID(repoID string) string {
	cleaned := strings.ReplaceAll(repoID, "-", "")
	if len(cleaned) > 8 {
		return cleaned[:8]
	}
	if cleaned == "" {
		return "default"
	}
	return cleaned
}

func userConfigHome() string {
	if xdg := os.Getenv("XDG_CONFIG_HOME"); xdg != "" {
		return xdg
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return "."
	}
	return filepath.Join(home, ".config")
}
