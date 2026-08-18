package driver

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"sort"
	"strings"

	"github.com/halbritt/striatum-next/internal/derived"
	"github.com/halbritt/striatum-next/internal/scheduler"
)

// This file is the placement-policy LOAD seam: the one place the declarations
// under policy/scheduler.yaml become a validated, resolved, digest-pinned
// object, and the one place a policy that cannot be read refuses instead of
// degrading.
//
// "Refuses to load" is meant literally. The loader returns an error and no
// policy; there is no partially-read policy, no dropped rule, and no defaulted
// declaration. Every downstream consumer of placement — the preference
// projection, the freshness predicate, the applicable-prior view, the
// comparator, and the live binding seam — reads the object this function
// returns, so a refusal here is a refusal everywhere, which is exactly the
// property the retired decorative rule did not have.
//
// Two environment reads happen alongside the policy body, and both are refusals
// rather than warnings:
//
//   - The RESOLUTION environment. Cataloged pass ids and placeable backend ids
//     are supplied by the caller, and every operative declaration must resolve
//     against them. A rule preferring a backend this repository cannot place is
//     text that binds nothing.
//   - The REPOSITORY POLICY. The build contract declares `policies: [repository]`
//     as a read, and this delivery is designed against that policy in its
//     accepted placeholder state. A repository policy that has been filled in
//     may relax or restrict placement in ways nothing here has been designed to
//     honor, so a non-placeholder repository policy refuses the load rather than
//     being read past. Fail-closed is the only honest posture: the alternative
//     is placing lanes under a governing policy the placement path silently
//     ignored.

// RepositoryPolicyPlaceholderStatus is the accepted repository-policy status
// this delivery is designed against.
const RepositoryPolicyPlaceholderStatus = "placeholder"

var (
	// ErrRepositoryPolicyNotPlaceholder means the repository policy has left the
	// placeholder state this delivery was designed against.
	ErrRepositoryPolicyNotPlaceholder = errors.New("driver: repository policy is not the accepted placeholder")
	// ErrRepositoryPolicyUnreadable means the repository policy could not be
	// read or does not identify itself.
	ErrRepositoryPolicyUnreadable = errors.New("driver: repository policy is unreadable")
)

// PlacementPolicyEnvironment names every file and fact one placement-policy load
// resolves against. It is explicit rather than derived from a repo root so a
// caller can never load the policy against one repository's catalog and another
// repository's backends.
type PlacementPolicyEnvironment struct {
	// SchedulerPolicyPath is the canonical scheduler policy body.
	SchedulerPolicyPath string
	// RepositoryPolicyPath is the governing repository policy this pass
	// declares as an environment read.
	RepositoryPolicyPath string
	// PassIDs are the cataloged pass ids operative declarations must resolve
	// against.
	PassIDs []string
	// BackendIDs are the placeable backend ids a backends preference must
	// resolve against.
	BackendIDs []string
	// ReadFile is how the SCHEDULER policy body is read. It is nil in every
	// production caller and defaults to os.ReadFile; it exists so a test can
	// observe how many times one load opens that path, which is the only way to
	// hold the single-read property below from outside the package.
	ReadFile func(path string) ([]byte, error)
}

// readFile is the environment's reader, defaulted.
func (env PlacementPolicyEnvironment) readFile(path string) ([]byte, error) {
	if env.ReadFile != nil {
		return env.ReadFile(path)
	}
	return os.ReadFile(path)
}

// LoadedPlacementPolicy is one exact load: the validated declarations, the
// content identity of the surface, and the pin of the body they were read from.
type LoadedPlacementPolicy struct {
	Policy derived.PlacementPolicy
	// Digest is the placement-surface identity a scheduling decision pins. It
	// is taken over the parsed declarations rather than the file bytes, so a
	// comment edit does not invalidate a pinned decision while a changed
	// threshold does.
	Digest string
	// Pin is the scheduler policy body pin, unchanged: the durable identity of
	// the exact bytes Policy and Digest were derived from. It is derived from
	// those bytes, never from a second read of the path.
	Pin scheduler.SchedulerPolicyPin
	// Body is exactly the bytes Policy, Digest, and Pin were derived from, for
	// persistence in the Graph Store. Hashing Body always reproduces Pin.BodyHash.
	Body []byte
}

// LoadPlacementPolicy reads, validates, and resolves the placement surface of
// the canonical scheduler policy. It returns no policy on any refusal.
func LoadPlacementPolicy(env PlacementPolicyEnvironment) (LoadedPlacementPolicy, error) {
	if env.SchedulerPolicyPath == "" {
		return LoadedPlacementPolicy{}, fmt.Errorf("%w: no scheduler policy path was supplied", derived.ErrPlacementPolicyAbsent)
	}
	if env.RepositoryPolicyPath == "" {
		return LoadedPlacementPolicy{}, fmt.Errorf("%w: no repository policy path was supplied", ErrRepositoryPolicyUnreadable)
	}
	if err := RequirePlaceholderRepositoryPolicy(env.RepositoryPolicyPath); err != nil {
		return LoadedPlacementPolicy{}, err
	}
	// ONE read. Every value this function returns — the declarations, the
	// surface digest, the policy pin, and the persisted body — is derived from
	// this exact byte slice. Reading the path a second time to obtain the pin
	// would leave a window in which the file changes between the reads, and the
	// returned object would then carry body A's objective under body B's content
	// hash: a content-addressed pin naming bytes that never declared what the
	// scheduler went on to place under, which is exactly the binding
	// objectives-bind-per-pass and D0005.C2 require to be exact.
	raw, err := env.readFile(env.SchedulerPolicyPath)
	if err != nil {
		return LoadedPlacementPolicy{}, err
	}
	body := append([]byte(nil), raw...)
	policy, err := derived.ParsePlacementPolicy(body, env.SchedulerPolicyPath)
	if err != nil {
		return LoadedPlacementPolicy{}, err
	}
	if err := policy.Resolve(env.PassIDs, env.BackendIDs); err != nil {
		return LoadedPlacementPolicy{}, fmt.Errorf("placement policy: %s: %w", env.SchedulerPolicyPath, err)
	}
	digest, err := policy.Digest()
	if err != nil {
		return LoadedPlacementPolicy{}, err
	}
	pin, _, err := SchedulerPolicyFromBody(env.SchedulerPolicyPath, body)
	if err != nil {
		return LoadedPlacementPolicy{}, err
	}
	return LoadedPlacementPolicy{Policy: policy, Digest: digest, Pin: pin, Body: body}, nil
}

// RequirePlaceholderRepositoryPolicy refuses unless the repository policy is the
// accepted placeholder this delivery is designed against.
//
// The check is deliberately narrow: it reads the identity and the status and
// nothing else. Interpreting a filled-in repository policy is a design this
// repository has not accepted, and guessing at one here would be the placement
// path deciding what a governing policy means.
func RequirePlaceholderRepositoryPolicy(path string) error {
	raw, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("%w: %s: %v", ErrRepositoryPolicyUnreadable, path, err)
	}
	doc := yamlDoc{raw: raw, lines: strings.Split(string(raw), "\n")}
	id := doc.value("id")
	status := doc.value("status")
	if id == "" || status == "" {
		return fmt.Errorf("%w: %s declares id %q and status %q", ErrRepositoryPolicyUnreadable, path, id, status)
	}
	if id != "repository" {
		return fmt.Errorf("%w: %s declares id %q, not \"repository\"", ErrRepositoryPolicyUnreadable, path, id)
	}
	if status != RepositoryPolicyPlaceholderStatus {
		return fmt.Errorf("%w: %s declares status %q; placement is designed against the %q policy and refuses to place lanes under a governing policy it cannot honor",
			ErrRepositoryPolicyNotPlaceholder, path, status, RepositoryPolicyPlaceholderStatus)
	}
	return nil
}

// PlacementPolicyEnvironmentFor assembles the resolution environment from an
// already-loaded catalog and backend declaration set — the two things the
// Driver has in hand at the point it opens a session.
func PlacementPolicyEnvironmentFor(schedulerPolicyPath, repositoryPolicyPath string, catalog Catalog, declarations []scheduler.Declaration) PlacementPolicyEnvironment {
	passIDs := make([]string, 0, len(catalog.Passes))
	for id := range catalog.Passes {
		passIDs = append(passIDs, id)
	}
	sort.Strings(passIDs)
	backendIDs := make([]string, 0, len(declarations))
	for _, declaration := range declarations {
		backendIDs = append(backendIDs, declaration.BackendID)
	}
	sort.Strings(backendIDs)
	return PlacementPolicyEnvironment{
		SchedulerPolicyPath:  schedulerPolicyPath,
		RepositoryPolicyPath: repositoryPolicyPath,
		PassIDs:              passIDs,
		BackendIDs:           backendIDs,
	}
}

// PlacementPolicyBodyHash is the content hash of a scheduler policy body, the
// same value LoadSchedulerPolicy pins. It is exported here so a caller holding
// only bytes can prove a loaded surface came from the body it expects.
func PlacementPolicyBodyHash(body []byte) string {
	sum := sha256.Sum256(body)
	return hex.EncodeToString(sum[:])
}

