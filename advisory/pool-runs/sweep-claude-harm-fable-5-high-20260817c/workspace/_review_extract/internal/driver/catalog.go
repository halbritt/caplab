// Package driver implements the compiler driver: a deterministic program
// that plans, gates, admits, invalidates, and escalates. It produces no
// artifacts; it appends ledger records and invokes the store, scheduler,
// and backend seam (RFC 0006).
package driver

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/halbritt/striatum-next/internal/scheduler"
	targetmodel "github.com/halbritt/striatum-next/internal/target"
)

// PassSpec is the driver-facing slice of one cataloged pass contract.
// Consumes carries the required inputs the planner ensures; optional
// consumes (diagnostic inputs, later-stage pins) are pinned at dispatch
// when a fresh head exists but are never produced on the pass's account.
type PassSpec struct {
	ID               string
	Class            string
	ContractVersion  int
	ImplVersion      int
	Determinism      string
	Effects          string
	LatencyClass     string
	Produces         []string
	Consumes         []string
	ConsumesOptional []string
	ConsumesElement  map[string]string // kind -> element grain (e.g. work-graph -> work-packet)
	// ConsumesClaimMin is the declared minimum claim level a consumed kind's
	// head must hold before this pass may run against it (kind -> level).
	// Declared since RFC 0004 and read since 2026-07-23; before that it was
	// decoration, and the generic produce path sealed integration dispatches
	// against unverified Change Sets that could only refuse.
	ConsumesClaimMin     map[string]string
	Gates                []string
	EnvironmentDecisions []string
	EnvironmentPolicies  []string
}

// GateSpec is one cataloged quality gate.
type GateSpec struct {
	ID               string
	Class            string
	PredicateVersion int
}

// KindSpec is one cataloged artifact kind with its gate wiring.
type KindSpec struct {
	ID    string
	Role  string
	Level string
	Gates []string
}

// Conjunct is one machine-evaluable target-state conjunct (v0 vocabulary).
type Conjunct struct {
	Kind         string
	ArtifactKind string
}

// TargetSpec is one cataloged target state.
type TargetSpec struct {
	ID               string
	PredicateVersion int
	Conjuncts        []Conjunct
	// Projection is the complete immutable target semantics request issuance
	// pins. DeclarationBody is the exact catalog file stored before the v2
	// compilation_request is appended.
	Projection      targetmodel.Projection
	DeclarationBody []byte
}

// Catalog is the loaded catalog surface the driver plans over.
type Catalog struct {
	Passes     map[string]PassSpec
	Gates      map[string]GateSpec
	Kinds      map[string]KindSpec
	Targets    map[string]TargetSpec
	PassBodies map[string][]byte
	GateBodies map[string][]byte
	KindBodies map[string][]byte
}

// ProducerOfForSubject resolves the producing pass for a kind, honoring
// per-subject production. RFC 0015: the fleet-knowledge subject's product-artifact
// is produced by the knowledge-promotion pass (distilling admitted cross-fleet
// evidence), not by integration (which links change-sets). The override is
// strictly subject-scoped — every other subject's product-artifact still
// resolves through the global ProducerOf — so integration semantics for real
// product lineage are untouched. The general per-repository declared-producer
// mechanism is the named refinement; this is the minimal hook that keeps the
// override to the knowledge subject.
func (c Catalog) ProducerOfForSubject(kind, subject string) (PassSpec, bool) {
	if kind == "product-artifact" && strings.HasPrefix(subject, "fleet-knowledge/") {
		if producer, ok := c.Passes["knowledge-promotion"]; ok {
			return producer, true
		}
	}
	return c.ProducerOf(kind)
}

// ProducerOf returns the pass producing an artifact kind.
func (c Catalog) ProducerOf(kind string) (PassSpec, bool) {
	ids := make([]string, 0, len(c.Passes))
	for id := range c.Passes {
		ids = append(ids, id)
	}
	// Stable iteration: catalog maps must not introduce nondeterminism.
	sortStrings(ids)
	for _, id := range ids {
		for _, produced := range c.Passes[id].Produces {
			if produced == kind {
				return c.Passes[id], true
			}
		}
	}
	return PassSpec{}, false
}

// LoadCatalog reads the pass, gate, kind, and target-state catalogs from a base
// root, then layers any overlay roots' target-states on top.
//
// The base root is the shipped compiler catalog: it carries the structural
// vocabulary (passes, gates, artifact-kinds, IRs, pipelines) and the generic
// lifecycle and standing-capability target-states. Each overlay root contributes
// target-states only, tolerating an absent target-states subdirectory; on a
// target-state id collision the later overlay wins, deterministically, in the
// order given. A fleet repository resolves the product catalog (base) plus its
// instance's foreign target-states (overlay) as one coherent catalog with
// identical semantics; a load with no overlays is byte-identical to loading the
// base root alone (fleet-catalog-resolution@1, D0011.C1: the base is the fleet's
// pinned environment). The merged result is one catalog — overlaying changes the
// loader's on-disk arity, never the vocabulary's meaning (RFC 0001/0005).
func LoadCatalog(root string, overlays ...string) (Catalog, error) {
	catalog := Catalog{
		Passes:     map[string]PassSpec{},
		Gates:      map[string]GateSpec{},
		Kinds:      map[string]KindSpec{},
		Targets:    map[string]TargetSpec{},
		PassBodies: map[string][]byte{},
		GateBodies: map[string][]byte{},
		KindBodies: map[string][]byte{},
	}
	if err := eachYAML(filepath.Join(root, "passes"), func(doc yamlDoc) error {
		required, optional := doc.sectionKindsSplit("consumes")
		pass := PassSpec{
			ID:                   doc.value("id"),
			Class:                doc.value("class"),
			ContractVersion:      doc.intValue("contract_version", 1),
			ImplVersion:          doc.intValue("impl_version", 1),
			Determinism:          doc.value("determinism"),
			Effects:              doc.value("effects"),
			Produces:             doc.sectionKinds("produces"),
			Consumes:             required,
			ConsumesOptional:     optional,
			ConsumesElement:      doc.sectionKindElements("consumes"),
			ConsumesClaimMin:     doc.sectionKindFields("consumes", "claim_min"),
			Gates:                doc.inlineList("gates"),
			EnvironmentDecisions: doc.nestedInlineList("environment", "decisions"),
			EnvironmentPolicies:  doc.nestedInlineList("environment", "policies"),
			LatencyClass:         doc.nestedValue("resources", "latency_class"),
		}
		if pass.ID == "" {
			return fmt.Errorf("driver: pass file missing id")
		}
		catalog.Passes[pass.ID] = pass
		catalog.PassBodies[pass.ID] = append([]byte(nil), doc.raw...)
		return nil
	}); err != nil {
		return catalog, err
	}
	if err := eachYAML(filepath.Join(root, "gates"), func(doc yamlDoc) error {
		gate := GateSpec{ID: doc.value("id"), Class: doc.value("class"), PredicateVersion: doc.intValue("predicate_version", 1)}
		if gate.ID == "" || gate.Class == "" {
			return fmt.Errorf("driver: gate file missing id or class")
		}
		catalog.Gates[gate.ID] = gate
		catalog.GateBodies[gate.ID] = append([]byte(nil), doc.raw...)
		return nil
	}); err != nil {
		return catalog, err
	}
	if err := eachYAML(filepath.Join(root, "artifact-kinds"), func(doc yamlDoc) error {
		kind := KindSpec{
			ID:    doc.value("id"),
			Role:  doc.value("role"),
			Level: doc.value("level"),
			Gates: doc.blockOrInlineList("gates"),
		}
		if kind.ID == "" {
			return fmt.Errorf("driver: artifact-kind file missing id")
		}
		catalog.Kinds[kind.ID] = kind
		catalog.KindBodies[kind.ID] = append([]byte(nil), doc.raw...)
		return nil
	}); err != nil {
		return catalog, err
	}
	if err := catalog.loadTargetStates(filepath.Join(root, "target-states"), false); err != nil {
		return catalog, err
	}
	// Overlay roots contribute target-states only, tolerating an absent
	// target-states subdirectory; later overlays win on id collision.
	for _, overlay := range overlays {
		if err := catalog.loadTargetStates(filepath.Join(overlay, "target-states"), true); err != nil {
			return catalog, err
		}
	}
	return catalog, nil
}

// loadTargetStates reads every target-state file in dir into the catalog. When
// tolerateMissing is set, an absent dir is treated as an empty overlay rather
// than an error — the base root always carries a target-states subdirectory, an
// overlay root may not.
func (c *Catalog) loadTargetStates(dir string, tolerateMissing bool) error {
	if tolerateMissing {
		if _, err := os.Stat(dir); errors.Is(err, os.ErrNotExist) {
			return nil
		}
	}
	return eachYAML(dir, func(doc yamlDoc) error {
		// A repository may keep generated adjuncts beside its declarations
		// (vitae's kind: target-state-baseline pin file). Overlays and the
		// base alike contribute target-states only, so a file explicitly
		// declaring a different kind is not a declaration and is skipped;
		// anything else still parses strictly and refuses loudly.
		if kind := doc.value("kind"); kind != "" && kind != "target-state" {
			return nil
		}
		declaration, err := targetmodel.ParseDeclaration(doc.raw)
		if err != nil {
			return err
		}
		spec := TargetSpec{
			ID:               declaration.Projection.StateID,
			PredicateVersion: declaration.Projection.PredicateVersion,
			Projection:       declaration.Projection,
			DeclarationBody:  declaration.Body,
		}
		for _, planned := range declaration.Projection.PlanningConjuncts {
			conjunct := Conjunct{Kind: planned.Kind, ArtifactKind: planned.ArtifactKind}
			switch conjunct.Kind {
			case "accepted_head", "evidence_admitted", "verified_dual_signal", "integrated_head", "built", "integrated_batch", "review_admitted":
			default:
				return fmt.Errorf("driver: target %s conjunct kind %q outside the conjunct vocabulary", spec.ID, conjunct.Kind)
			}
			if conjunct.ArtifactKind == "" {
				return fmt.Errorf("driver: target %s conjunct artifact kind is empty", spec.ID)
			}
			spec.Conjuncts = append(spec.Conjuncts, conjunct)
		}
		c.Targets[spec.ID] = spec
		return nil
	})
}

// LoadBackendDeclaration reads the scheduler-facing slice of one backend
// declaration; the declaration hash pins the full file content.
func LoadBackendDeclaration(path string) (scheduler.Declaration, error) {
	declaration, _, err := loadBackendDeclaration(path)
	return declaration, err
}

func loadBackendDeclaration(path string) (scheduler.Declaration, string, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return scheduler.Declaration{}, "", err
	}
	return parseBackendDeclaration(raw, path)
}

// parseBackendDeclaration resolves the complete scheduler-facing projection
// from one exact declaration body. File loading and lock-held Graph-object
// validation share this parser so an in-memory placement fact cannot diverge
// from the declaration_hash that transitively binds it.
func parseBackendDeclaration(raw []byte, source string) (scheduler.Declaration, string, error) {
	doc := yamlDoc{raw: raw, lines: strings.Split(string(raw), "\n")}
	sum := sha256.Sum256(raw)
	supportedPasses := doc.nestedInlineList("capabilities", "supported_pass_types")
	qualityClasses, err := scheduler.BackendQualityClasses(raw, supportedPasses)
	if err != nil {
		return scheduler.Declaration{}, "", fmt.Errorf("driver: %s quality.classes: %w", source, err)
	}
	status := doc.value("status")
	declaration := scheduler.Declaration{
		BackendID:       doc.value("id"),
		DeclarationHash: hex.EncodeToString(sum[:]),
		SupportedPasses: supportedPasses,
		ForbiddenPasses: doc.nestedInlineList("capabilities", "forbidden_pass_types"),
		AliasingClass:   doc.nestedValue("aliasing", "aliasing_class"),
		QualityClasses:  qualityClasses,
		// capabilities.effects is a declared capability fact; placement's
		// effect filter reads it from the declaration rather than inferring an
		// effect class from the adapter command. Parsed here so the in-memory
		// fact and the declaration_hash that binds it come from the same body.
		DeclaredEffects: doc.nestedInlineList("capabilities", "effects"),
		Rank:            100, // unranked binds last
	}
	for _, hint := range doc.inlineList("scheduler_hints") {
		if value, ok := strings.CutPrefix(hint, "rank="); ok {
			if rank, err := strconv.Atoi(strings.TrimSpace(value)); err == nil {
				declaration.Rank = rank
			}
		}
	}
	// capabilities.concurrency inline map: { max_lanes: N }. Absent or
	// unparseable stays 0 (unbounded) — recorded encoding choice.
	if concurrency := doc.nestedValue("capabilities", "concurrency"); concurrency != "" {
		trimmed := strings.Trim(concurrency, "{} ")
		if value, ok := strings.CutPrefix(trimmed, "max_lanes:"); ok {
			if lanes, err := strconv.Atoi(strings.TrimSpace(value)); err == nil && lanes > 0 {
				declaration.MaxLanes = lanes
			}
		}
	}
	if declaration.BackendID == "" {
		return declaration, "", fmt.Errorf("driver: %s missing backend id", source)
	}
	if status == "accepted" && declaration.AliasingClass == "" {
		return declaration, "", fmt.Errorf("driver: %s accepted backend %s has empty aliasing_class", source, declaration.BackendID)
	}
	return declaration, status, nil
}

// LoadBackendDeclarations reads every backends/<id>/backend.yaml. Only
// declarations with status `accepted` join the scheduler's world; the rest
// are reported as notices — a placeholder describes intent, not capability.
func LoadBackendDeclarations(dir string) ([]scheduler.Declaration, []string, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil, nil, err
	}
	var declarations []scheduler.Declaration
	var notices []string
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		path := filepath.Join(dir, entry.Name(), "backend.yaml")
		if _, err := os.Stat(path); err != nil {
			continue
		}
		declaration, status, err := loadBackendDeclaration(path)
		if err != nil {
			return nil, nil, err
		}
		if status != "accepted" {
			notices = append(notices, fmt.Sprintf("backend %s not scheduled (status %q)", declaration.BackendID, status))
			continue
		}
		declarations = append(declarations, declaration)
	}
	if len(declarations) == 0 {
		return nil, notices, fmt.Errorf("driver: no accepted backend declarations under %s", dir)
	}
	return declarations, notices, nil
}

// LoadSchedulerPolicyPin reads the canonical scheduler policy body. The full
// body is returned for persistence in the Graph Store; the pin is the only
// scheduler-policy identity carried into an evaluation.
func LoadSchedulerPolicyPin(path string) (scheduler.SchedulerPolicyPin, []byte, error) {
	pin, _, raw, err := LoadSchedulerPolicy(path)
	return pin, raw, err
}

// LoadSchedulerPolicy reads and validates the canonical scheduler policy once,
// returning both its durable pin and its pass-scoped backend-preference
// projection from that exact body.
func LoadSchedulerPolicy(path string) (scheduler.SchedulerPolicyPin, map[string][]string, []byte, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return scheduler.SchedulerPolicyPin{}, nil, nil, err
	}
	pin, preferences, err := SchedulerPolicyFromBody(path, raw)
	if err != nil {
		return scheduler.SchedulerPolicyPin{}, nil, nil, err
	}
	return pin, preferences, raw, nil
}

// SchedulerPolicyFromBody validates one EXACT scheduler policy body and derives
// its durable pin and pass-scoped backend-preference projection from those bytes
// and nothing else. The path is carried for diagnostics only; this function
// never opens it.
//
// The separation is load-bearing rather than cosmetic. A caller that has already
// read the body — the placement-policy load seam does, because it parses the
// placement surface from those same bytes — must be able to derive the pin from
// the body it actually parsed. Re-opening the path to derive the pin would leave
// a window in which the file changes between the two reads, and the caller would
// then pair one body's declarations with another body's content hash: the
// content-addressed pin would name bytes that never produced those declarations
// (D0005.C2), and a decision trace would record an objective its own pinned
// policy body does not declare.
func SchedulerPolicyFromBody(path string, raw []byte) (scheduler.SchedulerPolicyPin, map[string][]string, error) {
	doc := yamlDoc{raw: raw, lines: strings.Split(string(raw), "\n")}
	version, err := strconv.Atoi(doc.value("policy_version"))
	if err != nil || version <= 0 {
		return scheduler.SchedulerPolicyPin{}, nil, fmt.Errorf("driver: %s has invalid scheduler policy_version", path)
	}
	preferences, err := ParseSchedulerBackendPreferences(raw)
	if err != nil {
		return scheduler.SchedulerPolicyPin{}, nil, fmt.Errorf("driver: %s: %w", path, err)
	}
	sum := sha256.Sum256(raw)
	return scheduler.SchedulerPolicyPin{Version: version, BodyHash: hex.EncodeToString(sum[:])}, preferences, nil
}

// ParseSchedulerBackendPreferences resolves pass-scoped backend ordering from
// the accepted placement_rules surface. Rules retain their declared
// first-full-match order: only the first rule matching a pass contributes a
// backend preference, and a rule without prefer.backends intentionally leaves
// that pass on the declaration-rank fallback.
//
// This projection is keyed by pass alone, so a rule that further RESTRICTS its
// match — today, `gating: true` — is not representable in it and is skipped
// entirely rather than consuming its pass's first-full-match slot. Skipping is
// the faithful reading, not a convenience: a restricted rule does not match an
// unrestricted run, so it is not that run's first full match, and letting it
// claim the slot would drop the general rule's preference for every run the
// restricted rule never applied to.
func ParseSchedulerBackendPreferences(raw []byte) (map[string][]string, error) {
	doc := yamlDoc{raw: raw, lines: strings.Split(string(raw), "\n")}
	preferences := map[string][]string{}
	seenPass := map[string]bool{}
	currentPass := ""
	currentRestricted := false
	var currentBackends []string
	inPrefer := false
	flush := func() error {
		if currentPass == "" || currentRestricted || seenPass[currentPass] {
			return nil
		}
		seenPass[currentPass] = true
		if len(currentBackends) == 0 {
			return nil
		}
		seenBackend := map[string]bool{}
		for _, backendID := range currentBackends {
			if seenBackend[backendID] {
				return fmt.Errorf("driver: scheduler preference for pass %s contains duplicate backend %s", currentPass, backendID)
			}
			seenBackend[backendID] = true
		}
		preferences[currentPass] = append([]string(nil), currentBackends...)
		return nil
	}

	for _, line := range doc.section("placement_rules") {
		trimmed := strings.TrimSpace(stripComment(line))
		if strings.HasPrefix(trimmed, "- id:") {
			if err := flush(); err != nil {
				return nil, err
			}
			currentPass = ""
			currentRestricted = false
			currentBackends = nil
			inPrefer = false
			continue
		}
		if value, ok := strings.CutPrefix(trimmed, "match:"); ok {
			currentPass = inlineMapScalar(value, "pass")
			currentRestricted = inlineMapScalar(value, "gating") != ""
			continue
		}
		if value, ok := strings.CutPrefix(trimmed, "prefer:"); ok {
			inPrefer = true
			if backends, found := inlineMapList(value, "backends"); found {
				currentBackends = backends
				inPrefer = false
			}
			continue
		}
		if inPrefer {
			if value, ok := strings.CutPrefix(trimmed, "backends:"); ok {
				currentBackends = parseInlineList(value)
				inPrefer = false
			}
		}
	}
	if err := flush(); err != nil {
		return nil, err
	}
	return preferences, nil
}

func inlineMapScalar(raw, key string) string {
	raw = strings.Trim(strings.TrimSpace(raw), "{}")
	for _, field := range strings.Split(raw, ",") {
		name, value, ok := strings.Cut(field, ":")
		if ok && strings.TrimSpace(name) == key {
			return cleanScalar(value)
		}
	}
	return ""
}

func inlineMapList(raw, key string) ([]string, bool) {
	marker := key + ":"
	start := strings.Index(raw, marker)
	if start < 0 {
		return nil, false
	}
	value := raw[start+len(marker):]
	left := strings.Index(value, "[")
	right := strings.Index(value, "]")
	if left < 0 || right < left {
		return nil, false
	}
	return parseInlineList(value[left : right+1]), true
}

// LoadSchedulerAliasingPin reads the canonical backend aliasing registry body.
// Backend declarations carry the effective class values while this pin keeps
// their governing registry exact and replayable.
func LoadSchedulerAliasingPin(path string) (scheduler.SchedulerAliasingInput, []byte, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return scheduler.SchedulerAliasingInput{}, nil, err
	}
	sum := sha256.Sum256(raw)
	return scheduler.SchedulerAliasingInput{RegistryHash: hex.EncodeToString(sum[:])}, raw, nil
}

// --- minimal purpose-built yaml subset reader ---

type yamlDoc struct {
	raw   []byte
	lines []string
}

func eachYAML(dir string, visit func(yamlDoc) error) error {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return err
	}
	for _, entry := range entries {
		if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".yaml") {
			continue
		}
		raw, err := os.ReadFile(filepath.Join(dir, entry.Name()))
		if err != nil {
			return err
		}
		if err := visit(yamlDoc{raw: raw, lines: strings.Split(string(raw), "\n")}); err != nil {
			return fmt.Errorf("%s: %w", entry.Name(), err)
		}
	}
	return nil
}

func stripComment(line string) string {
	if index := strings.Index(line, "#"); index >= 0 {
		return line[:index]
	}
	return line
}

func (d yamlDoc) value(key string) string {
	prefix := key + ":"
	for _, line := range d.lines {
		if strings.HasPrefix(line, prefix) {
			return cleanScalar(strings.TrimPrefix(stripComment(line), prefix))
		}
	}
	return ""
}

func (d yamlDoc) intValue(key string, fallback int) int {
	raw := d.value(key)
	if raw == "" {
		return fallback
	}
	parsed, err := strconv.Atoi(raw)
	if err != nil {
		return fallback
	}
	return parsed
}

// section returns the indented lines under a top-level key.
func (d yamlDoc) section(key string) []string {
	prefix := key + ":"
	var out []string
	inside := false
	for _, line := range d.lines {
		if inside {
			if line != "" && line[0] != ' ' && line[0] != '\t' {
				break
			}
			out = append(out, line)
			continue
		}
		if strings.HasPrefix(line, prefix) {
			inside = true
			rest := cleanScalar(strings.TrimPrefix(stripComment(line), prefix))
			if rest != "" {
				return []string{"inline:" + rest}
			}
		}
	}
	return out
}

// sectionKinds extracts `- kind: x` entries under a key.
func (d yamlDoc) sectionKinds(key string) []string {
	required, optional := d.sectionKindsSplit(key)
	return append(required, optional...)
}

// sectionKindsSplit separates required from `optional: true` kind entries.
func (d yamlDoc) sectionKindsSplit(key string) ([]string, []string) {
	var required, optional []string
	current := ""
	currentOptional := false
	flush := func() {
		if current == "" {
			return
		}
		if currentOptional {
			optional = append(optional, current)
		} else {
			required = append(required, current)
		}
	}
	for _, line := range d.section(key) {
		trimmed := strings.TrimSpace(stripComment(line))
		if value, ok := strings.CutPrefix(trimmed, "- kind:"); ok {
			flush()
			current = cleanScalar(value)
			currentOptional = false
			continue
		}
		if strings.HasPrefix(trimmed, "optional:") && cleanScalar(strings.TrimPrefix(trimmed, "optional:")) == "true" {
			currentOptional = true
		}
	}
	flush()
	return required, optional
}

// sectionKindElements maps each `- kind: x` entry to its `element:` grain,
// if declared (e.g. build consumes work-graph at element: work-packet grain).
func (d yamlDoc) sectionKindElements(key string) map[string]string {
	return d.sectionKindFields(key, "element")
}

// sectionKindFields extracts one scalar field per `- kind:` entry under key.
func (d yamlDoc) sectionKindFields(key, field string) map[string]string {
	fields := map[string]string{}
	current := ""
	for _, line := range d.section(key) {
		trimmed := strings.TrimSpace(stripComment(line))
		if value, ok := strings.CutPrefix(trimmed, "- kind:"); ok {
			current = cleanScalar(value)
			continue
		}
		if value, ok := strings.CutPrefix(trimmed, field+":"); ok && current != "" {
			fields[current] = cleanScalar(value)
		}
	}
	return fields
}

// sectionItems extracts `- x` entries under a key.
func (d yamlDoc) sectionItems(key string) []string {
	var out []string
	for _, line := range d.section(key) {
		trimmed := strings.TrimSpace(stripComment(line))
		if value, ok := strings.CutPrefix(trimmed, "- "); ok {
			out = append(out, cleanScalar(value))
		}
	}
	return out
}

// inlineList parses `key: [a, b]`.
func (d yamlDoc) inlineList(key string) []string {
	return parseInlineList(d.value(key))
}

// blockOrInlineList parses either an inline list or block `- x` items.
func (d yamlDoc) blockOrInlineList(key string) []string {
	section := d.section(key)
	if len(section) == 1 && strings.HasPrefix(section[0], "inline:") {
		return parseInlineList(strings.TrimPrefix(section[0], "inline:"))
	}
	var out []string
	for _, line := range section {
		trimmed := strings.TrimSpace(stripComment(line))
		if value, ok := strings.CutPrefix(trimmed, "- "); ok {
			out = append(out, cleanScalar(value))
		}
	}
	return out
}

// nestedValue reads `outer:\n  inner: value`.
func (d yamlDoc) nestedValue(outer, inner string) string {
	prefix := inner + ":"
	for _, line := range d.section(outer) {
		trimmed := strings.TrimSpace(stripComment(line))
		if strings.HasPrefix(trimmed, prefix) {
			return cleanScalar(strings.TrimPrefix(trimmed, prefix))
		}
	}
	return ""
}

// nestedInlineList reads `outer:\n  inner: [a, b]`.
func (d yamlDoc) nestedInlineList(outer, inner string) []string {
	return parseInlineList(d.nestedValue(outer, inner))
}

func parseInlineList(raw string) []string {
	raw = strings.TrimSpace(raw)
	if raw == "" || raw == "[]" {
		return nil
	}
	raw = strings.TrimPrefix(raw, "[")
	raw = strings.TrimSuffix(raw, "]")
	var out []string
	for _, part := range strings.Split(raw, ",") {
		part = cleanScalar(part)
		if part != "" {
			out = append(out, part)
		}
	}
	return out
}

func cleanScalar(raw string) string {
	return strings.Trim(strings.TrimSpace(raw), `"'`)
}

func sortStrings(values []string) {
	for i := 1; i < len(values); i++ {
		for j := i; j > 0 && values[j] < values[j-1]; j-- {
			values[j], values[j-1] = values[j-1], values[j]
		}
	}
}

