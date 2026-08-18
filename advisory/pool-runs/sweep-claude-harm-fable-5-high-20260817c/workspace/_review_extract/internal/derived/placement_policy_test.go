package derived

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// The placement-policy surface earns its keep at the refusals. A parser that
// reads the accepted policy is table stakes; what the delivery actually depends
// on is that a policy which LOOKS operative and binds nothing cannot load. So
// the fixture corpus is one accepted body plus one body per refusal class, and
// every refusal is asserted by its sentinel error rather than by message text.

const placementPolicyFixtureDir = "../../testdata/placement/policy"

func loadPlacementPolicyFixture(t *testing.T, name string) ([]byte, string) {
	t.Helper()
	path := filepath.Join(placementPolicyFixtureDir, name)
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read fixture %s: %v", name, err)
	}
	return raw, path
}

func parsePlacementPolicyFixture(t *testing.T, name string) PlacementPolicy {
	t.Helper()
	raw, path := loadPlacementPolicyFixture(t, name)
	policy, err := ParsePlacementPolicy(raw, path)
	if err != nil {
		t.Fatalf("ParsePlacementPolicy(%s) error = %v", name, err)
	}
	return policy
}

func TestParsePlacementPolicyReadsTheAcceptedSurface(t *testing.T) {
	policy := parsePlacementPolicyFixture(t, "valid.yaml")

	if policy.Version != PlacementPolicySurfaceVersion {
		t.Fatalf("surface version = %d, want %d", policy.Version, PlacementPolicySurfaceVersion)
	}
	if policy.Objectives.Fallback != ObjectiveDefault {
		t.Errorf("objective fallback = %q, want %q", policy.Objectives.Fallback, ObjectiveDefault)
	}
	if len(policy.Objectives.ByPass) != 1 || policy.Objectives.ByPass[0].Pass != "fixture-review" ||
		policy.Objectives.ByPass[0].Objective != ObjectiveHighestQuality {
		t.Errorf("objective rows = %+v, want one fixture-review row at %q", policy.Objectives.ByPass, ObjectiveHighestQuality)
	}
	if policy.Comparator.ID != "fixture-dominance" || policy.Comparator.LatencyWorseRatioBP != 12500 ||
		policy.Comparator.CostWorseRatioBP != 12500 || policy.Comparator.AdverseCompletionWorseDeltaBP != 500 ||
		policy.Comparator.QualityAdvantageDeltaBP != 200 {
		t.Errorf("comparator = %+v, want the fixture thresholds", policy.Comparator)
	}
	if policy.Staleness != (StalenessPolicy{
		Metric:   StalenessMetricLedgerSeqLag,
		Unit:     StalenessUnitRecords,
		MaxLag:   5000,
		Boundary: StalenessBoundaryInclusive,
	}) {
		t.Errorf("staleness = %+v, want the fixture declaration", policy.Staleness)
	}
	wantOrder := []Effort{EffortLow, EffortMedium, EffortHigh, EffortXHigh, EffortMax}
	if len(policy.EffortOrder) != len(wantOrder) {
		t.Fatalf("effort order = %v, want %v", policy.EffortOrder, wantOrder)
	}
	for i, effort := range wantOrder {
		if policy.EffortOrder[i] != effort {
			t.Fatalf("effort order = %v, want %v", policy.EffortOrder, wantOrder)
		}
	}
	if policy.TelemetryInfluence != TelemetryInfluenceNone || policy.MinSamples != 20 {
		t.Errorf("telemetry = (%q, %d), want (%q, 20)", policy.TelemetryInfluence, policy.MinSamples, TelemetryInfluenceNone)
	}
	if len(policy.Rules) != 3 {
		t.Fatalf("rules = %d, want 3", len(policy.Rules))
	}
	if shape := policy.Rules[0].Prefer.Shape; shape != PreferShapeBackends {
		t.Errorf("first rule shape = %q, want %q", shape, PreferShapeBackends)
	}
	if shape := policy.Rules[2].Prefer.Shape; shape != PreferShapeQualityProfile {
		t.Errorf("third rule shape = %q, want %q", shape, PreferShapeQualityProfile)
	}
	if profile := policy.Rules[2].Prefer.QualityProfile; profile != QualityProfileHighest {
		t.Errorf("third rule profile = %q, want %q", profile, QualityProfileHighest)
	}
	if independence := policy.Rules[1].Require.Independence; independence != PlacementIndependenceSubject {
		t.Errorf("gating rule independence = %q, want %q", independence, PlacementIndependenceSubject)
	}
	if policy.Rules[1].Prefer.Declared() {
		t.Error("the gating rule declares a preference; it restricts only")
	}
}

// Both supported shapes are exercised by the accepted fixture, and nothing else
// is a shape. A third spelling arriving in policy must refuse, not degrade to
// the first two.
func TestPlacementPolicySupportsExactlyTwoPreferShapes(t *testing.T) {
	shapes := PreferShapeDomain()
	if len(shapes) != 2 || shapes[0] != PreferShapeBackends || shapes[1] != PreferShapeQualityProfile {
		t.Fatalf("prefer shape domain = %v, want exactly [backends quality_profile]", shapes)
	}
	policy := parsePlacementPolicyFixture(t, "valid.yaml")
	seen := map[PreferShape]bool{}
	for _, rule := range policy.Rules {
		if rule.Prefer.Declared() {
			seen[rule.Prefer.Shape] = true
		}
	}
	for _, shape := range shapes {
		if !seen[shape] {
			t.Errorf("the accepted fixture never exercises the %q shape", shape)
		}
	}
}

// One refusal per validation rule, each asserted by sentinel. The
// expiring_capacity case is the retired decorative rule: it is the reason this
// whole surface refuses instead of ignoring.
func TestParsePlacementPolicyRefusals(t *testing.T) {
	cases := []struct {
		fixture string
		want    error
	}{
		{"absent-placement-block.yaml", ErrPlacementPolicyAbsent},
		{"absent-objectives.yaml", ErrPlacementPolicyAbsent},
		{"absent-fallback.yaml", ErrPlacementPolicyAbsent},
		{"absent-effort-order.yaml", ErrPlacementPolicyAbsent},
		{"absent-staleness-boundary.yaml", ErrPlacementPolicyAbsent},
		{"absent-telemetry.yaml", ErrPlacementPolicyAbsent},
		{"absent-placement-rules.yaml", ErrPlacementPolicyAbsent},

		{"unsupported-prefer-expiring-capacity.yaml", ErrPlacementPolicyUnsupported},
		{"unsupported-prefer-key.yaml", ErrPlacementPolicyUnsupported},
		{"unsupported-match-mode.yaml", ErrPlacementPolicyUnsupported},
		{"unsupported-rule-key.yaml", ErrPlacementPolicyUnsupported},
		{"unsupported-placement-key.yaml", ErrPlacementPolicyUnsupported},
		{"unsupported-require-key.yaml", ErrPlacementPolicyUnsupported},

		{"out-of-domain-objective.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-fallback.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-quality-profile.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-staleness-metric.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-staleness-boundary.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-comparator-ratio.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-comparator-delta.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-effort.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-effort-default.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-influence.yaml", ErrPlacementPolicyOutOfDomain},
		{"out-of-domain-independence.yaml", ErrPlacementPolicyOutOfDomain},

		{"incomplete-effort-order.yaml", ErrPlacementPolicyIncomplete},
		{"incomplete-rule.yaml", ErrPlacementPolicyIncomplete},
		{"incomplete-empty-backends.yaml", ErrPlacementPolicyIncomplete},

		{"ambiguous-two-prefer-shapes.yaml", ErrPlacementPolicyAmbiguous},
		{"ambiguous-effort-order.yaml", ErrPlacementPolicyAmbiguous},
		{"ambiguous-rule-id.yaml", ErrPlacementPolicyAmbiguous},
		{"ambiguous-duplicate-backend.yaml", ErrPlacementPolicyAmbiguous},

		{"unresolvable-shadowed-rule.yaml", ErrPlacementPolicyUnresolvable},
	}
	for _, tc := range cases {
		t.Run(tc.fixture, func(t *testing.T) {
			raw, path := loadPlacementPolicyFixture(t, tc.fixture)
			policy, err := ParsePlacementPolicy(raw, path)
			if err == nil {
				t.Fatalf("ParsePlacementPolicy(%s) loaded a policy that must refuse: %+v", tc.fixture, policy)
			}
			if !errors.Is(err, tc.want) {
				t.Fatalf("ParsePlacementPolicy(%s) error = %v, want %v", tc.fixture, err, tc.want)
			}
		})
	}
}

// The expiring_capacity refusal names where capacity expiry does live. A
// refusal that only said "unknown key" would leave the next author to guess.
func TestExpiringCapacityRefusalNamesItsRealHome(t *testing.T) {
	raw, path := loadPlacementPolicyFixture(t, "unsupported-prefer-expiring-capacity.yaml")
	_, err := ParsePlacementPolicy(raw, path)
	if err == nil {
		t.Fatal("expiring_capacity loaded")
	}
	for _, want := range []string{"expiring_capacity", "backend declarations", "dispatch"} {
		if !strings.Contains(err.Error(), want) {
			t.Errorf("refusal %q does not mention %q", err.Error(), want)
		}
	}
}

// Resolution is a separate refusal from parsing: the body is well-formed and
// still binds nothing here.
func TestPlacementPolicyResolveRefusesUnbindableDeclarations(t *testing.T) {
	passes := []string{"fixture-build", "fixture-review"}
	backends := []string{"fixture-alpha", "fixture-beta"}

	if err := parsePlacementPolicyFixture(t, "valid.yaml").Resolve(passes, backends); err != nil {
		t.Fatalf("Resolve(accepted fixture) error = %v", err)
	}
	for _, fixture := range []string{"unresolvable-backend.yaml", "unresolvable-pass.yaml", "unresolvable-objective-pass.yaml"} {
		t.Run(fixture, func(t *testing.T) {
			err := parsePlacementPolicyFixture(t, fixture).Resolve(passes, backends)
			if !errors.Is(err, ErrPlacementPolicyUnresolvable) {
				t.Fatalf("Resolve(%s) error = %v, want %v", fixture, err, ErrPlacementPolicyUnresolvable)
			}
		})
	}
	policy := parsePlacementPolicyFixture(t, "valid.yaml")
	if err := policy.Resolve(nil, backends); !errors.Is(err, ErrPlacementPolicyUnresolvable) {
		t.Errorf("Resolve(no passes) error = %v, want a refusal: resolving against nothing accepts everything", err)
	}
	if err := policy.Resolve(passes, nil); !errors.Is(err, ErrPlacementPolicyUnresolvable) {
		t.Errorf("Resolve(no backends) error = %v, want a refusal", err)
	}
}

// An objective is resolved from the policy or refused. It is never defaulted by
// the code, which is the whole content of clause objectives-bind-per-pass.
func TestObjectiveForResolvesRowThenFallbackAndNeverGuesses(t *testing.T) {
	policy := parsePlacementPolicyFixture(t, "valid.yaml")

	got, err := policy.ObjectiveFor("fixture-review")
	if err != nil || got != ObjectiveHighestQuality {
		t.Errorf("ObjectiveFor(fixture-review) = (%q, %v), want (%q, nil)", got, err, ObjectiveHighestQuality)
	}
	got, err = policy.ObjectiveFor("fixture-build")
	if err != nil || got != ObjectiveDefault {
		t.Errorf("ObjectiveFor(fixture-build) = (%q, %v), want the declared fallback %q", got, err, ObjectiveDefault)
	}
	if _, err := policy.ObjectiveFor(""); !errors.Is(err, ErrPlacementPolicyAbsent) {
		t.Errorf("ObjectiveFor(\"\") error = %v, want %v", err, ErrPlacementPolicyAbsent)
	}

	// With the fallback stripped after parsing, a pass with no row has no
	// objective at all — and the answer is a refusal, not the default one.
	policy.Objectives.Fallback = ""
	if _, err := policy.ObjectiveFor("fixture-build"); !errors.Is(err, ErrPlacementPolicyAbsent) {
		t.Errorf("ObjectiveFor with no fallback error = %v, want %v", err, ErrPlacementPolicyAbsent)
	}

	// Every objective the table accepts is declarable, and nothing else is.
	for _, objective := range AcceptedObjectives() {
		candidate := PlacementObjectives{Fallback: objective}
		if err := candidate.Validate(); err != nil {
			t.Errorf("accepted objective %q is not declarable as a fallback: %v", objective, err)
		}
	}
}

// First full match wins in declared order, and a restricted rule is only that
// run's first match when the restriction actually holds.
func TestRuleForHonorsFirstFullMatch(t *testing.T) {
	policy := parsePlacementPolicyFixture(t, "valid.yaml")

	rule, ok := policy.RuleFor("fixture-review", true)
	if !ok || rule.ID != "fixture-gating-review" {
		t.Errorf("RuleFor(fixture-review, gating) = (%s, %v), want fixture-gating-review", rule.ID, ok)
	}
	rule, ok = policy.RuleFor("fixture-review", false)
	if !ok || rule.ID != "fixture-review-quality" {
		t.Errorf("RuleFor(fixture-review, non-gating) = (%s, %v), want fixture-review-quality", rule.ID, ok)
	}
	rule, ok = policy.RuleFor("fixture-build", false)
	if !ok || rule.ID != "fixture-build-backends" {
		t.Errorf("RuleFor(fixture-build) = (%s, %v), want fixture-build-backends", rule.ID, ok)
	}
	if _, ok := policy.RuleFor("fixture-unmatched", false); ok {
		t.Error("an unmatched pass matched a rule; a pass with no rule keeps the declaration-rank fallback")
	}
}

// The ladder is the only thing that orients effort siblings, so it must place
// every graded effort and never place the ungraded one.
func TestEffortRankPlacesEveryGradedEffortAndNothingElse(t *testing.T) {
	policy := parsePlacementPolicyFixture(t, "valid.yaml")

	previous := -1
	for _, effort := range PlacementEffortDomain() {
		rank, placed := policy.EffortRank(effort)
		if effort.IsGraded() {
			if !placed {
				t.Fatalf("graded effort %q is not placed by the declared ladder", effort)
			}
			if rank <= previous {
				t.Fatalf("graded effort %q ranks %d, not above the previous rung %d", effort, rank, previous)
			}
			previous = rank
			continue
		}
		if placed {
			t.Errorf("ungraded effort %q was placed at rank %d", effort, rank)
		}
	}
}

// The staleness boundary is interpreted in exactly one place, and both
// boundaries are exercised: a boundary nobody tests is a boundary nobody knows.
func TestStalenessBoundaryIsInterpretedOnce(t *testing.T) {
	inclusive := StalenessPolicy{Metric: StalenessMetricLedgerSeqLag, Unit: StalenessUnitRecords, MaxLag: 10, Boundary: StalenessBoundaryInclusive}
	exclusive := inclusive
	exclusive.Boundary = StalenessBoundaryExclusive
	for _, policy := range []StalenessPolicy{inclusive, exclusive} {
		if err := policy.Validate(); err != nil {
			t.Fatalf("Validate(%+v) error = %v", policy, err)
		}
	}
	if !inclusive.Fresh(10) {
		t.Error("an inclusive bound calls lag == max_lag stale")
	}
	if exclusive.Fresh(10) {
		t.Error("an exclusive bound calls lag == max_lag fresh")
	}
	if !exclusive.Fresh(9) || inclusive.Fresh(11) {
		t.Error("the boundary does not separate 9, 10 and 11 as declared")
	}
}

// Thresholds are integers so the digest is exact; the ratio accessors are the
// only place they become floats, and they never move the number.
func TestComparatorThresholdsAreExactBasisPoints(t *testing.T) {
	policy := parsePlacementPolicyFixture(t, "valid.yaml")
	comparator := policy.Comparator

	if got := comparator.LatencyWorseRatio(); got != 1.25 {
		t.Errorf("LatencyWorseRatio() = %v, want 1.25", got)
	}
	if got := comparator.CostWorseRatio(); got != 1.25 {
		t.Errorf("CostWorseRatio() = %v, want 1.25", got)
	}
	if got := comparator.AdverseCompletionWorseDelta(); got != 0.05 {
		t.Errorf("AdverseCompletionWorseDelta() = %v, want 0.05", got)
	}
	if got := comparator.QualityAdvantageDelta(); got != 0.02 {
		t.Errorf("QualityAdvantageDelta() = %v, want 0.02", got)
	}
	for _, invalid := range []DemotionComparator{
		{ID: "", LatencyWorseRatioBP: 12500, CostWorseRatioBP: 12500, AdverseCompletionWorseDeltaBP: 500, QualityAdvantageDeltaBP: 200},
		{ID: "x", LatencyWorseRatioBP: 9999, CostWorseRatioBP: 12500, AdverseCompletionWorseDeltaBP: 500, QualityAdvantageDeltaBP: 200},
		{ID: "x", LatencyWorseRatioBP: 12500, CostWorseRatioBP: 12500, AdverseCompletionWorseDeltaBP: 0, QualityAdvantageDeltaBP: 200},
	} {
		if err := invalid.Validate(); err == nil {
			t.Errorf("Validate(%+v) accepted an out-of-domain comparator", invalid)
		}
	}
}

// The digest commits to the declarations, so a changed threshold changes the
// identity and a re-read of the same body does not.
func TestPlacementPolicyDigestIsStableAndSensitive(t *testing.T) {
	first := parsePlacementPolicyFixture(t, "valid.yaml")
	second := parsePlacementPolicyFixture(t, "valid.yaml")

	firstDigest, err := first.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	secondDigest, err := second.Digest()
	if err != nil {
		t.Fatalf("Digest() error = %v", err)
	}
	if firstDigest != secondDigest {
		t.Fatalf("two reads of one body digest differently: %s vs %s", firstDigest, secondDigest)
	}
	if len(firstDigest) != 64 {
		t.Fatalf("digest %q is not a 64-character hex digest", firstDigest)
	}

	for _, mutate := range []func(*PlacementPolicy){
		func(p *PlacementPolicy) { p.Comparator.LatencyWorseRatioBP = 13000 },
		func(p *PlacementPolicy) { p.Staleness.MaxLag = 4999 },
		func(p *PlacementPolicy) { p.Objectives.Fallback = ObjectiveCheapestAcceptable },
		func(p *PlacementPolicy) { p.MinSamples = 21 },
		func(p *PlacementPolicy) { p.TelemetryInfluence = TelemetryInfluencePreferOnly },
		func(p *PlacementPolicy) {
			p.EffortOrder = []Effort{EffortMax, EffortXHigh, EffortHigh, EffortMedium, EffortLow}
		},
	} {
		mutated := parsePlacementPolicyFixture(t, "valid.yaml")
		mutate(&mutated)
		digest, err := mutated.Digest()
		if err != nil {
			t.Fatalf("Digest() after mutation error = %v", err)
		}
		if digest == firstDigest {
			t.Error("a changed declaration left the policy digest unchanged")
		}
	}
}

// A policy that fails validation has no identity: the digest is refused rather
// than taken over declarations nobody may rely on.
func TestPlacementPolicyDigestRefusesAnInvalidPolicy(t *testing.T) {
	policy := parsePlacementPolicyFixture(t, "valid.yaml")
	policy.EffortOrder = []Effort{EffortLow}
	if _, err := policy.Digest(); !errors.Is(err, ErrPlacementPolicyIncomplete) {
		t.Fatalf("Digest() over an incomplete ladder error = %v, want %v", err, ErrPlacementPolicyIncomplete)
	}
}

// The repository's own policy is the one that has to load. This is the
// shipped-value assertion: the delegated Principal declarations this delivery
// ships are read back exactly.
func TestRepositorySchedulerPolicyDeclaresTheShippedPlacementValues(t *testing.T) {
	path := filepath.Join("..", "..", "policy", "scheduler.yaml")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read repository scheduler policy: %v", err)
	}
	policy, err := ParsePlacementPolicy(raw, path)
	if err != nil {
		t.Fatalf("the repository scheduler policy does not load: %v", err)
	}
	if policy.Objectives.Fallback != ObjectiveDefault {
		t.Errorf("shipped objective fallback = %q, want %q", policy.Objectives.Fallback, ObjectiveDefault)
	}
	for pass, want := range map[string]Objective{
		"review":             ObjectiveHighestQuality,
		"design-convergence": ObjectiveHighestQuality,
		"build":              ObjectiveDefault,
		"verification":       ObjectiveDefault,
	} {
		got, err := policy.ObjectiveFor(pass)
		if err != nil {
			t.Errorf("ObjectiveFor(%s) error = %v", pass, err)
			continue
		}
		if got != want {
			t.Errorf("shipped objective for %s = %q, want %q", pass, got, want)
		}
	}
	if policy.Comparator.LatencyWorseRatioBP != 12500 || policy.Comparator.CostWorseRatioBP != 12500 ||
		policy.Comparator.AdverseCompletionWorseDeltaBP != 500 || policy.Comparator.QualityAdvantageDeltaBP != 200 {
		t.Errorf("shipped comparator = %+v", policy.Comparator)
	}
	if policy.Staleness.MaxLag != 5000 || policy.Staleness.Boundary != StalenessBoundaryInclusive ||
		policy.Staleness.Metric != StalenessMetricLedgerSeqLag || policy.Staleness.Unit != StalenessUnitRecords {
		t.Errorf("shipped staleness = %+v", policy.Staleness)
	}
	if policy.MinSamples != 20 {
		t.Errorf("shipped min_samples = %d, want 20", policy.MinSamples)
	}
	// This packet declares the surface; activation is a later packet's change.
	if policy.TelemetryInfluence != TelemetryInfluenceNone {
		t.Errorf("shipped telemetry influence = %q, want %q until activation", policy.TelemetryInfluence, TelemetryInfluenceNone)
	}
}

// The decorative rule is gone, and its keys cannot come back by another name.
func TestRepositoryPolicyCarriesNoDecorativeCapacityRule(t *testing.T) {
	path := filepath.Join("..", "..", "policy", "scheduler.yaml")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read repository scheduler policy: %v", err)
	}
	policy, err := ParsePlacementPolicy(raw, path)
	if err != nil {
		t.Fatalf("the repository scheduler policy does not load: %v", err)
	}
	for _, rule := range policy.Rules {
		if rule.ID == "harvest-expiring-first" {
			t.Fatal("the decorative harvest-expiring-first rule is still declared")
		}
		if !rule.Operative() {
			t.Errorf("rule %s neither prefers nor requires anything", rule.ID)
		}
	}
	// The parser is what makes the removal durable: a policy that reintroduces
	// the shape refuses rather than loading it as decoration.
	reintroduced := strings.Replace(string(raw), "placement_rules:", "placement_rules:\n"+
		"  - id: harvest-expiring-first\n"+
		"    match: {pass: build}\n"+
		"    prefer: {expiring_capacity: true}", 1)
	if _, err := ParsePlacementPolicy([]byte(reintroduced), path); !errors.Is(err, ErrPlacementPolicyUnsupported) {
		t.Fatalf("reintroducing expiring_capacity error = %v, want %v", err, ErrPlacementPolicyUnsupported)
	}
}

