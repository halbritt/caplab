package derived

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"sort"
	"strconv"
	"strings"

	"github.com/halbritt/striatum-next/internal/scf"
	"gopkg.in/yaml.v3"
)

// This file is the placement-policy declaration surface: the exact set of
// placement facts scheduler policy is allowed to state, the parser that reads
// them, and the refusals that keep an unreadable statement from being read as
// no statement at all.
//
// Four declarations are load-bearing and all four live here rather than in code:
//
//   - OBJECTIVES. Every pass resolves an explicit placement objective, either
//     from its own row or from the declared fallback for the pass class. The
//     objective is bound at the live seam and projected before Bind; it is never
//     inferred from a pass id, and a pass with neither a row nor a fallback is a
//     refusal rather than a silent default (clause objectives-bind-per-pass).
//   - COMPARATOR. The materiality thresholds the unearned-effort demotion is
//     stated at. They are declared as integer basis points, not floats: the
//     policy digest is taken over exact bytes, and a threshold that hashes
//     differently on two machines is not a pin.
//   - STALENESS. One metric, one unit, one boundary, one bound. Everything
//     downstream asks freshness of a ledger coordinate against this single
//     declaration, so "stale" has exactly one meaning in the delivery.
//   - EFFORT ORDER. The ladder the coordinate table deliberately refuses to
//     carry. Effort siblings are oriented here, by declaration, never by a row
//     order or an alphabetical accident.
//
// The rule surface supports exactly two prefer shapes: an ordered `backends`
// list and a `quality_profile`. That is not a parser limitation dressed up as a
// design; it is the whole accepted preference vocabulary, and everything outside
// it refuses to load. The refusal is the point. Before this delivery, an
// unsupported key such as `expiring_capacity` parsed, matched, and ordered
// nothing — a decorative rule that read as operative policy in the file and
// bound nothing in the scheduler. The target's rule is explicit: "An unsupported
// prefer shape refuses policy load; policy that looks operative is never
// silently ignored."
//
// So this parser is closed at every level it reads. Unknown keys refuse. A
// capacity key refuses BY NAME, with a message saying where capacity expiry does
// live, because that is the exact mistake the retired rule made. Two supported
// shapes in one rule refuse, because a rule that names two orders states no
// order. A rule that carries neither a preference nor a restriction refuses,
// because it is decoration. A rule an earlier rule already subsumes refuses,
// because first-full-match makes it dead text that still reads as policy.
//
// Nothing here orders, folds, or binds. This file states what was declared and
// refuses what cannot be declared; the projection that lowers a shape into an
// order lives elsewhere, and its influence is prefer-only (D0008.C9).

// PlacementPolicySurfaceVersion is the version of the declaration surface and
// its canonicalization taken together. A trace pins the policy digest, so a
// changed surface yields a different identity rather than a silent
// reinterpretation of a pinned decision.
const PlacementPolicySurfaceVersion = 1

// ratioBasisPointParity is the basis-point spelling of 1.0. A worse-ratio
// threshold is a multiple of the better side's value, so parity is its floor.
const ratioBasisPointParity = 10000

// Placement-policy refusals. Every one is fail-closed and every one is
// distinguishable: a caller that wants to know whether a policy was absent,
// unsupported, or merely unresolvable against this repository can ask.
var (
	// ErrPlacementPolicyInvalid means the body is not a readable placement
	// policy at all: unparseable YAML, a wrong node kind, a non-integer where
	// an integer is declared.
	ErrPlacementPolicyInvalid = errors.New("derived: invalid placement policy")
	// ErrPlacementPolicyAbsent means a required declaration is missing. Absence
	// is never a default: a policy that does not declare its objectives has not
	// declared that it wants the default ones.
	ErrPlacementPolicyAbsent = errors.New("derived: absent placement policy declaration")
	// ErrPlacementPolicyUnsupported means the policy states something outside
	// the accepted vocabulary: an unknown key, a capacity key, or a prefer shape
	// this delivery does not support.
	ErrPlacementPolicyUnsupported = errors.New("derived: unsupported placement policy declaration")
	// ErrPlacementPolicyOutOfDomain means a declared value is not in its closed
	// domain.
	ErrPlacementPolicyOutOfDomain = errors.New("derived: placement policy value outside its domain")
	// ErrPlacementPolicyIncomplete means a declaration is present but does not
	// state everything it must: an effort order missing a graded effort, a rule
	// that prefers and requires nothing.
	ErrPlacementPolicyIncomplete = errors.New("derived: incomplete placement policy declaration")
	// ErrPlacementPolicyAmbiguous means the policy states one thing twice, or
	// two things that cannot both hold: a duplicate rule id, a repeated pass
	// objective, more than one supported shape in one rule.
	ErrPlacementPolicyAmbiguous = errors.New("derived: ambiguous placement policy declaration")
	// ErrPlacementPolicyUnresolvable means an operative declaration cannot bind
	// anything in this repository: a rule naming an unknown pass or backend, or
	// a rule an earlier rule has already subsumed.
	ErrPlacementPolicyUnresolvable = errors.New("derived: unresolvable placement policy declaration")
)

// PreferShape names one supported preference shape. The set is closed and has
// exactly two members; a third would be a design change, not a policy edit.
type PreferShape string

const (
	// PreferShapeBackends is an ordered, explicit list of backend ids.
	PreferShapeBackends PreferShape = "backends"
	// PreferShapeQualityProfile orders by the declared quality class.
	PreferShapeQualityProfile PreferShape = "quality_profile"
)

var preferShapeDomain = []PreferShape{PreferShapeBackends, PreferShapeQualityProfile}

// PreferShapeDomain returns the two supported prefer shapes in canonical order.
func PreferShapeDomain() []PreferShape {
	return append([]PreferShape(nil), preferShapeDomain...)
}

// QualityProfile is the value domain of the quality_profile shape.
type QualityProfile string

const (
	// QualityProfileHighest prefers the strongest declared quality class first.
	QualityProfileHighest QualityProfile = "highest"
	// QualityProfileAny expresses no quality preference: the incoming order
	// stands. It is declarable because "this rule deliberately orders nothing"
	// is a statement policy is allowed to make, and an absent rule is not.
	QualityProfileAny QualityProfile = "any"
)

var qualityProfileDomain = []QualityProfile{QualityProfileAny, QualityProfileHighest}

// QualityProfileDomain returns the closed quality_profile domain in canonical
// order.
func QualityProfileDomain() []QualityProfile {
	return append([]QualityProfile(nil), qualityProfileDomain...)
}

// Valid reports whether the profile is in the closed domain.
func (p QualityProfile) Valid() bool {
	for _, member := range qualityProfileDomain {
		if p == member {
			return true
		}
	}
	return false
}

// TelemetryInfluence is the declared force outcome evidence has over placement.
// The domain is closed at two values, and neither of them can unlock anything:
// prefer_only reorders candidates that already survive every hard filter
// (D0008.C9, clause telemetry-is-prefer-only).
type TelemetryInfluence string

const (
	// TelemetryInfluenceNone is the pre-@3 setting: evidence orders nothing.
	TelemetryInfluenceNone TelemetryInfluence = "none"
	// TelemetryInfluencePreferOnly lets evidence reorder survivors and nothing
	// else.
	TelemetryInfluencePreferOnly TelemetryInfluence = "prefer_only"
)

var telemetryInfluenceDomain = []TelemetryInfluence{TelemetryInfluenceNone, TelemetryInfluencePreferOnly}

// TelemetryInfluenceDomain returns the closed influence domain in canonical
// order.
func TelemetryInfluenceDomain() []TelemetryInfluence {
	return append([]TelemetryInfluence(nil), telemetryInfluenceDomain...)
}

// Valid reports whether the influence is in the closed domain.
func (i TelemetryInfluence) Valid() bool {
	for _, member := range telemetryInfluenceDomain {
		if i == member {
			return true
		}
	}
	return false
}

// StalenessMetric names how distance from the evaluation frontier is measured.
// There is exactly one, and it is a ledger distance rather than an age: this
// delivery has no clock, and a wall-clock staleness would make a replayed
// decision depend on when the replay happened.
type StalenessMetric string

// StalenessMetricLedgerSeqLag is frontier sequence minus evidence sequence.
const StalenessMetricLedgerSeqLag StalenessMetric = "ledger_seq_lag"

// StalenessUnit names the unit the bound is stated in.
type StalenessUnit string

// StalenessUnitRecords is the unit of a sequence lag: ledger records.
const StalenessUnitRecords StalenessUnit = "records"

// StalenessBoundary states whether the declared bound is itself fresh.
type StalenessBoundary string

const (
	// StalenessBoundaryInclusive means lag == max_lag is still fresh.
	StalenessBoundaryInclusive StalenessBoundary = "inclusive"
	// StalenessBoundaryExclusive means lag == max_lag is already stale.
	StalenessBoundaryExclusive StalenessBoundary = "exclusive"
)

var stalenessBoundaryDomain = []StalenessBoundary{StalenessBoundaryExclusive, StalenessBoundaryInclusive}

// StalenessBoundaryDomain returns the closed boundary domain in canonical order.
func StalenessBoundaryDomain() []StalenessBoundary {
	return append([]StalenessBoundary(nil), stalenessBoundaryDomain...)
}

// StalenessPolicy is the single declared answer to "is this evidence current".
// Every freshness question in the delivery — a merit cell's, a prior's, a
// demotion's eligibility — is asked against this one declaration, so there is
// one definition of stale rather than one per consumer.
type StalenessPolicy struct {
	Metric   StalenessMetric   `json:"metric"`
	Unit     StalenessUnit     `json:"unit"`
	MaxLag   uint64            `json:"max_lag"`
	Boundary StalenessBoundary `json:"boundary"`
}

// Validate reports whether the staleness declaration is complete and in domain.
func (s StalenessPolicy) Validate() error {
	if s.Metric == "" || s.Unit == "" || s.Boundary == "" {
		return fmt.Errorf("%w: staleness declares metric %q, unit %q, boundary %q", ErrPlacementPolicyIncomplete, s.Metric, s.Unit, s.Boundary)
	}
	if s.Metric != StalenessMetricLedgerSeqLag {
		return fmt.Errorf("%w: staleness metric %q is not %q", ErrPlacementPolicyOutOfDomain, s.Metric, StalenessMetricLedgerSeqLag)
	}
	if s.Unit != StalenessUnitRecords {
		return fmt.Errorf("%w: staleness unit %q is not %q", ErrPlacementPolicyOutOfDomain, s.Unit, StalenessUnitRecords)
	}
	if s.Boundary != StalenessBoundaryInclusive && s.Boundary != StalenessBoundaryExclusive {
		return fmt.Errorf("%w: staleness boundary %q is neither %q nor %q", ErrPlacementPolicyOutOfDomain,
			s.Boundary, StalenessBoundaryInclusive, StalenessBoundaryExclusive)
	}
	if s.MaxLag == 0 {
		return fmt.Errorf("%w: staleness max_lag is 0, which declares that nothing is ever current", ErrPlacementPolicyOutOfDomain)
	}
	return nil
}

// Fresh reports whether a lag of this many records is current under the declared
// boundary. It is the one place the boundary is interpreted.
func (s StalenessPolicy) Fresh(lag uint64) bool {
	if s.Boundary == StalenessBoundaryExclusive {
		return lag < s.MaxLag
	}
	return lag <= s.MaxLag
}

func (s StalenessPolicy) canonicalValue() map[string]any {
	return map[string]any{
		"boundary": string(s.Boundary),
		"max_lag":  int64(s.MaxLag),
		"metric":   string(s.Metric),
		"unit":     string(s.Unit),
	}
}

// DemotionComparator carries the materiality thresholds the unearned-effort
// demotion is stated at.
//
// Every threshold is an integer in basis points and never a float. Two reasons,
// and both are load-bearing: the policy digest is taken over canonical bytes and
// scf carries no float, so a float threshold could not be pinned at all; and a
// demotion trace that says "materially worse" has to name an exact number that
// re-reads identically, which 12500bp does and 1.25 does not always.
//
// Ratios are stated against the better side: a latency ratio of 12500bp means
// the higher-effort tuple's latency exceeds the lower-effort tuple's by 25%
// before the comparison calls it materially worse. Deltas are absolute
// differences of rates already in [0,1], stated in the same basis points.
type DemotionComparator struct {
	// ID names the comparison relation this delivery ships, so a trace records
	// which relation produced an edge and not merely which numbers it used.
	ID string `json:"id"`
	// LatencyWorseRatioBP is the observed-active latency ratio above which the
	// higher-effort side is materially slower.
	LatencyWorseRatioBP uint64 `json:"latency_worse_ratio_bp"`
	// CostWorseRatioBP is the observed-cost ratio above which it is materially
	// dearer. Absent cost is absent, never zero: the comparator reads this
	// threshold only when both sides reported money in one currency.
	CostWorseRatioBP uint64 `json:"cost_worse_ratio_bp"`
	// AdverseCompletionWorseDeltaBP is the absolute rate difference above which
	// its error-or-abandonment share is materially worse.
	AdverseCompletionWorseDeltaBP uint64 `json:"adverse_completion_worse_delta_bp"`
	// QualityAdvantageDeltaBP is the absolute admission-quality rate difference
	// at or above which the higher-effort side HAS an advantage and is therefore
	// never demoted, however much slower or dearer it is.
	QualityAdvantageDeltaBP uint64 `json:"quality_advantage_delta_bp"`
}

// LatencyWorseRatio returns the latency threshold as a ratio.
func (c DemotionComparator) LatencyWorseRatio() float64 {
	return float64(c.LatencyWorseRatioBP) / float64(ratioBasisPointParity)
}

// CostWorseRatio returns the cost threshold as a ratio.
func (c DemotionComparator) CostWorseRatio() float64 {
	return float64(c.CostWorseRatioBP) / float64(ratioBasisPointParity)
}

// AdverseCompletionWorseDelta returns the adverse-completion threshold as a rate
// difference.
func (c DemotionComparator) AdverseCompletionWorseDelta() float64 {
	return float64(c.AdverseCompletionWorseDeltaBP) / float64(ratioBasisPointParity)
}

// QualityAdvantageDelta returns the quality-advantage threshold as a rate
// difference.
func (c DemotionComparator) QualityAdvantageDelta() float64 {
	return float64(c.QualityAdvantageDeltaBP) / float64(ratioBasisPointParity)
}

// Validate reports whether the comparator is complete and in domain. A ratio at
// or below parity would demote a tuple for being no worse; a delta above 10000bp
// is a difference of rates larger than the whole [0,1] range and can never be
// met, which is a threshold that silently disables its own dimension.
func (c DemotionComparator) Validate() error {
	if c.ID == "" {
		return fmt.Errorf("%w: comparator names no relation", ErrPlacementPolicyIncomplete)
	}
	for _, ratio := range []struct {
		name  string
		value uint64
	}{
		{"latency_worse_ratio_bp", c.LatencyWorseRatioBP},
		{"cost_worse_ratio_bp", c.CostWorseRatioBP},
	} {
		if ratio.value <= ratioBasisPointParity {
			return fmt.Errorf("%w: comparator %s is %d, at or below parity %d", ErrPlacementPolicyOutOfDomain,
				ratio.name, ratio.value, ratioBasisPointParity)
		}
	}
	for _, delta := range []struct {
		name  string
		value uint64
	}{
		{"adverse_completion_worse_delta_bp", c.AdverseCompletionWorseDeltaBP},
		{"quality_advantage_delta_bp", c.QualityAdvantageDeltaBP},
	} {
		if delta.value == 0 || delta.value > ratioBasisPointParity {
			return fmt.Errorf("%w: comparator %s is %d, outside (0,%d]", ErrPlacementPolicyOutOfDomain,
				delta.name, delta.value, ratioBasisPointParity)
		}
	}
	return nil
}

func (c DemotionComparator) canonicalValue() map[string]any {
	return map[string]any{
		"adverse_completion_worse_delta_bp": int64(c.AdverseCompletionWorseDeltaBP),
		"cost_worse_ratio_bp":               int64(c.CostWorseRatioBP),
		"id":                                c.ID,
		"latency_worse_ratio_bp":            int64(c.LatencyWorseRatioBP),
		"quality_advantage_delta_bp":        int64(c.QualityAdvantageDeltaBP),
	}
}

// PlacementPassObjective is one pass's declared objective.
type PlacementPassObjective struct {
	Pass      string    `json:"pass"`
	Objective Objective `json:"objective"`
}

// PlacementObjectives is the objective declaration set: the per-pass rows and
// the explicit fallback the declared pass class resolves to.
//
// The fallback is REQUIRED. The target permits a pass class with an explicit
// fallback in place of a row per cataloged pass, and "explicit" is the whole
// content of the permission: a policy that declares neither a row nor a fallback
// for a pass has not chosen the default objective for it, it has failed to
// choose, and ObjectiveFor refuses rather than choosing on its behalf.
type PlacementObjectives struct {
	Fallback Objective                `json:"fallback"`
	ByPass   []PlacementPassObjective `json:"by_pass"`
}

// Validate reports whether every declared objective is an accepted one, the rows
// are canonically ordered, and no pass is declared twice.
func (o PlacementObjectives) Validate() error {
	if o.Fallback == "" {
		return fmt.Errorf("%w: objectives declare no fallback for the pass class", ErrPlacementPolicyAbsent)
	}
	if !ObjectiveAccepted(o.Fallback) {
		return fmt.Errorf("%w: objective fallback %q is not an accepted objective", ErrPlacementPolicyOutOfDomain, o.Fallback)
	}
	seen := make(map[string]bool, len(o.ByPass))
	for i, row := range o.ByPass {
		if row.Pass == "" {
			return fmt.Errorf("%w: objective row %d names no pass", ErrPlacementPolicyIncomplete, i)
		}
		if !ObjectiveAccepted(row.Objective) {
			return fmt.Errorf("%w: pass %s declares objective %q, which is not an accepted objective", ErrPlacementPolicyOutOfDomain, row.Pass, row.Objective)
		}
		if seen[row.Pass] {
			return fmt.Errorf("%w: pass %s declares an objective twice", ErrPlacementPolicyAmbiguous, row.Pass)
		}
		seen[row.Pass] = true
		if i > 0 && o.ByPass[i-1].Pass >= row.Pass {
			return fmt.Errorf("%w: objective rows are not in strictly ascending pass order at %q", ErrPlacementPolicyInvalid, row.Pass)
		}
	}
	return nil
}

func (o PlacementObjectives) canonicalValue() map[string]any {
	rows := make([]any, 0, len(o.ByPass))
	for _, row := range o.ByPass {
		rows = append(rows, map[string]any{"objective": string(row.Objective), "pass": row.Pass})
	}
	return map[string]any{"by_pass": rows, "fallback": string(o.Fallback)}
}

// PlacementMatch is the closed match vocabulary: which pass, and optionally
// whether the run is gating.
//
// `mode` is deliberately absent. The retired harvest rule matched on it and
// preferred a capacity key, and neither half bound anything; run mode is not a
// placement coordinate in this delivery, so a rule matching on one refuses
// rather than reading as live policy.
type PlacementMatch struct {
	Pass string `json:"pass"`
	// Gating restricts the rule to gating (or explicitly non-gating) runs.
	// GatingDeclared distinguishes "restricted to non-gating" from "not
	// restricted", which a bare bool cannot.
	Gating         bool `json:"gating"`
	GatingDeclared bool `json:"gating_declared"`
}

// Applies reports whether the match admits a run of this pass and gating shape.
func (m PlacementMatch) Applies(passID string, gating bool) bool {
	if m.Pass != "" && m.Pass != passID {
		return false
	}
	if m.GatingDeclared && m.Gating != gating {
		return false
	}
	return true
}

// subsumes reports whether every run this match admits is also admitted by the
// other match. It is the mechanical form of "an earlier rule already answers
// this", which under first-full-match makes the later rule dead text.
func (m PlacementMatch) subsumes(other PlacementMatch) bool {
	if m.Pass != "" && m.Pass != other.Pass {
		return false
	}
	if m.GatingDeclared && (!other.GatingDeclared || m.Gating != other.Gating) {
		return false
	}
	return true
}

func (m PlacementMatch) canonicalValue() map[string]any {
	value := map[string]any{"pass": m.Pass}
	if m.GatingDeclared {
		value["gating"] = m.Gating
	}
	return value
}

// PlacementPrefer is a rule's preference: exactly one supported shape, or none.
// A rule may state no preference at all — that is how a rule restricts without
// re-preferring — but it may never state two, because two shapes in one rule
// name two orders and the rule then states neither.
type PlacementPrefer struct {
	Shape          PreferShape    `json:"shape"`
	Backends       []string       `json:"backends,omitempty"`
	QualityProfile QualityProfile `json:"quality_profile,omitempty"`
}

// Declared reports whether the rule states a preference at all.
func (p PlacementPrefer) Declared() bool { return p.Shape != "" }

// Validate reports whether the preference states exactly what its shape claims.
func (p PlacementPrefer) Validate() error {
	switch p.Shape {
	case "":
		if len(p.Backends) > 0 || p.QualityProfile != "" {
			return fmt.Errorf("%w: preference carries a value under no shape", ErrPlacementPolicyInvalid)
		}
		return nil
	case PreferShapeBackends:
		if p.QualityProfile != "" {
			return fmt.Errorf("%w: a backends preference also declares a quality_profile", ErrPlacementPolicyAmbiguous)
		}
		if len(p.Backends) == 0 {
			return fmt.Errorf("%w: a backends preference names no backend", ErrPlacementPolicyIncomplete)
		}
		seen := make(map[string]bool, len(p.Backends))
		for _, backendID := range p.Backends {
			if backendID == "" {
				return fmt.Errorf("%w: a backends preference names an empty backend", ErrPlacementPolicyIncomplete)
			}
			if seen[backendID] {
				return fmt.Errorf("%w: a backends preference names %s twice", ErrPlacementPolicyAmbiguous, backendID)
			}
			seen[backendID] = true
		}
		return nil
	case PreferShapeQualityProfile:
		if len(p.Backends) > 0 {
			return fmt.Errorf("%w: a quality_profile preference also names backends", ErrPlacementPolicyAmbiguous)
		}
		if !p.QualityProfile.Valid() {
			return fmt.Errorf("%w: quality_profile %q is not one of %s", ErrPlacementPolicyOutOfDomain,
				p.QualityProfile, renderQualityProfileDomain())
		}
		return nil
	}
	return fmt.Errorf("%w: prefer shape %q is not one of %s", ErrPlacementPolicyUnsupported, p.Shape, renderPreferShapeDomain())
}

func (p PlacementPrefer) canonicalValue() map[string]any {
	value := map[string]any{"shape": string(p.Shape)}
	switch p.Shape {
	case PreferShapeBackends:
		backends := make([]any, 0, len(p.Backends))
		for _, backendID := range p.Backends {
			backends = append(backends, backendID)
		}
		value["backends"] = backends
	case PreferShapeQualityProfile:
		value["quality_profile"] = string(p.QualityProfile)
	}
	return value
}

// PlacementIndependenceSubject is the only declarable independence restriction:
// the run's own subject. Rules may restrict, never relax (D0002.C9), so this
// value restates the contract and cannot weaken it.
const PlacementIndependenceSubject = "subject"

// PlacementRequire is a rule's restriction half. It is not a preference: it
// narrows what is eligible, ahead of and independently of any ordering.
type PlacementRequire struct {
	Independence string `json:"independence,omitempty"`
}

// Declared reports whether the rule states a restriction.
func (r PlacementRequire) Declared() bool { return r.Independence != "" }

// Validate reports whether the restriction is in domain.
func (r PlacementRequire) Validate() error {
	if r.Independence == "" || r.Independence == PlacementIndependenceSubject {
		return nil
	}
	return fmt.Errorf("%w: require.independence %q is not %q", ErrPlacementPolicyOutOfDomain, r.Independence, PlacementIndependenceSubject)
}

func (r PlacementRequire) canonicalValue() map[string]any {
	return map[string]any{"independence": r.Independence}
}

// PlacementRule is one ordered placement rule: what it matches, what it prefers,
// and what it requires. Rules retain their declared order and the first full
// match wins.
type PlacementRule struct {
	ID      string           `json:"id"`
	Match   PlacementMatch   `json:"match"`
	Prefer  PlacementPrefer  `json:"prefer"`
	Require PlacementRequire `json:"require"`
}

// Operative reports whether the rule states anything at all. A rule that neither
// prefers nor requires is decoration; it refuses at Validate.
func (r PlacementRule) Operative() bool { return r.Prefer.Declared() || r.Require.Declared() }

// Validate reports whether the rule is a complete, unambiguous, in-domain
// statement.
func (r PlacementRule) Validate() error {
	if r.ID == "" {
		return fmt.Errorf("%w: a placement rule declares no id", ErrPlacementPolicyIncomplete)
	}
	if r.Match.Pass == "" {
		return fmt.Errorf("%w: rule %s matches no pass", ErrPlacementPolicyIncomplete, r.ID)
	}
	if err := r.Prefer.Validate(); err != nil {
		return fmt.Errorf("rule %s: %w", r.ID, err)
	}
	if err := r.Require.Validate(); err != nil {
		return fmt.Errorf("rule %s: %w", r.ID, err)
	}
	if !r.Operative() {
		return fmt.Errorf("%w: rule %s neither prefers nor requires anything", ErrPlacementPolicyIncomplete, r.ID)
	}
	return nil
}

func (r PlacementRule) canonicalValue() map[string]any {
	return map[string]any{
		"id":      r.ID,
		"match":   r.Match.canonicalValue(),
		"prefer":  r.Prefer.canonicalValue(),
		"require": r.Require.canonicalValue(),
	}
}

// PlacementPolicy is the whole parsed, validated placement surface of one
// scheduler policy body.
type PlacementPolicy struct {
	Version            int                 `json:"version"`
	Objectives         PlacementObjectives `json:"objectives"`
	Comparator         DemotionComparator  `json:"comparator"`
	Staleness          StalenessPolicy     `json:"staleness"`
	EffortOrder        []Effort            `json:"effort_order"`
	Rules              []PlacementRule     `json:"rules"`
	TelemetryInfluence TelemetryInfluence  `json:"telemetry_influence"`
	// MinSamples is the declared minimum sample count a cell must reach before
	// its evidence is comparable at all. It is read from the accepted telemetry
	// block rather than restated under the comparator: one number, one home.
	MinSamples uint64 `json:"min_samples"`
}

// ObjectiveFor resolves the placement objective bound for a pass: its own
// declared row, or the declared fallback. A pass the policy cannot answer for is
// a refusal, never the default objective — placing a pass under an objective
// nobody declared for it is exactly what clause objectives-bind-per-pass forbids.
func (p PlacementPolicy) ObjectiveFor(passID string) (Objective, error) {
	if passID == "" {
		return "", fmt.Errorf("%w: an objective was asked for an unnamed pass", ErrPlacementPolicyAbsent)
	}
	for _, row := range p.Objectives.ByPass {
		if row.Pass == passID {
			return row.Objective, nil
		}
	}
	if p.Objectives.Fallback == "" {
		return "", fmt.Errorf("%w: pass %s has no declared objective and the policy declares no fallback", ErrPlacementPolicyAbsent, passID)
	}
	return p.Objectives.Fallback, nil
}

// RuleFor returns the first rule matching a pass and gating shape, and whether
// one matched. First full match wins, in declared order.
func (p PlacementPolicy) RuleFor(passID string, gating bool) (PlacementRule, bool) {
	for _, rule := range p.Rules {
		if rule.Match.Applies(passID, gating) {
			return rule, true
		}
	}
	return PlacementRule{}, false
}

// EffortRank returns an effort's position on the declared ladder, and whether
// the ladder places it. EffortDefault is never placed: it declares that the
// tuple pins no effort knob, so it sits nowhere and forms no sibling pair.
func (p PlacementPolicy) EffortRank(effort Effort) (int, bool) {
	for rank, member := range p.EffortOrder {
		if member == effort {
			return rank, true
		}
	}
	return 0, false
}

// Validate reports whether the policy is a complete, unambiguous statement of
// every declaration this delivery binds.
func (p PlacementPolicy) Validate() error {
	if p.Version != PlacementPolicySurfaceVersion {
		return fmt.Errorf("%w: placement surface version %d is not %d", ErrPlacementPolicyInvalid, p.Version, PlacementPolicySurfaceVersion)
	}
	if err := p.Objectives.Validate(); err != nil {
		return err
	}
	if err := p.Comparator.Validate(); err != nil {
		return err
	}
	if err := p.Staleness.Validate(); err != nil {
		return err
	}
	if err := validateEffortOrder(p.EffortOrder); err != nil {
		return err
	}
	if !p.TelemetryInfluence.Valid() {
		return fmt.Errorf("%w: telemetry influence %q is not one of %s", ErrPlacementPolicyOutOfDomain,
			p.TelemetryInfluence, renderTelemetryInfluenceDomain())
	}
	if p.MinSamples == 0 {
		return fmt.Errorf("%w: telemetry min_samples is 0, which declares that one sample is evidence", ErrPlacementPolicyOutOfDomain)
	}
	if len(p.Rules) == 0 {
		return fmt.Errorf("%w: the policy declares no placement rule", ErrPlacementPolicyAbsent)
	}
	seen := make(map[string]bool, len(p.Rules))
	for i, rule := range p.Rules {
		if err := rule.Validate(); err != nil {
			return err
		}
		if seen[rule.ID] {
			return fmt.Errorf("%w: rule id %s is declared twice", ErrPlacementPolicyAmbiguous, rule.ID)
		}
		seen[rule.ID] = true
		for j := 0; j < i; j++ {
			if p.Rules[j].Match.subsumes(rule.Match) {
				return fmt.Errorf("%w: rule %s can never match — rule %s already matches every run it names", ErrPlacementPolicyUnresolvable, rule.ID, p.Rules[j].ID)
			}
		}
	}
	return nil
}

// validateEffortOrder holds the declared ladder to exactly the graded efforts:
// every one of them, each exactly once, and nothing else. An incomplete ladder
// leaves a sibling pair unorientable, a repeated rung makes it ambiguous, and
// EffortDefault on it would place a tuple that declares it sits nowhere.
func validateEffortOrder(order []Effort) error {
	graded := make([]Effort, 0, len(PlacementEffortDomain()))
	for _, effort := range PlacementEffortDomain() {
		if effort.IsGraded() {
			graded = append(graded, effort)
		}
	}
	if len(order) == 0 {
		return fmt.Errorf("%w: the policy declares no effort order", ErrPlacementPolicyAbsent)
	}
	seen := make(map[Effort]bool, len(order))
	for _, effort := range order {
		if effort == EffortDefault {
			return fmt.Errorf("%w: effort order places %q, which declares that it sits nowhere on the ladder", ErrPlacementPolicyOutOfDomain, EffortDefault)
		}
		if !effort.IsGraded() {
			return fmt.Errorf("%w: effort order names %q, which is not a graded effort", ErrPlacementPolicyOutOfDomain, effort)
		}
		if seen[effort] {
			return fmt.Errorf("%w: effort order places %q twice", ErrPlacementPolicyAmbiguous, effort)
		}
		seen[effort] = true
	}
	for _, effort := range graded {
		if !seen[effort] {
			return fmt.Errorf("%w: effort order does not place the graded effort %q", ErrPlacementPolicyIncomplete, effort)
		}
	}
	return nil
}

// Resolve holds every operative declaration to what this repository actually
// carries: the cataloged passes and the placeable backends. A rule naming a pass
// no catalog declares, or a backend no coordinate table places, is operative
// text that can bind nothing — the same failure mode as the retired capacity
// rule, one level up.
//
// passIDs and backendIDs are the repository's own; both must be non-empty,
// because resolving against nothing would accept everything.
func (p PlacementPolicy) Resolve(passIDs, backendIDs []string) error {
	if len(passIDs) == 0 {
		return fmt.Errorf("%w: no cataloged pass was supplied to resolve placement policy against", ErrPlacementPolicyUnresolvable)
	}
	if len(backendIDs) == 0 {
		return fmt.Errorf("%w: no placeable backend was supplied to resolve placement policy against", ErrPlacementPolicyUnresolvable)
	}
	passes := make(map[string]bool, len(passIDs))
	for _, passID := range passIDs {
		passes[passID] = true
	}
	backends := make(map[string]bool, len(backendIDs))
	for _, backendID := range backendIDs {
		backends[backendID] = true
	}
	for _, row := range p.Objectives.ByPass {
		if !passes[row.Pass] {
			return fmt.Errorf("%w: objectives declare pass %s, which this catalog does not carry", ErrPlacementPolicyUnresolvable, row.Pass)
		}
	}
	for _, rule := range p.Rules {
		if !passes[rule.Match.Pass] {
			return fmt.Errorf("%w: rule %s matches pass %s, which this catalog does not carry", ErrPlacementPolicyUnresolvable, rule.ID, rule.Match.Pass)
		}
		for _, backendID := range rule.Prefer.Backends {
			if !backends[backendID] {
				return fmt.Errorf("%w: rule %s prefers backend %s, which is not placeable here", ErrPlacementPolicyUnresolvable, rule.ID, backendID)
			}
		}
	}
	return nil
}

// Preimage returns the canonical SCF-1 bytes the policy digest is taken over. It
// commits to the surface version and to every declaration in declared order —
// rules keep their file order because that order IS the first-full-match
// semantics, while the objective rows are canonically sorted because their order
// carries no meaning.
func (p PlacementPolicy) Preimage() ([]byte, error) {
	if err := p.Validate(); err != nil {
		return nil, err
	}
	rules := make([]any, 0, len(p.Rules))
	for _, rule := range p.Rules {
		rules = append(rules, rule.canonicalValue())
	}
	order := make([]any, 0, len(p.EffortOrder))
	for _, effort := range p.EffortOrder {
		order = append(order, string(effort))
	}
	return scf.Marshal(map[string]any{
		"comparator":          p.Comparator.canonicalValue(),
		"effort_order":        order,
		"min_samples":         int64(p.MinSamples),
		"objectives":          p.Objectives.canonicalValue(),
		"rules":               rules,
		"staleness":           p.Staleness.canonicalValue(),
		"telemetry_influence": string(p.TelemetryInfluence),
		"version":             int64(p.Version),
	})
}

// Digest is the placement-policy identity a scheduling decision pins. A decision
// made under one set of declarations can never be replayed under another.
func (p PlacementPolicy) Digest() (string, error) {
	preimage, err := p.Preimage()
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(preimage)
	return hex.EncodeToString(sum[:]), nil
}

// The closed key vocabularies. Anything outside them refuses; capacity keys
// refuse by name, with the message naming where capacity expiry does live.
var (
	placementPolicyBlockKeys = map[string]bool{
		"objectives": true, "comparator": true, "staleness": true, "effort_order": true,
	}
	placementObjectiveKeys  = map[string]bool{"fallback": true, "by_pass": true}
	placementComparatorKeys = map[string]bool{
		"id": true, "latency_worse_ratio_bp": true, "cost_worse_ratio_bp": true,
		"adverse_completion_worse_delta_bp": true, "quality_advantage_delta_bp": true,
	}
	placementStalenessKeys = map[string]bool{"metric": true, "unit": true, "max_lag": true, "boundary": true}
	placementRuleKeys      = map[string]bool{"id": true, "match": true, "prefer": true, "require": true}
	placementMatchKeys     = map[string]bool{"pass": true, "gating": true}
	placementPreferKeys    = map[string]bool{"backends": true, "quality_profile": true}
	placementRequireKeys   = map[string]bool{"independence": true}
	placementTelemetryKeys = map[string]bool{"influence": true, "min_samples": true}

	// placementPolicyCapacityKeys are refused by name wherever the placement
	// surface reads. Capacity expiry is a real fact with a real home — the
	// backend declarations and the dispatch and signal paths that own them —
	// and the whole reason the retired harvest rule was decorative is that it
	// stated it here, where placement never reads it.
	placementPolicyCapacityKeys = map[string]bool{
		"capacity":             true,
		"capacity_observation": true,
		"concurrency":          true,
		"exhaustion_behavior":  true,
		"expires_at":           true,
		"expiring_capacity":    true,
		"lanes":                true,
		"max_lanes":            true,
		"mode":                 true,
		"quota":                true,
		"window":               true,
	}
)

// ParsePlacementPolicy reads and validates the placement surface of one exact
// scheduler policy body. Every refusal names the source and the offending
// declaration.
func ParsePlacementPolicy(raw []byte, source string) (PlacementPolicy, error) {
	fail := func(err error) (PlacementPolicy, error) {
		return PlacementPolicy{}, fmt.Errorf("placement policy: %s: %w", source, err)
	}

	var top map[string]yaml.Node
	if err := yaml.Unmarshal(raw, &top); err != nil {
		return fail(fmt.Errorf("%w: %v", ErrPlacementPolicyInvalid, err))
	}
	if len(top) == 0 {
		return fail(fmt.Errorf("%w: the body declares nothing", ErrPlacementPolicyAbsent))
	}

	policy := PlacementPolicy{Version: PlacementPolicySurfaceVersion}

	placement, ok := top["placement"]
	if !ok {
		return fail(fmt.Errorf("%w: the body declares no `placement` block", ErrPlacementPolicyAbsent))
	}
	block, err := placementMapping(placement, "placement", placementPolicyBlockKeys)
	if err != nil {
		return fail(err)
	}
	for _, key := range []string{"objectives", "comparator", "staleness", "effort_order"} {
		if _, ok := block[key]; !ok {
			return fail(fmt.Errorf("%w: placement declares no %s", ErrPlacementPolicyAbsent, key))
		}
	}
	if policy.Objectives, err = parsePlacementObjectives(block["objectives"]); err != nil {
		return fail(err)
	}
	if policy.Comparator, err = parsePlacementComparator(block["comparator"]); err != nil {
		return fail(err)
	}
	if policy.Staleness, err = parsePlacementStaleness(block["staleness"]); err != nil {
		return fail(err)
	}
	if policy.EffortOrder, err = parsePlacementEffortOrder(block["effort_order"]); err != nil {
		return fail(err)
	}

	telemetry, ok := top["telemetry"]
	if !ok {
		return fail(fmt.Errorf("%w: the body declares no `telemetry` block", ErrPlacementPolicyAbsent))
	}
	if policy.TelemetryInfluence, policy.MinSamples, err = parsePlacementTelemetry(telemetry); err != nil {
		return fail(err)
	}

	rules, ok := top["placement_rules"]
	if !ok {
		return fail(fmt.Errorf("%w: the body declares no `placement_rules`", ErrPlacementPolicyAbsent))
	}
	if policy.Rules, err = parsePlacementRules(rules); err != nil {
		return fail(err)
	}

	if err := policy.Validate(); err != nil {
		return fail(err)
	}
	return policy, nil
}

func placementMapping(node yaml.Node, what string, allowed map[string]bool) (map[string]yaml.Node, error) {
	var mapping map[string]yaml.Node
	if err := node.Decode(&mapping); err != nil {
		return nil, fmt.Errorf("%w: %s is not a mapping: %v", ErrPlacementPolicyInvalid, what, err)
	}
	for _, key := range sortedKeys(mapping) {
		if allowed[key] {
			continue
		}
		if placementPolicyCapacityKeys[key] {
			return nil, fmt.Errorf("%w: %s declares capacity key %q; placement reads no capacity fact — lane ceilings, windows, exhaustion behavior and expiry stay in the backend declarations and the dispatch and signal paths that own them",
				ErrPlacementPolicyUnsupported, what, key)
		}
		return nil, fmt.Errorf("%w: %s declares unknown key %q", ErrPlacementPolicyUnsupported, what, key)
	}
	return mapping, nil
}

func placementScalar(node yaml.Node, what string) (string, error) {
	if node.Kind != yaml.ScalarNode {
		return "", fmt.Errorf("%w: %s is not a scalar", ErrPlacementPolicyInvalid, what)
	}
	value := strings.TrimSpace(node.Value)
	if value == "" {
		return "", fmt.Errorf("%w: %s declares an empty value", ErrPlacementPolicyIncomplete, what)
	}
	return value, nil
}

func placementUint(node yaml.Node, what string) (uint64, error) {
	value, err := placementScalar(node, what)
	if err != nil {
		return 0, err
	}
	parsed, err := strconv.ParseUint(value, 10, 64)
	if err != nil {
		return 0, fmt.Errorf("%w: %s is %q, which is not a non-negative integer", ErrPlacementPolicyInvalid, what, value)
	}
	return parsed, nil
}

func placementBool(node yaml.Node, what string) (bool, error) {
	value, err := placementScalar(node, what)
	if err != nil {
		return false, err
	}
	switch value {
	case "true":
		return true, nil
	case "false":
		return false, nil
	}
	return false, fmt.Errorf("%w: %s is %q, which is neither true nor false", ErrPlacementPolicyOutOfDomain, what, value)
}

func parsePlacementObjectives(node yaml.Node) (PlacementObjectives, error) {
	mapping, err := placementMapping(node, "placement.objectives", placementObjectiveKeys)
	if err != nil {
		return PlacementObjectives{}, err
	}
	fallbackNode, ok := mapping["fallback"]
	if !ok {
		return PlacementObjectives{}, fmt.Errorf("%w: placement.objectives declares no fallback", ErrPlacementPolicyAbsent)
	}
	fallback, err := placementScalar(fallbackNode, "placement.objectives.fallback")
	if err != nil {
		return PlacementObjectives{}, err
	}
	objectives := PlacementObjectives{Fallback: Objective(fallback)}
	if byPass, ok := mapping["by_pass"]; ok {
		var rows map[string]yaml.Node
		if err := byPass.Decode(&rows); err != nil {
			return PlacementObjectives{}, fmt.Errorf("%w: placement.objectives.by_pass is not a mapping: %v", ErrPlacementPolicyInvalid, err)
		}
		for _, passID := range sortedKeys(rows) {
			value, err := placementScalar(rows[passID], "placement.objectives.by_pass."+passID)
			if err != nil {
				return PlacementObjectives{}, err
			}
			objectives.ByPass = append(objectives.ByPass, PlacementPassObjective{Pass: passID, Objective: Objective(value)})
		}
		sort.Slice(objectives.ByPass, func(i, j int) bool { return objectives.ByPass[i].Pass < objectives.ByPass[j].Pass })
	}
	return objectives, objectives.Validate()
}

func parsePlacementComparator(node yaml.Node) (DemotionComparator, error) {
	mapping, err := placementMapping(node, "placement.comparator", placementComparatorKeys)
	if err != nil {
		return DemotionComparator{}, err
	}
	for key := range placementComparatorKeys {
		if _, ok := mapping[key]; !ok {
			return DemotionComparator{}, fmt.Errorf("%w: placement.comparator declares no %s", ErrPlacementPolicyAbsent, key)
		}
	}
	id, err := placementScalar(mapping["id"], "placement.comparator.id")
	if err != nil {
		return DemotionComparator{}, err
	}
	comparator := DemotionComparator{ID: id}
	for _, field := range []struct {
		key    string
		target *uint64
	}{
		{"latency_worse_ratio_bp", &comparator.LatencyWorseRatioBP},
		{"cost_worse_ratio_bp", &comparator.CostWorseRatioBP},
		{"adverse_completion_worse_delta_bp", &comparator.AdverseCompletionWorseDeltaBP},
		{"quality_advantage_delta_bp", &comparator.QualityAdvantageDeltaBP},
	} {
		value, err := placementUint(mapping[field.key], "placement.comparator."+field.key)
		if err != nil {
			return DemotionComparator{}, err
		}
		*field.target = value
	}
	return comparator, comparator.Validate()
}

func parsePlacementStaleness(node yaml.Node) (StalenessPolicy, error) {
	mapping, err := placementMapping(node, "placement.staleness", placementStalenessKeys)
	if err != nil {
		return StalenessPolicy{}, err
	}
	for key := range placementStalenessKeys {
		if _, ok := mapping[key]; !ok {
			return StalenessPolicy{}, fmt.Errorf("%w: placement.staleness declares no %s", ErrPlacementPolicyAbsent, key)
		}
	}
	metric, err := placementScalar(mapping["metric"], "placement.staleness.metric")
	if err != nil {
		return StalenessPolicy{}, err
	}
	unit, err := placementScalar(mapping["unit"], "placement.staleness.unit")
	if err != nil {
		return StalenessPolicy{}, err
	}
	boundary, err := placementScalar(mapping["boundary"], "placement.staleness.boundary")
	if err != nil {
		return StalenessPolicy{}, err
	}
	maxLag, err := placementUint(mapping["max_lag"], "placement.staleness.max_lag")
	if err != nil {
		return StalenessPolicy{}, err
	}
	staleness := StalenessPolicy{
		Metric:   StalenessMetric(metric),
		Unit:     StalenessUnit(unit),
		MaxLag:   maxLag,
		Boundary: StalenessBoundary(boundary),
	}
	return staleness, staleness.Validate()
}

func parsePlacementEffortOrder(node yaml.Node) ([]Effort, error) {
	var values []string
	if err := node.Decode(&values); err != nil {
		return nil, fmt.Errorf("%w: placement.effort_order is not a sequence of scalars: %v", ErrPlacementPolicyInvalid, err)
	}
	order := make([]Effort, 0, len(values))
	for _, value := range values {
		order = append(order, Effort(strings.TrimSpace(value)))
	}
	return order, validateEffortOrder(order)
}

func parsePlacementTelemetry(node yaml.Node) (TelemetryInfluence, uint64, error) {
	mapping, err := placementMapping(node, "telemetry", placementTelemetryKeys)
	if err != nil {
		return "", 0, err
	}
	for key := range placementTelemetryKeys {
		if _, ok := mapping[key]; !ok {
			return "", 0, fmt.Errorf("%w: telemetry declares no %s", ErrPlacementPolicyAbsent, key)
		}
	}
	influence, err := placementScalar(mapping["influence"], "telemetry.influence")
	if err != nil {
		return "", 0, err
	}
	minSamples, err := placementUint(mapping["min_samples"], "telemetry.min_samples")
	if err != nil {
		return "", 0, err
	}
	if !TelemetryInfluence(influence).Valid() {
		return "", 0, fmt.Errorf("%w: telemetry influence %q is not one of %s", ErrPlacementPolicyOutOfDomain,
			influence, renderTelemetryInfluenceDomain())
	}
	return TelemetryInfluence(influence), minSamples, nil
}

func parsePlacementRules(node yaml.Node) ([]PlacementRule, error) {
	var rows []map[string]yaml.Node
	if err := node.Decode(&rows); err != nil {
		return nil, fmt.Errorf("%w: placement_rules is not a sequence of mappings: %v", ErrPlacementPolicyInvalid, err)
	}
	if len(rows) == 0 {
		return nil, fmt.Errorf("%w: placement_rules declares no rule", ErrPlacementPolicyAbsent)
	}
	rules := make([]PlacementRule, 0, len(rows))
	for index, row := range rows {
		rule, err := parsePlacementRule(index, row)
		if err != nil {
			return nil, err
		}
		rules = append(rules, rule)
	}
	return rules, nil
}

func parsePlacementRule(index int, row map[string]yaml.Node) (PlacementRule, error) {
	what := fmt.Sprintf("placement_rules[%d]", index)
	for _, key := range sortedKeys(row) {
		if placementRuleKeys[key] {
			continue
		}
		if placementPolicyCapacityKeys[key] {
			return PlacementRule{}, fmt.Errorf("%w: %s declares capacity key %q; placement reads no capacity fact", ErrPlacementPolicyUnsupported, what, key)
		}
		return PlacementRule{}, fmt.Errorf("%w: %s declares unknown key %q", ErrPlacementPolicyUnsupported, what, key)
	}
	idNode, ok := row["id"]
	if !ok {
		return PlacementRule{}, fmt.Errorf("%w: %s declares no id", ErrPlacementPolicyIncomplete, what)
	}
	id, err := placementScalar(idNode, what+".id")
	if err != nil {
		return PlacementRule{}, err
	}
	rule := PlacementRule{ID: id}
	what = "placement rule " + id

	matchNode, ok := row["match"]
	if !ok {
		return PlacementRule{}, fmt.Errorf("%w: %s declares no match", ErrPlacementPolicyIncomplete, what)
	}
	if rule.Match, err = parsePlacementMatch(matchNode, what); err != nil {
		return PlacementRule{}, err
	}
	if preferNode, ok := row["prefer"]; ok {
		if rule.Prefer, err = parsePlacementPrefer(preferNode, what); err != nil {
			return PlacementRule{}, err
		}
	}
	if requireNode, ok := row["require"]; ok {
		if rule.Require, err = parsePlacementRequire(requireNode, what); err != nil {
			return PlacementRule{}, err
		}
	}
	return rule, rule.Validate()
}

func parsePlacementMatch(node yaml.Node, what string) (PlacementMatch, error) {
	mapping, err := placementMapping(node, what+".match", placementMatchKeys)
	if err != nil {
		return PlacementMatch{}, err
	}
	passNode, ok := mapping["pass"]
	if !ok {
		return PlacementMatch{}, fmt.Errorf("%w: %s matches no pass", ErrPlacementPolicyIncomplete, what)
	}
	pass, err := placementScalar(passNode, what+".match.pass")
	if err != nil {
		return PlacementMatch{}, err
	}
	match := PlacementMatch{Pass: pass}
	if gatingNode, ok := mapping["gating"]; ok {
		gating, err := placementBool(gatingNode, what+".match.gating")
		if err != nil {
			return PlacementMatch{}, err
		}
		match.Gating = gating
		match.GatingDeclared = true
	}
	return match, nil
}

// parsePlacementPrefer reads the one supported shape a rule declares. Two shapes
// in one rule refuse: a rule naming both an ordered backend list and a quality
// profile states two orders, and there is no accepted precedence between them to
// pick one — inventing one here would be this parser deciding placement policy.
func parsePlacementPrefer(node yaml.Node, what string) (PlacementPrefer, error) {
	mapping, err := placementMapping(node, what+".prefer", placementPreferKeys)
	if err != nil {
		return PlacementPrefer{}, err
	}
	if len(mapping) == 0 {
		return PlacementPrefer{}, fmt.Errorf("%w: %s declares an empty prefer", ErrPlacementPolicyIncomplete, what)
	}
	if len(mapping) > 1 {
		return PlacementPrefer{}, fmt.Errorf("%w: %s declares %d supported prefer shapes (%s); a rule states exactly one order",
			ErrPlacementPolicyAmbiguous, what, len(mapping), strings.Join(sortedKeys(mapping), ", "))
	}
	if backendsNode, ok := mapping["backends"]; ok {
		var backends []string
		if err := backendsNode.Decode(&backends); err != nil {
			return PlacementPrefer{}, fmt.Errorf("%w: %s.prefer.backends is not a sequence of scalars: %v", ErrPlacementPolicyInvalid, what, err)
		}
		for i, backendID := range backends {
			backends[i] = strings.TrimSpace(backendID)
		}
		prefer := PlacementPrefer{Shape: PreferShapeBackends, Backends: backends}
		if err := prefer.Validate(); err != nil {
			return PlacementPrefer{}, fmt.Errorf("%s: %w", what, err)
		}
		return prefer, nil
	}
	profile, err := placementScalar(mapping["quality_profile"], what+".prefer.quality_profile")
	if err != nil {
		return PlacementPrefer{}, err
	}
	prefer := PlacementPrefer{Shape: PreferShapeQualityProfile, QualityProfile: QualityProfile(profile)}
	if err := prefer.Validate(); err != nil {
		return PlacementPrefer{}, fmt.Errorf("%s: %w", what, err)
	}
	return prefer, nil
}

func parsePlacementRequire(node yaml.Node, what string) (PlacementRequire, error) {
	mapping, err := placementMapping(node, what+".require", placementRequireKeys)
	if err != nil {
		return PlacementRequire{}, err
	}
	if len(mapping) == 0 {
		return PlacementRequire{}, fmt.Errorf("%w: %s declares an empty require", ErrPlacementPolicyIncomplete, what)
	}
	independence, err := placementScalar(mapping["independence"], what+".require.independence")
	if err != nil {
		return PlacementRequire{}, err
	}
	require := PlacementRequire{Independence: independence}
	if err := require.Validate(); err != nil {
		return PlacementRequire{}, fmt.Errorf("%s: %w", what, err)
	}
	return require, nil
}

func renderPreferShapeDomain() string {
	rendered := make([]string, 0, len(preferShapeDomain))
	for _, shape := range preferShapeDomain {
		rendered = append(rendered, string(shape))
	}
	return "[" + strings.Join(rendered, " ") + "]"
}

func renderQualityProfileDomain() string {
	rendered := make([]string, 0, len(qualityProfileDomain))
	for _, profile := range qualityProfileDomain {
		rendered = append(rendered, string(profile))
	}
	return "[" + strings.Join(rendered, " ") + "]"
}

func renderTelemetryInfluenceDomain() string {
	rendered := make([]string, 0, len(telemetryInfluenceDomain))
	for _, influence := range telemetryInfluenceDomain {
		rendered = append(rendered, string(influence))
	}
	return "[" + strings.Join(rendered, " ") + "]"
}

