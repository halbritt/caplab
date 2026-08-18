package driver

import (
	"strings"
	"time"

	"github.com/halbritt/striatum-next/internal/records"
	"github.com/halbritt/striatum-next/internal/store"
)

// State is the driver's re-fold of the ledger: everything the loop decides
// against. It is derived, destroyable, and rebuilt at every session.
type State struct {
	Requests      map[uint64]*RequestState
	Runs          map[uint64]*RunState
	Identities    map[string]*IdentityState
	GateResults   map[gateKey][]GateResultState
	Escalations   map[uint64]*EscalationState
	Drained       map[string]bool
	MarkedWaves   map[uint64]bool
	Plans         map[uint64]*PlanState
	HeadMovements []HeadMovementState
	Flakes        map[string]bool
	Applications  []ApplicationState
	Winners       map[string]uint64
	LastSeq       uint64
}

// ApplicationState is one application_record: a change set bound into
// product lineage.
type ApplicationState struct {
	Seq            uint64
	ChangeSetHash  string
	LinkedTreeHash string
	ProductID      string
}

// HeadMovementState is one recorded head movement, for the mark phase.
type HeadMovementState struct {
	Seq      uint64
	Identity string
	Movement string
	From     uint64
	To       uint64
}

type gateKey struct {
	Identity string
	Version  uint64
	GateID   string
}

// RequestState is one compilation request's authority events.
type RequestState struct {
	Seq       uint64
	Subject   string
	Principal string
	Note      string
	TargetID  string
	TargetVer int
	// DelegationRef marks an agent-issued request (RFC 0006 delegation);
	// WrittenAt supports issuance cadence accounting.
	DelegationRef string
	WrittenAt     string
	// IssuerKind is the folded issuer.kind — "planner" distinguishes a
	// planner-scheduled request from a Principal- or agent-issued one
	// everywhere the driver reads folds (C9). A record predating the marker
	// folds as its recorded kind; an absent kind folds as principal-issued —
	// no retroactive migration, ever (C13).
	IssuerKind string
	Satisfied  bool
	// SatisfactionLevel is the claim level the satisfaction earned from its
	// conjunct evidence (Verified/Asserted/Designed) — a floor-only satisfaction
	// is Asserted, never a bare Verified (D0005.C5 on the satisfaction surface).
	SatisfactionLevel string
	Canceled          bool
}

// RunState is one pass run and its closures.
type RunState struct {
	Seq           uint64
	PassID        string
	StepID        string
	Subject       string
	RequestRef    uint64
	PlanRef       uint64
	DeadlineClass string
	ManifestHash  string
	Manifest      map[string]any
	OpenedAt      time.Time
	Closures      []string

	// Lane binding facts (from lane_binding records): the ledger-derived
	// basis for in-flight accounting (D0013.C6) and courtesy aborts.
	BackendID  string
	DispatchID string
	LaneID     string
}

// Open reports whether the run has no closure.
func (r *RunState) Open() bool {
	return len(r.Closures) == 0
}

// IdentityState folds one artifact identity: versions, head, staleness.
type IdentityState struct {
	ID       string
	Kind     string
	Role     string
	Versions map[uint64]*VersionState
	Order    []uint64
	Head     uint64
}

// VersionState is one admitted artifact version.
type VersionState struct {
	Seq            uint64
	ContentHash    string
	Kind           string
	Lifecycle      string
	ProducedByRun  uint64
	ProductionMode string
	Anchors        map[string]string
	RetiredAnchors []store.RetiredAnchor
	DerivedFrom    []store.Pin
	ConstrainedBy  []store.Pin
	BodyAddress    string
	Stale          bool

	// Evidence mirror: review-ledger versions carry their subject pin and
	// verdict in the admitted record's evidences edge, so gate and re-stamp
	// folds never open bodies.
	ReviewVerdict         string
	ReviewSubjectIdentity string
	ReviewSubjectVersion  uint64
	ReviewSubjectHash     string

	// Foreign-head mirror: a Foreign Head Attestation (an Exogenous Change
	// Record, D0014.C2) carries the attested foreign accepted head in its
	// evidences edge — subject = the foreign head, claim = "foreign_head:<hash>".
	// Mirrored here so cross-repository pin freshness reads a local head plus a
	// hash comparison, never a foreign graph and never a body (D0014.C3).
	ForeignContentHash string

	// SessionNonce, BackendID, and AliasingClass mirror the producing
	// lane's admitted attribution — what independence evaluation reads.
	SessionNonce  string
	BackendID     string
	AliasingClass string
}

// GateResultState is one recorded gate result.
type GateResultState struct {
	Seq     uint64
	GateID  string
	Class   string
	Outcome string
	Verdict string
	Detail  string
}

// EscalationState is one escalation and its resolution state.
type EscalationState struct {
	Seq           uint64
	Reason        string
	Detail        string
	BlockingScope string
	RunRef        uint64
	Resolved      bool
	Disposition   string
}

// PlanState is the latest plan appended for a request.
type PlanState struct {
	Seq         uint64
	ContentHash string
}

// Fold rebuilds driver state from decoded ledger records.
func Fold(all []records.DecodedRecord) *State {
	state := NewState()
	state.Apply(all)
	return state
}

// NewState returns an empty fold state.
func NewState() *State {
	return &State{
		Requests:    map[uint64]*RequestState{},
		Runs:        map[uint64]*RunState{},
		Identities:  map[string]*IdentityState{},
		GateResults: map[gateKey][]GateResultState{},
		Escalations: map[uint64]*EscalationState{},
		Drained:     map[string]bool{},
		MarkedWaves: map[uint64]bool{},
		Plans:       map[uint64]*PlanState{},
		Flakes:      map[string]bool{},
		Winners:     map[string]uint64{},
	}
}

// Apply folds records appended after those already applied. Folding a ledger
// incrementally — any prefix, then any suffix — is equivalent to folding it
// whole: Apply is the single per-record loop Fold itself runs, and the
// fold-equivalence guard holds that invariant against drift.
func (state *State) Apply(all []records.DecodedRecord) {
	for _, record := range all {
		state.LastSeq = record.Seq
		payload := record.Payload
		switch record.Type {
		case "compilation_request":
			subject, _ := payload["subject"].(map[string]any)
			target, _ := payload["target"].(map[string]any)
			issuer, _ := payload["issuer"].(map[string]any)
			issuerKind := str(issuer, "kind")
			if issuerKind == "" {
				// A record predating the issuer.kind marker folds as
				// principal-issued — no retroactive migration (C13).
				issuerKind = "principal"
			}
			state.Requests[record.Seq] = &RequestState{
				Seq:           record.Seq,
				Subject:       str(subject, "identity"),
				Principal:     str(issuer, "identity"),
				Note:          str(payload, "note"),
				TargetID:      str(target, "state_id"),
				TargetVer:     intOf(target, "predicate_version"),
				DelegationRef: str(issuer, "delegation_ref"),
				IssuerKind:    issuerKind,
				WrittenAt:     record.WrittenAt,
			}
		case "cancellation_record":
			if request, ok := state.Requests[num(payload, "request_ref")]; ok {
				request.Canceled = true
			}
		case "satisfaction_record":
			if request, ok := state.Requests[num(payload, "request_ref")]; ok {
				request.Satisfied = true
				request.SatisfactionLevel = str(payload, "claim_level")
			}
		case "plan_record":
			state.Plans[num(payload, "request_ref")] = &PlanState{
				Seq:         record.Seq,
				ContentHash: str(payload, "content_hash"),
			}
		case "pass_run_opened":
			run := &RunState{
				Seq:           record.Seq,
				PassID:        str(payload, "pass_id"),
				RequestRef:    num(payload, "request_ref"),
				PlanRef:       num(payload, "plan_ref"),
				DeadlineClass: str(payload, "deadline_class"),
			}
			if manifest, ok := payload["manifest"].(map[string]any); ok {
				run.Manifest = manifest
				run.StepID = str(manifest, "step_id")
				run.Subject = str(manifest, "subject")
				if hash, err := store.RunManifestHash(manifest); err == nil {
					run.ManifestHash = hash
				}
			}
			if at, err := time.Parse("2006-01-02T15:04:05.000Z", record.WrittenAt); err == nil {
				run.OpenedAt = at
			}
			state.Runs[record.Seq] = run
		case "pass_run_closed":
			if run, ok := state.Runs[num(payload, "run_ref")]; ok {
				run.Closures = append(run.Closures, str(payload, "outcome"))
			}
		case "admission_decision":
			state.foldAdmissionDecision(payload)
		case "lane_binding":
			if run, ok := state.Runs[num(payload, "run_ref")]; ok {
				run.BackendID = str(payload, "backend_id")
				run.DispatchID = str(payload, "dispatch_id")
				run.LaneID = str(payload, "lane_id")
			}
		case "artifact_admitted":
			state.foldArtifact(record)
		case "head_movement":
			identity := state.identity(str(payload, "identity"))
			movement := str(payload, "movement")
			state.HeadMovements = append(state.HeadMovements, HeadMovementState{
				Seq:      record.Seq,
				Identity: identity.ID,
				Movement: movement,
				From:     num(payload, "from_version"),
				To:       num(payload, "to_version"),
			})
			if movement == "retire" {
				identity.Head = 0
				continue
			}
			identity.Head = num(payload, "to_version")
		case "gate_result":
			subject, _ := payload["subject"].(map[string]any)
			key := gateKey{
				Identity: str(subject, "identity"),
				Version:  num(subject, "version_seq"),
				GateID:   str(payload, "gate_id"),
			}
			detail := str(payload, "detail")
			if detail == "" {
				// Acceptance verdicts written by the accept/reject verbs
				// carry their adjudication text as "reason"; a rejection's
				// reason is the revision lane's only steer, so it must fold.
				detail = str(payload, "reason")
			}
			state.GateResults[key] = append(state.GateResults[key], GateResultState{
				Seq:     record.Seq,
				GateID:  key.GateID,
				Class:   str(payload, "gate_class"),
				Outcome: str(payload, "outcome"),
				Verdict: str(payload, "verdict"),
				Detail:  detail,
			})
		case "staleness_event":
			state.MarkedWaves[num(payload, "wave")] = true
			subjects, _ := payload["subjects"].([]any)
			for _, entry := range subjects {
				subject, _ := entry.(map[string]any)
				pin, _ := subject["pin"].(map[string]any)
				identity := state.identity(str(pin, "identity"))
				if version, ok := identity.Versions[num(pin, "version_seq")]; ok {
					version.Stale = true
				}
			}
		case "escalation":
			state.Escalations[record.Seq] = &EscalationState{
				Seq:           record.Seq,
				Reason:        str(payload, "reason"),
				Detail:        str(payload, "detail"),
				BlockingScope: str(payload, "blocking_scope"),
				RunRef:        num(payload, "run_ref"),
			}
		case "resolution_event":
			if escalation, ok := state.Escalations[num(payload, "escalation_ref")]; ok {
				escalation.Resolved = true
				if disposition, ok := payload["disposition"].(map[string]any); ok {
					escalation.Disposition = str(disposition, "action")
				}
			}
		case "submission_received", "submission_refused":
			state.Drained[str(payload, "dispatch_id")] = true
			if record.Type == "submission_refused" {
				// A refused submission (a redundant or superseded loser under
				// the winner rule, D0010.C2) is terminal: no pass_run_closed
				// follows, so the run must close here or it hangs Open() — and
				// with it the drive's quiescence — forever.
				if run, ok := state.Runs[num(payload, "run_ref")]; ok {
					run.Closures = append(run.Closures, "refused")
				}
			}
		case "check_flake":
			// A standing contradiction blocks Verified promotion (RFC 0010 §5.6).
			state.Flakes[str(payload, "check_id")+"\x00"+str(payload, "result_tree_hash")] = true
		case "application_record":
			state.Applications = append(state.Applications, ApplicationState{
				Seq:            record.Seq,
				ChangeSetHash:  str(payload, "change_set_hash"),
				LinkedTreeHash: str(payload, "linked_tree_hash"),
				ProductID:      str(payload, "product_identity"),
			})
		}
	}
}

func (s *State) foldAdmissionDecision(payload map[string]any) {
	if str(payload, "decision") != "admitted" {
		return
	}
	run := s.Runs[num(payload, "run_ref")]
	if run == nil || run.ManifestHash == "" {
		return
	}
	laneID := str(payload, "lane_id")
	if laneID == "" {
		return
	}
	key := winnerKey(run.ManifestHash, laneID)
	if _, exists := s.Winners[key]; !exists {
		s.Winners[key] = num(payload, "admitted_version")
	}
}

func (s *State) foldArtifact(record records.DecodedRecord) {
	payload := record.Payload
	id := str(payload, "identity")
	if id == "" {
		return
	}
	identity := s.identity(id)
	identity.Kind = str(payload, "kind")
	identity.Role = str(payload, "role")

	version := &VersionState{
		Seq:            record.Seq,
		ContentHash:    str(payload, "content_hash"),
		Kind:           identity.Kind,
		Lifecycle:      str(payload, "lifecycle"),
		ProducedByRun:  num(payload, "produced_by_run"),
		ProductionMode: str(payload, "production_mode"),
		Anchors:        map[string]string{},
	}
	if body, ok := payload["body"].(map[string]any); ok {
		version.BodyAddress = str(body, "address")
	}
	if anchors, ok := payload["anchor_map"].([]any); ok {
		for _, entry := range anchors {
			anchor, _ := entry.(map[string]any)
			version.Anchors[str(anchor, "anchor")] = str(anchor, "element_hash")
		}
	}
	if retired, ok := payload["retired_anchors"].([]any); ok {
		for _, entry := range retired {
			anchor, _ := entry.(map[string]any)
			version.RetiredAnchors = append(version.RetiredAnchors, store.RetiredAnchor{
				Anchor: str(anchor, "anchor"),
				Reason: str(anchor, "reason"),
			})
		}
	}
	if attribution, ok := payload["attribution"].(map[string]any); ok {
		version.SessionNonce = str(attribution, "session_nonce")
		version.BackendID = str(attribution, "backend_id")
		version.AliasingClass = str(attribution, "aliasing_class")
	}
	if edges, ok := payload["edges"].(map[string]any); ok {
		version.DerivedFrom = pinsOf(edges, "derived_from")
		version.ConstrainedBy = pinsOf(edges, "constrained_by")
		if evidences, ok := edges["evidences"].([]any); ok && len(evidences) > 0 {
			evidence, _ := evidences[0].(map[string]any)
			subject, _ := evidence["subject"].(map[string]any)
			claim := str(evidence, "claim")
			if verdict, ok := strings.CutPrefix(claim, "verdict:"); ok {
				version.ReviewVerdict = verdict
			}
			if hash, ok := strings.CutPrefix(claim, "foreign_head:"); ok {
				version.ForeignContentHash = hash
			}
			version.ReviewSubjectIdentity = str(subject, "identity")
			version.ReviewSubjectVersion = num(subject, "version_seq")
			version.ReviewSubjectHash = str(subject, "content_hash")
		}
	}
	identity.Versions[record.Seq] = version
	identity.Order = append(identity.Order, record.Seq)
}

func (s *State) identity(id string) *IdentityState {
	if id == "" {
		id = "?"
	}
	identity, ok := s.Identities[id]
	if !ok {
		identity = &IdentityState{ID: id, Versions: map[uint64]*VersionState{}}
		s.Identities[id] = identity
	}
	return identity
}

// GateResultsFor returns the recorded outcomes for one (identity, version,
// gate) key in append order.
func (s *State) GateResultsFor(identity string, version uint64, gateID string) []string {
	var out []string
	for _, result := range s.GateResults[gateKey{Identity: identity, Version: version, GateID: gateID}] {
		out = append(out, result.Outcome)
	}
	return out
}

// HeadVersion returns an identity's accepted head version, if any.
func (s *State) HeadVersion(id string) *VersionState {
	identity, ok := s.Identities[id]
	if !ok || identity.Head == 0 {
		return nil
	}
	return identity.Versions[identity.Head]
}

// PinFresh reports whether a pin still matches the pinned identity's head:
// resolution is hash-first, so a body-identical re-stamp keeps pins fresh.
//
// A cross-repository pin (RepoID set, D0014.C1) resolves against the local
// Foreign Head Attestation stream for (RepoID, Identity) — never a foreign
// graph and never on a live read (D0010.C11 across graphs): it is fresh iff the
// latest locally-admitted attestation for that foreign head reports the pinned
// content hash. A moved foreign head is admitted at planning as a fresh
// attestation reporting a new hash; that head movement decays the stale
// cross-repository pin by the one invalidation algebra (D0014.C3).
func (s *State) PinFresh(pin store.Pin) bool {
	if pin.RepoID != "" {
		attestation := s.HeadVersion(store.ForeignHeadIdentity(pin.RepoID, pin.Identity))
		if attestation == nil {
			return false
		}
		return attestation.ForeignContentHash == pin.ContentHash
	}
	head := s.HeadVersion(pin.Identity)
	if head == nil {
		return false
	}
	return head.ContentHash == pin.ContentHash
}

// FreshnessPins filters a version's input pins to those that participate in
// freshness evaluation. Prior-version self-references, pins onto evidence
// identities, and pins onto gate-refused versions are diagnostic lineage —
// recorded provenance, never freshness inputs: evidence never head-moves, a
// prior version of oneself is permanently superseded by construction, and a
// refused version pinned as a W10 diagnostic input can never become fresh —
// counting it would permanently stale every revision produced from it.
func (s *State) FreshnessPins(identityID string, version *VersionState) []store.Pin {
	var out []store.Pin
	for _, pin := range append(append([]store.Pin{}, version.DerivedFrom...), version.ConstrainedBy...) {
		if pin.Identity == identityID {
			continue
		}
		if pinned, ok := s.Identities[pin.Identity]; ok && pinned.Role == "evidence" {
			continue
		}
		if s.versionRefused(pin.Identity, pin.VersionSeq) {
			continue
		}
		out = append(out, pin)
	}
	return out
}

// versionRefused reports whether any gate's latest result refused the exact
// pinned version.
func (s *State) versionRefused(identity string, versionSeq uint64) bool {
	for key, results := range s.GateResults {
		if key.Identity != identity || key.Version != versionSeq {
			continue
		}
		if latest := latestResult(results); latest != nil && latest.Outcome != "pass" {
			return true
		}
	}
	return false
}

func (s *State) LaneWon(run *RunState) bool {
	if run == nil || run.ManifestHash == "" || run.LaneID == "" {
		return false
	}
	_, ok := s.Winners[winnerKey(run.ManifestHash, run.LaneID)]
	return ok
}

func winnerKey(manifestHash, laneID string) string {
	return manifestHash + "\x00" + laneID
}

func pinsOf(edges map[string]any, key string) []store.Pin {
	list, _ := edges[key].([]any)
	var out []store.Pin
	for _, entry := range list {
		pin, _ := entry.(map[string]any)
		out = append(out, store.Pin{
			RepoID:      str(pin, "repo_id"),
			Identity:    str(pin, "identity"),
			VersionSeq:  num(pin, "version_seq"),
			ContentHash: str(pin, "content_hash"),
			Anchor:      str(pin, "anchor"),
			ElementHash: str(pin, "element_hash"),
		})
	}
	return out
}

func str(payload map[string]any, key string) string {
	if payload == nil {
		return ""
	}
	value, _ := payload[key].(string)
	return value
}

func num(payload map[string]any, key string) uint64 {
	if payload == nil {
		return 0
	}
	value, ok := payload[key].(int64)
	if !ok || value < 0 {
		return 0
	}
	return uint64(value)
}

func intOf(payload map[string]any, key string) int {
	return int(num(payload, key))
}

