// Package cli implements the striatum control surface: one binary, stable
// --json output, and the workstation's sole ledger read surface (RFC 0006).
package cli

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/halbritt/striatum-next/internal/backend"
	"github.com/halbritt/striatum-next/internal/backend/llm"
	"github.com/halbritt/striatum-next/internal/backend/local"
	"github.com/halbritt/striatum-next/internal/driver"
	"github.com/halbritt/striatum-next/internal/store"
)

// Exit codes (RFC 0006): 0 satisfied/idle, 1 usage, 2 refusal, 3 parked,
// 4 drive lease held, 5 quiescent-blocked.
const (
	ExitOK      = 0
	ExitUsage   = 1
	ExitRefusal = 2
	ExitParked  = 3
	ExitBusy    = 4
	ExitBlocked = 5
)

// stringList accumulates a repeatable string flag in invocation order.
type stringList []string

func (l *stringList) String() string { return strings.Join(*l, ",") }

func (l *stringList) Set(value string) error {
	*l = append(*l, value)
	return nil
}

// Config carries the resolved global flags.
type Config struct {
	Repo        string
	DataHome    string
	CatalogDir  string
	Overlays    stringList
	BackendsDir string
	PolicyPath  string
	ChecksPath  string
	// ChecksExplicit records whether -checks was set on the invocation —
	// a parse-time fact, never a value comparison, so an operator passing
	// the default string or the empty string is explicit
	// (checks-resolve-to-repo@2). Check-registry precedence branches on it:
	// true honors ChecksPath under the untouched @1 resolution rule and
	// never consults registration; false opts into registration-derived
	// resolution. Programmatic constructors wanting flag-override semantics
	// must set it.
	ChecksExplicit bool
	JSON           bool
	Out            *os.File
	Runtime        local.Runtime
	Now            func() time.Time
}

// Main runs one CLI invocation and returns its exit code.
func Main(args []string) int {
	config := Config{Out: os.Stdout, Now: time.Now}
	flags := flag.NewFlagSet("striatum", flag.ContinueOnError)
	flags.StringVar(&config.Repo, "repo", ".", "target repository working tree")
	flags.StringVar(&config.DataHome, "data-home", defaultDataHome(), "XDG data home holding Graph Stores")
	flags.StringVar(&config.CatalogDir, "catalog", "catalog", "compiler catalog directory")
	flags.Var(&config.Overlays, "catalog-overlay", "overlay catalog root contributing target-states (repeatable; layered over -catalog, later wins)")
	flags.StringVar(&config.BackendsDir, "backends", "backends", "backend declarations directory")
	flags.StringVar(&config.PolicyPath, "policy", "policy/driver.yaml", "driver policy file")
	flags.StringVar(&config.ChecksPath, "checks", "policy/checks/repository.json", "check registry file")
	flags.BoolVar(&config.JSON, "json", false, "stable JSON output")
	if err := flags.Parse(args); err != nil {
		return ExitUsage
	}
	// flag.Visit reports exactly the flags that were set, so explicitness is
	// a parse-time fact: -checks with the default string or the empty string
	// is explicit, and precedence never compares the value to the default.
	flags.Visit(func(f *flag.Flag) {
		if f.Name == "checks" {
			config.ChecksExplicit = true
		}
	})
	rest := flags.Args()
	if len(rest) == 0 {
		fmt.Fprintln(os.Stderr, "usage: striatum [flags] <init|request|cancel|drive|status|accept|reject|resolve|revoke|reconcile|ledger>")
		return ExitUsage
	}
	code, err := Run(config, rest[0], rest[1:])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
	}
	return code
}

// Run executes one verb under a resolved configuration.
func Run(config Config, verb string, args []string) (int, error) {
	if config.Out == nil {
		config.Out = os.Stdout
	}
	if config.Now == nil {
		config.Now = time.Now
	}
	switch verb {
	case "init":
		return runInit(config, args)
	case "request":
		return runRequest(config, args)
	case "cancel":
		return runCancel(config, args)
	case "drive":
		return runDrive(config, args)
	case "status":
		return runStatus(config)
	case "accept":
		return runAcceptance(config, args, true)
	case "reject":
		return runAcceptance(config, args, false)
	case "resolve":
		return runResolve(config, args)
	case "revoke":
		return runRevoke(config, args)
	case "reconcile":
		return runReconcile(config, args)
	case "ledger":
		return runLedger(config, args)
	default:
		return ExitUsage, fmt.Errorf("striatum: unknown verb %q", verb)
	}
}

func runInit(config Config, args []string) (int, error) {
	flags := flag.NewFlagSet("init", flag.ContinueOnError)
	repoID := flags.String("repo-id", "", "repository id (UUIDv7; minted when absent)")
	rootCommit := flags.String("root-commit", "", "git root commit (discovered when absent)")
	humanName := flags.String("name", "", "human-readable graph name")
	if err := flags.Parse(args); err != nil {
		return ExitUsage, err
	}
	if *repoID == "" {
		existing, err := readRepoID(config.Repo)
		if err == nil && existing != "" {
			*repoID = existing
		} else {
			minted, err := newUUIDv7(config.Now())
			if err != nil {
				return ExitRefusal, err
			}
			*repoID = minted
		}
	}
	if *rootCommit == "" {
		discovered, err := discoverRootCommit(config.Repo)
		if err != nil {
			return ExitRefusal, fmt.Errorf("striatum init: cannot discover root commit (pass --root-commit): %w", err)
		}
		*rootCommit = discovered
	}
	graph, err := store.InitGraph(store.InitOptions{
		DataHome:        config.DataHome,
		RepoRoot:        config.Repo,
		RepoID:          *repoID,
		RootCommit:      *rootCommit,
		HumanName:       *humanName,
		CompilerVersion: "v0-spine",
		Now:             config.Now,
	})
	if err != nil {
		return ExitRefusal, err
	}
	fmt.Fprintf(config.Out, "initialized graph %s at %s\n", graph.RepoID, graph.GraphDir)
	return ExitOK, nil
}

func runRequest(config Config, args []string) (int, error) {
	positionals, rest := splitLeadingPositionals(args)
	flags := flag.NewFlagSet("request", flag.ContinueOnError)
	target := flags.String("target", "", "target state id")
	note := flags.String("note", "", "request note (the Principal's utterance for capture targets)")
	if err := flags.Parse(rest); err != nil {
		return ExitUsage, err
	}
	positionals = append(positionals, flags.Args()...)
	if len(positionals) != 1 || *target == "" {
		return ExitUsage, errors.New("usage: striatum request <subject> --target <state> [--note text]")
	}
	graph, catalog, _, err := openGraphAndCatalog(config)
	if err != nil {
		return ExitRefusal, err
	}
	seq, err := driver.IssueRequest(graph, catalog, driver.RequestOptions{
		Subject:   positionals[0],
		TargetID:  *target,
		Note:      *note,
		Principal: principalIdentity(),
		Now:       config.Now,
	})
	if err != nil {
		return ExitRefusal, err
	}
	fmt.Fprintf(config.Out, "request %d issued: %s -> %s\n", seq, positionals[0], *target)
	return ExitOK, nil
}

func runCancel(config Config, args []string) (int, error) {
	positionals, rest := splitLeadingPositionals(args)
	flags := flag.NewFlagSet("cancel", flag.ContinueOnError)
	reason := flags.String("reason", "", "cancellation reason")
	if err := flags.Parse(rest); err != nil {
		return ExitUsage, err
	}
	positionals = append(positionals, flags.Args()...)
	if len(positionals) != 1 {
		return ExitUsage, errors.New("usage: striatum cancel <request-seq> [--reason text]")
	}
	requestRef, err := strconv.ParseUint(positionals[0], 10, 64)
	if err != nil {
		return ExitUsage, errors.New("usage: striatum cancel <request-seq> [--reason text]")
	}
	graph, _, _, err := openGraphAndCatalog(config)
	if err != nil {
		return ExitRefusal, err
	}
	seq, err := driver.RecordCancellation(graph, requestRef, *reason, principalIdentity(), config.Now)
	if err != nil {
		return ExitRefusal, err
	}
	// Append-only, no post-cancel drive (RFC 0006, design alternative A6):
	// cancellation creates no new work to advance — the next session,
	// whenever triggered, plans less.
	fmt.Fprintf(config.Out, "cancellation %d appended for request %d\n", seq, requestRef)
	return ExitOK, nil
}

func runDrive(config Config, args []string) (int, error) {
	flags := flag.NewFlagSet("drive", flag.ContinueOnError)
	trigger := flags.String("trigger", "principal", "wake trigger attribution")
	if err := flags.Parse(args); err != nil {
		return ExitUsage, err
	}
	session, config, err := buildSession(config)
	if err != nil {
		return ExitRefusal, err
	}
	session.Trigger = *trigger
	report, err := session.Drive()
	if err != nil {
		if errors.Is(err, driver.ErrDriveLeaseBusy) {
			return ExitBusy, err
		}
		return ExitRefusal, err
	}
	// Liveness is the system's property: every session re-arms the durable
	// wake to its computed next horizon. Best-effort — an unarmable host is
	// a note, never a failed drive.
	if _, err := armWakeTimer(config, session.Graph.RepoID, report.NextHorizon, session.Policy.LivenessFloor); err != nil {
		report.Notes = append(report.Notes, "liveness floor unarmed: "+err.Error())
	}
	// Progress needs no principal: at quiescence, expiring capacity converts
	// to durable evidence via delegated harvest issuance (RFC 0008 —
	// bounded by policy/gates.yaml and a per-day cadence; every issued
	// request carries its delegation_ref on the ledger).
	if note := maybeHarvest(config, session, report.Quiescence); note != "" {
		report.Notes = append(report.Notes, note)
	}
	if config.JSON {
		printJSON(config.Out, report)
	} else {
		fmt.Fprintf(config.Out, "drive session %d quiesced: %s\n", report.SessionSeq, report.Quiescence)
		for _, note := range report.Notes {
			fmt.Fprintln(config.Out, "  note:", note)
		}
	}
	if report.Blocked() {
		return ExitBlocked, nil
	}
	return ExitOK, nil
}

func runStatus(config Config) (int, error) {
	session, _, err := buildSession(config)
	if err != nil {
		return ExitRefusal, err
	}
	status, err := session.CurrentStatus()
	if err != nil {
		return ExitRefusal, err
	}
	if config.JSON {
		printJSON(config.Out, status)
		return ExitOK, nil
	}
	fmt.Fprintf(config.Out, "requests: %d  expectations: %d  acceptance queue: %d  escalations: %d\n",
		len(status.Requests), len(status.Expectations), len(status.AcceptanceQueue), len(status.Escalations))
	for _, request := range status.Requests {
		phase := request.Phase
		if request.Phase == "satisfied" && request.Level != "" {
			// Satisfaction earns its force: show the claim level, so a
			// floor-only satisfaction reads [satisfied: Asserted], never a bare
			// [satisfied] that looks Verified (D0005.C5 on the satisfaction surface).
			phase = "satisfied: " + request.Level
		}
		fmt.Fprintf(config.Out, "  RQ-%d %s -> %s [%s]\n", request.Seq, request.Subject, request.TargetID, phase)
	}
	for _, warning := range status.Warnings {
		fmt.Fprintln(config.Out, "  warning:", warning)
	}
	for _, notice := range status.Notices {
		fmt.Fprintln(config.Out, "  notice:", notice)
	}
	return ExitOK, nil
}

func runAcceptance(config Config, args []string, accept bool) (int, error) {
	positionals, rest := splitLeadingPositionals(args)
	flags := flag.NewFlagSet("acceptance", flag.ContinueOnError)
	reason := flags.String("reason", "", "verdict reason")
	if err := flags.Parse(rest); err != nil {
		return ExitUsage, err
	}
	positionals = append(positionals, flags.Args()...)
	if len(positionals) != 1 {
		return ExitUsage, errors.New("usage: striatum accept|reject <identity> [--reason text]")
	}
	if !accept && *reason == "" {
		return ExitUsage, errors.New("striatum reject: --reason is required")
	}
	graph, catalog, _, err := openGraphAndCatalog(config)
	if err != nil {
		return ExitRefusal, err
	}
	seq, err := driver.RecordAcceptance(graph, catalog, driver.AcceptanceOptions{
		Identity:  positionals[0],
		Accept:    accept,
		Reason:    *reason,
		Principal: principalIdentity(),
		Now:       config.Now,
	})
	if err != nil {
		return ExitRefusal, err
	}
	verdict := "accepted"
	if !accept {
		verdict = "rejected"
	}
	fmt.Fprintf(config.Out, "%s %s (gate_result %d)\n", verdict, positionals[0], seq)

	// Bounded transition: move the head promptly, lease permitting (P4).
	session, _, err := buildSession(config)
	if err == nil {
		session.Trigger = "principal"
		if _, err := session.Drive(); err != nil && !errors.Is(err, driver.ErrDriveLeaseBusy) {
			return ExitRefusal, err
		}
	}
	return ExitOK, nil
}

func runResolve(config Config, args []string) (int, error) {
	positionals, rest := splitLeadingPositionals(args)
	flags := flag.NewFlagSet("resolve", flag.ContinueOnError)
	disposition := flags.String("disposition", "proceed", "closed set: proceed|cancel_request|reissue|redirect|override")
	note := flags.String("note", "", "resolution note")
	if err := flags.Parse(rest); err != nil {
		return ExitUsage, err
	}
	positionals = append(positionals, flags.Args()...)
	if len(positionals) != 1 {
		return ExitUsage, errors.New("usage: striatum resolve <escalation-seq> --disposition <d>")
	}
	escalationRef, err := strconv.ParseUint(positionals[0], 10, 64)
	if err != nil {
		return ExitUsage, err
	}
	graph, _, _, err := openGraphAndCatalog(config)
	if err != nil {
		return ExitRefusal, err
	}
	seq, err := driver.RecordResolution(graph, escalationRef, *disposition, *note, principalIdentity(), config.Now)
	if err != nil {
		return ExitRefusal, err
	}
	fmt.Fprintf(config.Out, "resolution %d appended for escalation %d\n", seq, escalationRef)
	return ExitOK, nil
}

func runRevoke(config Config, args []string) (int, error) {
	positionals, rest := splitLeadingPositionals(args)
	flags := flag.NewFlagSet("revoke", flag.ContinueOnError)
	reason := flags.String("reason", "", "revocation reason (required)")
	if err := flags.Parse(rest); err != nil {
		return ExitUsage, err
	}
	positionals = append(positionals, flags.Args()...)
	if len(positionals) != 1 || *reason == "" {
		return ExitUsage, errors.New("usage: striatum revoke <decision-id> --reason text")
	}
	graph, _, _, err := openGraphAndCatalog(config)
	if err != nil {
		return ExitRefusal, err
	}
	seq, err := driver.RecordRevocation(graph, positionals[0], *reason, principalIdentity(), config.Now)
	if err != nil {
		return ExitRefusal, err
	}
	fmt.Fprintf(config.Out, "revocation %d appended for %s\n", seq, positionals[0])
	return ExitOK, nil
}

func runReconcile(config Config, args []string) (int, error) {
	flags := flag.NewFlagSet("reconcile", flag.ContinueOnError)
	verify := flags.Bool("verify", false, "verify derived stores by shadow refold")
	if err := flags.Parse(args); err != nil {
		return ExitUsage, err
	}
	graph, _, _, err := openGraphAndCatalog(config)
	if err != nil {
		return ExitRefusal, err
	}
	report, err := graph.Reconcile(store.ReconcileOptions{Verify: *verify})
	if err != nil {
		return ExitRefusal, err
	}
	parked := false
	for _, finding := range report.Findings {
		fmt.Fprintf(config.Out, "finding %s: %s\n", finding.Code, finding.Detail)
		if finding.Code == store.FindingSchemaNewerThanReader || finding.Code == store.FindingBodyMissing {
			parked = true
		}
	}
	fmt.Fprintf(config.Out, "reconciled %d frames; derived digest %s\n", report.FrameCount, report.DerivedDigest)
	if parked {
		// Park, never crash-loop; do not retry without a human.
		return ExitParked, nil
	}
	return ExitOK, nil
}

func runLedger(config Config, args []string) (int, error) {
	if len(args) == 0 || (args[0] != "cat" && args[0] != "seal") {
		return ExitUsage, errors.New("usage: striatum ledger <cat|seal>")
	}
	graph, _, _, err := openGraphAndCatalog(config)
	if err != nil {
		return ExitRefusal, err
	}
	if args[0] == "seal" {
		result, err := graph.SealActiveSegment(store.SealOptions{})
		if err != nil {
			return ExitRefusal, err
		}
		fmt.Fprintf(config.Out, "sealed %s; new active segment %s\n", filepath.Base(result.SealedPath), filepath.Base(result.NewActivePath))
		return ExitOK, nil
	}
	all, err := graph.Records()
	if err != nil {
		return ExitRefusal, err
	}
	for _, record := range all {
		line := map[string]any{
			"seq":              record.Seq,
			"type":             record.Type,
			"schema_version":   record.SchemaVersion,
			"written_at":       record.WrittenAt,
			"actor":            map[string]string{"component": record.Actor.Component, "instance": record.Actor.Instance},
			"causes":           record.Causes,
			"prev_record_hash": record.PrevRecordHash,
			"payload":          record.Payload,
		}
		raw, err := json.Marshal(line)
		if err != nil {
			return ExitRefusal, err
		}
		fmt.Fprintln(config.Out, string(raw))
	}
	return ExitOK, nil
}

// --- construction helpers ---

// resolvedChecksPath resolves the check-registry path relative to the target
// repository. The registry is per-repo policy (RFC 0010) resident in the
// repository's own tree, so a relative -checks names a file under -repo, not the
// process working directory (checks-resolve-to-repo@1). An absolute -checks is
// an explicit override and is honored as given; an empty -checks stays empty (a
// missing registry is a legal state). On the self-drive, where -repo defaults to
// the working directory, the relative path resolves to the same file as before.
func (c Config) resolvedChecksPath() string {
	if c.ChecksPath == "" || filepath.IsAbs(c.ChecksPath) {
		return c.ChecksPath
	}
	repo := c.Repo
	if repo == "" {
		repo = "."
	}
	return filepath.Join(repo, c.ChecksPath)
}

// resolveEffectiveOverlays computes the catalog-overlay list one invocation
// actually uses (fleet-catalog-resolution@2). Explicit -catalog-overlay flags
// override: the effective list is exactly the flags in invocation order, and
// registration is never consulted. Otherwise a registered repository's
// declared resolution.instance_catalog_overlay derives a single-element list;
// no declaration is the standing base-only load, byte-identical to the
// pre-declaration drive. A declaration about to be used must name an
// absolute, clean path to an existing readable directory — a violation, like
// a registry lookup error, refuses the invocation before any catalog load as
// a registration-resolution failure near its configuration cause, never a
// degraded catalog. Every returned path is absolute: the effective list is
// computed once per invocation and re-emitted verbatim to the post-commit
// wake, which must resolve the same merged catalog without re-reading
// registration.
func resolveEffectiveOverlays(config Config, repoID string) (stringList, error) {
	if len(config.Overlays) > 0 {
		effective := make(stringList, 0, len(config.Overlays))
		for _, overlay := range config.Overlays {
			abs, err := filepath.Abs(overlay)
			if err != nil {
				return nil, err
			}
			effective = append(effective, abs)
		}
		return effective, nil
	}
	declared, err := store.InstanceCatalogOverlay(config.DataHome, repoID)
	if err != nil {
		return nil, fmt.Errorf("striatum: registration resolution for repo %s refused: %w", repoID, err)
	}
	if declared == "" {
		return nil, nil
	}
	if !filepath.IsAbs(declared) {
		return nil, fmt.Errorf("striatum: registration resolution for repo %s refused: declared instance_catalog_overlay %q is not an absolute path", repoID, declared)
	}
	if filepath.Clean(declared) != declared {
		return nil, fmt.Errorf("striatum: registration resolution for repo %s refused: declared instance_catalog_overlay %q is not a clean path", repoID, declared)
	}
	info, err := os.Stat(declared)
	if err != nil {
		return nil, fmt.Errorf("striatum: registration resolution for repo %s refused: declared instance_catalog_overlay %q is not usable: %v", repoID, declared, err)
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("striatum: registration resolution for repo %s refused: declared instance_catalog_overlay %q is not a directory", repoID, declared)
	}
	dir, err := os.Open(declared)
	if err != nil {
		return nil, fmt.Errorf("striatum: registration resolution for repo %s refused: declared instance_catalog_overlay %q is not readable: %v", repoID, declared, err)
	}
	dir.Close()
	// A valid root without target-states/ flows through unchanged: it is an
	// empty overlay under the v1 loader rule, not a refusal.
	return stringList{declared}, nil
}

// resolveEffectiveChecks computes the check-registry path one invocation
// actually gates on (checks-resolve-to-repo@2). Exactly one source decides,
// blend-free. An explicit -checks — any value, including the default string
// and the empty string — is honored under the untouched @1 resolution rule,
// and registration is never consulted. Otherwise a registered repository's
// declared resolution.check_registry derives the path; declaring nothing is
// the @1 default behavior byte-identically (the default path resolves
// against -repo, a missing file stays the legal unmet state). A declaration
// about to be used must name an absolute, clean path to an existing
// readable regular file — a violation, like a registry lookup error,
// refuses the invocation before any check-registry load (this function
// never loads one) as a registration-resolution failure near its
// configuration cause, never a degraded gate; a declared-but-unusable path
// never falls back to the default. Resolution runs once per invocation, at
// the session-construction seam, and the wake re-emits the effective
// decision verbatim — including the empty decision — so a wake never
// re-reads registration.
func resolveEffectiveChecks(config Config, repoID string) (string, error) {
	if config.ChecksExplicit {
		return config.resolvedChecksPath(), nil
	}
	declared, ok, err := store.CheckRegistry(config.DataHome, repoID)
	if err != nil {
		return "", fmt.Errorf("striatum: registration resolution for repo %s refused: %w", repoID, err)
	}
	if !ok {
		return config.resolvedChecksPath(), nil
	}
	if declared == "" {
		return "", fmt.Errorf("striatum: registration resolution for repo %s refused: declared check_registry %q is empty", repoID, declared)
	}
	if !filepath.IsAbs(declared) {
		return "", fmt.Errorf("striatum: registration resolution for repo %s refused: declared check_registry %q is not an absolute path", repoID, declared)
	}
	if filepath.Clean(declared) != declared {
		return "", fmt.Errorf("striatum: registration resolution for repo %s refused: declared check_registry %q is not a clean path", repoID, declared)
	}
	info, err := os.Stat(declared)
	if err != nil {
		return "", fmt.Errorf("striatum: registration resolution for repo %s refused: declared check_registry %q is not usable: %v", repoID, declared, err)
	}
	if !info.Mode().IsRegular() {
		return "", fmt.Errorf("striatum: registration resolution for repo %s refused: declared check_registry %q is not a regular file", repoID, declared)
	}
	file, err := os.Open(declared)
	if err != nil {
		return "", fmt.Errorf("striatum: registration resolution for repo %s refused: declared check_registry %q is not readable: %v", repoID, declared, err)
	}
	file.Close()
	return declared, nil
}

// openGraphAndCatalog opens the graph, resolves the effective overlay list at
// the session-construction seam — after OpenGraph names the repository,
// before LoadCatalog composes the vocabulary — and loads the merged catalog.
// The returned Config carries the resolved list as its Overlays: callers must
// thread it, not the raw flag list, so the session, its adapters' wake argv,
// and the armed wake timer all see one resolution per invocation.
func openGraphAndCatalog(config Config) (*store.Graph, driver.Catalog, Config, error) {
	graph, _, err := store.OpenGraph(store.OpenOptions{DataHome: config.DataHome, RepoRoot: config.Repo})
	if err != nil {
		return nil, driver.Catalog{}, config, err
	}
	overlays, err := resolveEffectiveOverlays(config, graph.RepoID)
	if err != nil {
		return nil, driver.Catalog{}, config, err
	}
	config.Overlays = overlays
	catalog, err := driver.LoadCatalog(config.CatalogDir, config.Overlays...)
	if err != nil {
		return nil, driver.Catalog{}, config, err
	}
	return graph, catalog, config, nil
}

func buildSession(config Config) (*driver.Session, Config, error) {
	graph, catalog, config, err := openGraphAndCatalog(config)
	if err != nil {
		return nil, config, err
	}
	// The effective check registry resolves exactly once, at this seam —
	// after the graph names the repository, before the adapters loop
	// snapshots wake argv and before the registry load below
	// (checks-resolve-to-repo@2). The decision rides the returned Config as
	// its ChecksPath: callers and the load site consume it verbatim, never
	// through resolvedChecksPath again (the effective value is already
	// @1-resolved on the flag and default branches; re-resolving would join
	// -repo a second time).
	effectiveChecks, err := resolveEffectiveChecks(config, graph.RepoID)
	if err != nil {
		return nil, config, err
	}
	config.ChecksPath = effectiveChecks
	kinds, err := store.LoadArtifactKinds(filepath.Join(config.CatalogDir, "artifact-kinds"))
	if err != nil {
		return nil, config, err
	}
	policy, err := driver.LoadPolicy(config.PolicyPath)
	if err != nil {
		return nil, config, err
	}
	declarations, _, err := driver.LoadBackendDeclarations(config.BackendsDir)
	if err != nil {
		return nil, config, err
	}
	spool := backend.Spool{Root: filepath.Join(graph.DataRoot, "exchange", graph.RepoID)}
	if err := spool.EnsureLayout(); err != nil {
		return nil, config, err
	}
	runtime := config.Runtime
	if runtime == nil {
		runtime = local.DefaultRuntime()
	}
	// Per-backend runtime seal keys (RFC 0012): minted at first use, held
	// outside every repository and outside the spool. The lane-credential
	// (rung-2 isolation) directory sits beside it, provisioned out of band by
	// a privileged deployment; absent keeps every lane at the single-uid
	// posture (D0012.C5).
	keysDir := filepath.Join(graph.DataRoot, "keys")
	isolationDir := filepath.Join(graph.DataRoot, llm.IsolationDirName)
	sealKeys := map[string][]byte{}
	localKey, err := backend.LoadOrMintSealKey(keysDir, local.BackendID)
	if err != nil {
		return nil, config, err
	}
	sealKeys[local.BackendID] = localKey
	adapters := map[string]driver.Adapter{
		local.BackendID: &local.Adapter{Spool: spool, Runtime: runtime, StoreRoot: graph.GraphDir, SealKey: localKey},
	}
	for _, declaration := range declarations {
		if declaration.BackendID == local.BackendID {
			continue
		}
		adapterConfig, err := llm.LoadConfig(filepath.Join(config.BackendsDir, declaration.BackendID, "backend.yaml"))
		if err != nil {
			// A declaration without an adapter block schedules but cannot
			// dispatch; the session reports the missing adapter as a note.
			continue
		}
		key, err := backend.LoadOrMintSealKey(keysDir, declaration.BackendID)
		if err != nil {
			return nil, config, err
		}
		sealKeys[declaration.BackendID] = key
		surface := adapterConfig.SurfaceCommand
		if len(surface) == 0 {
			surface = []string{"striatum-backend-" + declaration.BackendID}
		}
		adapters[declaration.BackendID] = &llm.Adapter{
			Config: adapterConfig, Spool: spool, StoreRoot: graph.GraphDir, SealKey: key,
			Surface:      surface,
			Declaration:  filepath.Join(config.BackendsDir, declaration.BackendID, "backend.yaml"),
			KeysDir:      keysDir,
			IsolationDir: isolationDir,
			WakeCmd:      wakeCommand(config),
		}
	}
	// A missing check registry is a legal state: verified targets stay unmet.
	// The registry is per-repo policy (RFC 0010), resident in the target
	// repository's tree. The path here is the invocation's effective checks
	// decision — explicit flag, registration-derived, or the @1 default —
	// resolved once at the seam above (checks-resolve-to-repo@2) and
	// consumed verbatim. The stat tolerance applies in practice only to
	// flag/default decisions: a declared path already passed
	// existing-regular-readable validation at resolution, so it cannot
	// silently take this branch.
	var checkWorld *driver.CheckWorld
	if checksPath := config.ChecksPath; checksPath != "" {
		if _, err := os.Stat(checksPath); err == nil {
			checkWorld, err = driver.LoadCheckWorld(checksPath)
			if err != nil {
				return nil, config, err
			}
		}
	}
	return &driver.Session{
		Graph:    graph,
		Spool:    spool,
		Adapters: adapters,
		Catalog:  catalog,
		Policy:   policy,
		Kinds:    kinds,
		Backends: declarations,
		Checks:   checkWorld,
		SealKeys: sealKeys,
		Now:      config.Now,
	}, config, nil
}

// wakeCommand derives the post-commit wake argv from this session's own
// resolved configuration: self-sufficient absolute paths, since the wake
// fires from a detached supervisor with an unrelated working directory.
// The supervisor appends "-trigger adapter_wake" itself (D0013.C7). Empty
// values are skipped, with one deliberate exception: the -checks pair is
// emitted unconditionally, because an omitted -checks on re-entry would
// silently flip an explicit-empty override into registration-derived
// resolution (checks-resolve-to-repo@2).
func wakeCommand(config Config) []string {
	self, err := os.Executable()
	if err != nil {
		return nil // no wake; the standing timer remains the floor
	}
	argv := []string{self}
	for _, pair := range [][2]string{
		{"-repo", config.Repo},
		{"-data-home", config.DataHome},
		{"-catalog", config.CatalogDir},
		{"-backends", config.BackendsDir},
		{"-policy", config.PolicyPath},
	} {
		if pair[1] == "" {
			continue
		}
		abs, err := filepath.Abs(pair[1])
		if err != nil {
			return nil
		}
		argv = append(argv, pair[0], abs)
	}
	// The checks decision is pinned even when empty: the resolved absolute
	// path when non-empty, an explicit empty -checks when the effective
	// decision is "no registry" — never an omitted flag. Callers pass
	// resolved snapshots by contract, so ChecksPath is the invocation's
	// effective decision and re-entry takes the explicit-flag branch by
	// construction, never re-reading registration. Absolutization is
	// skipped for the empty value (filepath.Abs("") would fabricate a
	// cwd-relative path).
	checks := config.ChecksPath
	if checks != "" {
		abs, err := filepath.Abs(checks)
		if err != nil {
			return nil
		}
		checks = abs
	}
	argv = append(argv, "-checks", checks)
	// Overlays are repeatable and order-significant; preserve each so the
	// detached wake resolves the same merged catalog this session did. The
	// list here is the session's resolved effective list — explicit flags or
	// the registration-derived overlay — re-emitted as explicit argv pairs,
	// so the wake's re-entry takes the flags-override branch by construction
	// and never re-reads registration (fleet-catalog-resolution@2).
	for _, overlay := range config.Overlays {
		if overlay == "" {
			continue
		}
		abs, err := filepath.Abs(overlay)
		if err != nil {
			return nil
		}
		argv = append(argv, "-catalog-overlay", abs)
	}
	return append(argv, "drive")
}

func principalIdentity() string {
	if user := os.Getenv("USER"); user != "" {
		return user
	}
	return "principal"
}

func defaultDataHome() string {
	if xdg := os.Getenv("XDG_DATA_HOME"); xdg != "" {
		return xdg
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return ".striatum-data"
	}
	return filepath.Join(home, ".local", "share")
}

func readRepoID(repoRoot string) (string, error) {
	raw, err := os.ReadFile(filepath.Join(repoRoot, ".striatum", "graph.json"))
	if err != nil {
		return "", err
	}
	var identity struct {
		RepoID string `json:"repo_id"`
	}
	if err := json.Unmarshal(raw, &identity); err != nil {
		return "", err
	}
	return identity.RepoID, nil
}

func discoverRootCommit(repoRoot string) (string, error) {
	cmd := exec.Command("git", "-C", repoRoot, "rev-list", "--max-parents=0", "HEAD")
	out, err := cmd.Output()
	if err != nil {
		return "", err
	}
	lines := strings.Fields(strings.TrimSpace(string(out)))
	if len(lines) == 0 {
		return "", errors.New("no root commit found")
	}
	return lines[len(lines)-1], nil
}

func newUUIDv7(now time.Time) (string, error) {
	var b [16]byte
	if _, err := rand.Read(b[:]); err != nil {
		return "", err
	}
	ms := uint64(now.UnixMilli())
	b[0] = byte(ms >> 40)
	b[1] = byte(ms >> 32)
	b[2] = byte(ms >> 24)
	b[3] = byte(ms >> 16)
	b[4] = byte(ms >> 8)
	b[5] = byte(ms)
	b[6] = (b[6] & 0x0f) | 0x70
	b[8] = (b[8] & 0x3f) | 0x80
	hexed := hex.EncodeToString(b[:])
	return hexed[0:8] + "-" + hexed[8:12] + "-" + hexed[12:16] + "-" + hexed[16:20] + "-" + hexed[20:32], nil
}

// splitLeadingPositionals lets verbs accept `striatum verb <arg> --flag v`.
func splitLeadingPositionals(args []string) ([]string, []string) {
	var positionals []string
	for len(args) > 0 && !strings.HasPrefix(args[0], "-") {
		positionals = append(positionals, args[0])
		args = args[1:]
	}
	return positionals, args
}

func printJSON(out *os.File, value any) {
	raw, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		fmt.Fprintln(out, `{"error":"marshal failure"}`)
		return
	}
	fmt.Fprintln(out, string(raw))
}
