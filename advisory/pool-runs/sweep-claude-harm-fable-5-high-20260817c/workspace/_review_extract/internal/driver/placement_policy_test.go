package driver_test

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/halbritt/striatum-next/internal/derived"
	"github.com/halbritt/striatum-next/internal/driver"
)

// The load seam is where a refusal becomes a refusal for every consumer. These
// tests hold two properties: the repository's own environment loads, and a
// policy that cannot bind here returns no policy at all rather than a partial
// one.

func repositoryPath(parts ...string) string {
	return filepath.Join(append([]string{"..", ".."}, parts...)...)
}

func repositoryPlacementEnvironment(t *testing.T) driver.PlacementPolicyEnvironment {
	t.Helper()
	catalog, err := driver.LoadCatalog(repositoryPath("catalog"))
	if err != nil {
		t.Fatalf("load catalog: %v", err)
	}
	declarations, _, err := driver.LoadBackendDeclarations(repositoryPath("backends"))
	if err != nil {
		t.Fatalf("load backend declarations: %v", err)
	}
	return driver.PlacementPolicyEnvironmentFor(
		repositoryPath("policy", "scheduler.yaml"),
		repositoryPath("policy", "repository.yaml"),
		catalog, declarations)
}

// The shipped policy must resolve against the shipped catalog and the shipped
// backends. This is the assertion that keeps the declarations honest: a rule
// preferring a backend nobody places, or naming a pass nobody catalogs, fails
// here rather than at the binding seam.
func TestLoadPlacementPolicyResolvesTheRepositoryEnvironment(t *testing.T) {
	loaded, err := driver.LoadPlacementPolicy(repositoryPlacementEnvironment(t))
	if err != nil {
		t.Fatalf("LoadPlacementPolicy(repository) error = %v", err)
	}
	if len(loaded.Digest) != 64 {
		t.Errorf("placement digest %q is not a 64-character hex digest", loaded.Digest)
	}
	if loaded.Pin.Version <= 0 || len(loaded.Pin.BodyHash) != 64 {
		t.Errorf("scheduler policy pin = %+v", loaded.Pin)
	}
	if got := driver.PlacementPolicyBodyHash(loaded.Body); got != loaded.Pin.BodyHash {
		t.Errorf("body hash %s does not match the pin %s", got, loaded.Pin.BodyHash)
	}
	if len(loaded.Policy.Rules) == 0 {
		t.Fatal("the repository policy loaded with no placement rule")
	}
	for _, rule := range loaded.Policy.Rules {
		if rule.ID == "harvest-expiring-first" {
			t.Error("the decorative harvest rule survived the load")
		}
	}
	// Every cataloged pass resolves an objective, by row or by the declared
	// fallback. That totality is clause objectives-bind-per-pass.
	catalog, err := driver.LoadCatalog(repositoryPath("catalog"))
	if err != nil {
		t.Fatalf("load catalog: %v", err)
	}
	for passID := range catalog.Passes {
		objective, err := loaded.Policy.ObjectiveFor(passID)
		if err != nil {
			t.Errorf("pass %s resolves no placement objective: %v", passID, err)
			continue
		}
		if !derived.ObjectiveAccepted(objective) {
			t.Errorf("pass %s resolves objective %q, which is not accepted", passID, objective)
		}
	}
}

// One load reads the scheduler policy body exactly once, and everything it
// returns comes from those bytes.
//
// The defect this holds shut: a loader that parses the declarations from one
// read and then re-opens the path for the pin can be raced by a writer between
// the two reads, returning body A's objective under body B's content hash. The
// pin would then be content-addressed to bytes that never declared what the
// scheduler placed under, and a decision trace recording that pin would be
// unfalsifiable — replaying it against the pinned body yields a different
// objective. Here the reader hands out a DIFFERENT body on every call after the
// first, so any second read shows up immediately as an inconsistent result.
func TestLoadPlacementPolicyReadsTheSchedulerBodyExactlyOnce(t *testing.T) {
	env := repositoryPlacementEnvironment(t)
	first, err := os.ReadFile(env.SchedulerPolicyPath)
	if err != nil {
		t.Fatalf("read scheduler policy: %v", err)
	}
	// The swapped-in body is a lawful policy that declares a DIFFERENT
	// fallback objective and hashes differently, so pairing either half of it
	// with the original is visible in the result rather than silent.
	swapped := []byte(strings.Replace(string(first), "fallback: default", "fallback: highest-quality", 1))
	if string(swapped) == string(first) {
		t.Fatal("the swapped fixture is identical to the shipped policy; the swap proves nothing")
	}

	reads := 0
	env.ReadFile = func(path string) ([]byte, error) {
		if path != env.SchedulerPolicyPath {
			t.Errorf("unexpected read of %s through the scheduler-policy reader", path)
		}
		reads++
		if reads == 1 {
			return append([]byte(nil), first...), nil
		}
		return append([]byte(nil), swapped...), nil
	}

	loaded, err := driver.LoadPlacementPolicy(env)
	if err != nil {
		t.Fatalf("LoadPlacementPolicy() error = %v", err)
	}
	if reads != 1 {
		t.Fatalf("one load read the scheduler policy %d times; it must read it exactly once", reads)
	}
	// Independent of the read count: the returned pin, body, and declarations
	// must all be the same bytes' story.
	if got := driver.PlacementPolicyBodyHash(loaded.Body); got != loaded.Pin.BodyHash {
		t.Errorf("returned body hashes to %s but the pin says %s", got, loaded.Pin.BodyHash)
	}
	if got := driver.PlacementPolicyBodyHash(first); got != loaded.Pin.BodyHash {
		t.Errorf("the pin %s does not name the body the declarations were parsed from (%s)", loaded.Pin.BodyHash, got)
	}
	reparsed, err := derived.ParsePlacementPolicy(loaded.Body, env.SchedulerPolicyPath)
	if err != nil {
		t.Fatalf("re-parsing the returned body failed: %v", err)
	}
	replayed, err := reparsed.Digest()
	if err != nil {
		t.Fatalf("digest of the re-parsed body: %v", err)
	}
	if replayed != loaded.Digest {
		t.Errorf("re-parsing the pinned body yields digest %s, not the returned %s", replayed, loaded.Digest)
	}
	for _, passID := range []string{"build", "review"} {
		want, err := reparsed.ObjectiveFor(passID)
		if err != nil {
			t.Fatalf("objective for %s from the pinned body: %v", passID, err)
		}
		got, err := loaded.Policy.ObjectiveFor(passID)
		if err != nil {
			t.Fatalf("objective for %s from the loaded policy: %v", passID, err)
		}
		if got != want {
			t.Errorf("pass %s resolves objective %q, but its pinned body declares %q", passID, got, want)
		}
	}
}

// A repository policy that has left the placeholder state refuses the load. The
// placement path is designed against the placeholder and has no accepted way to
// honor a filled-in one; reading past it would place lanes under a governing
// policy nothing here consulted.
func TestLoadPlacementPolicyRefusesANonPlaceholderRepositoryPolicy(t *testing.T) {
	env := repositoryPlacementEnvironment(t)

	accepted := filepath.Join(t.TempDir(), "repository.yaml")
	if err := os.WriteFile(accepted, []byte("id: repository\nkind: policy\nstatus: accepted\n"), 0o644); err != nil {
		t.Fatalf("write repository policy: %v", err)
	}
	env.RepositoryPolicyPath = accepted
	loaded, err := driver.LoadPlacementPolicy(env)
	if !errors.Is(err, driver.ErrRepositoryPolicyNotPlaceholder) {
		t.Fatalf("LoadPlacementPolicy error = %v, want %v", err, driver.ErrRepositoryPolicyNotPlaceholder)
	}
	if len(loaded.Policy.Rules) != 0 || loaded.Digest != "" {
		t.Errorf("a refused load still returned a policy: %+v", loaded)
	}

	env.RepositoryPolicyPath = filepath.Join(t.TempDir(), "absent.yaml")
	if _, err := driver.LoadPlacementPolicy(env); !errors.Is(err, driver.ErrRepositoryPolicyUnreadable) {
		t.Fatalf("LoadPlacementPolicy(absent repository policy) error = %v, want %v", err, driver.ErrRepositoryPolicyUnreadable)
	}

	misidentified := filepath.Join(t.TempDir(), "repository.yaml")
	if err := os.WriteFile(misidentified, []byte("id: scheduler\nstatus: placeholder\n"), 0o644); err != nil {
		t.Fatalf("write repository policy: %v", err)
	}
	env.RepositoryPolicyPath = misidentified
	if _, err := driver.LoadPlacementPolicy(env); !errors.Is(err, driver.ErrRepositoryPolicyUnreadable) {
		t.Fatalf("LoadPlacementPolicy(misidentified policy) error = %v, want %v", err, driver.ErrRepositoryPolicyUnreadable)
	}
}

// The repository's own repository.yaml is the placeholder this delivery was
// designed against. If that ever stops being true, this test is the notice.
func TestRepositoryPolicyIsStillThePlaceholder(t *testing.T) {
	if err := driver.RequirePlaceholderRepositoryPolicy(repositoryPath("policy", "repository.yaml")); err != nil {
		t.Fatalf("repository policy: %v", err)
	}
}

// An unsupported prefer shape refuses the LOAD, not merely the parse: no
// consumer downstream of this function can be handed a policy with the
// offending rule quietly dropped.
func TestLoadPlacementPolicyRefusesUnsupportedShapes(t *testing.T) {
	base, err := os.ReadFile(repositoryPath("policy", "scheduler.yaml"))
	if err != nil {
		t.Fatalf("read scheduler policy: %v", err)
	}
	cases := []struct {
		name       string
		injectRule string
		want       error
	}{
		{
			name: "expiring-capacity",
			injectRule: "  - id: fixture-harvest\n" +
				"    match: {pass: build}\n" +
				"    prefer: {expiring_capacity: true}\n",
			want: derived.ErrPlacementPolicyUnsupported,
		},
		{
			name: "two-shapes",
			injectRule: "  - id: fixture-two-shapes\n" +
				"    match: {pass: build}\n" +
				"    prefer: {backends: [local], quality_profile: highest}\n",
			want: derived.ErrPlacementPolicyAmbiguous,
		},
		{
			name: "run-mode-match",
			injectRule: "  - id: fixture-mode\n" +
				"    match: {pass: build, mode: harvest}\n" +
				"    prefer: {backends: [local]}\n",
			want: derived.ErrPlacementPolicyUnsupported,
		},
		{
			name: "unplaceable-backend",
			injectRule: "  - id: fixture-unplaceable\n" +
				"    match: {pass: observation}\n" +
				"    prefer: {backends: [no-such-backend]}\n",
			want: derived.ErrPlacementPolicyUnresolvable,
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			body := strings.Replace(string(base), "  - id: build-single-agent-coding\n", tc.injectRule+"  - id: build-single-agent-coding\n", 1)
			path := filepath.Join(t.TempDir(), "scheduler.yaml")
			if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
				t.Fatalf("write scheduler policy: %v", err)
			}
			env := repositoryPlacementEnvironment(t)
			env.SchedulerPolicyPath = path
			if _, err := driver.LoadPlacementPolicy(env); !errors.Is(err, tc.want) {
				t.Fatalf("LoadPlacementPolicy error = %v, want %v", err, tc.want)
			}
		})
	}
}

// The pass-scoped preference projection and the placement surface read the same
// file and must agree about which rule answers a pass. A gating-restricted rule
// answers only gating runs, so it never consumes an unrestricted pass's slot.
func TestBackendPreferencesAgreeWithThePlacementSurface(t *testing.T) {
	path := repositoryPath("policy", "scheduler.yaml")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read scheduler policy: %v", err)
	}
	preferences, err := driver.ParseSchedulerBackendPreferences(raw)
	if err != nil {
		t.Fatalf("ParseSchedulerBackendPreferences() error = %v", err)
	}
	policy, err := derived.ParsePlacementPolicy(raw, path)
	if err != nil {
		t.Fatalf("ParsePlacementPolicy() error = %v", err)
	}
	for passID, preference := range preferences {
		rule, ok := policy.RuleFor(passID, false)
		if !ok {
			t.Errorf("pass %s has a backend preference but matches no placement rule", passID)
			continue
		}
		if rule.Prefer.Shape != derived.PreferShapeBackends {
			t.Errorf("pass %s prefers backends in the projection but shape %q in the surface", passID, rule.Prefer.Shape)
			continue
		}
		if len(rule.Prefer.Backends) != len(preference) {
			t.Errorf("pass %s: surface lists %d backends, projection lists %d", passID, len(rule.Prefer.Backends), len(preference))
			continue
		}
		for i, backendID := range rule.Prefer.Backends {
			if preference[i] != backendID {
				t.Errorf("pass %s position %d: surface %s, projection %s", passID, i, backendID, preference[i])
			}
		}
	}
	// The gating restriction is declared ahead of the general review rule and
	// still leaves the general rule's preference intact for ordinary reviews.
	if _, ok := preferences["review"]; !ok {
		t.Error("the review preference was consumed by the gating-restricted rule")
	}
	gating, ok := policy.RuleFor("review", true)
	if !ok || gating.Require.Independence != derived.PlacementIndependenceSubject {
		t.Errorf("a gating review resolves rule %+v, want the independence restriction", gating)
	}
}

