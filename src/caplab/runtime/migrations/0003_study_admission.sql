SELECT pg_advisory_xact_lock(hashtextextended('caplab_v0:study-admission', 0));

CREATE TABLE caplab_v0.study_registrations (
    manifest_sha256 text PRIMARY KEY CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    study_id text NOT NULL UNIQUE,
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    registered_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE caplab_v0.study_objects (
    content_sha256 text PRIMARY KEY CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    object_key text NOT NULL UNIQUE,
    local_copy_key text NOT NULL UNIQUE,
    byte_count bigint NOT NULL CHECK (byte_count > 0)
);

CREATE TABLE caplab_v0.study_evidence_records (
    manifest_sha256 text NOT NULL REFERENCES caplab_v0.study_registrations(manifest_sha256),
    record_id text NOT NULL,
    source_kind text NOT NULL,
    source_commit text CHECK (source_commit IS NULL OR source_commit ~ '^[0-9a-f]{40}$'),
    source_path text NOT NULL,
    content_sha256 text NOT NULL REFERENCES caplab_v0.study_objects(content_sha256),
    media_type text NOT NULL,
    disposition text NOT NULL CHECK (disposition = 'restricted-admission'),
    record_body jsonb NOT NULL CHECK (jsonb_typeof(record_body) = 'object'),
    PRIMARY KEY (manifest_sha256, record_id)
);

CREATE TABLE caplab_v0.study_identity_records (
    manifest_sha256 text NOT NULL REFERENCES caplab_v0.study_registrations(manifest_sha256),
    kind text NOT NULL,
    identity_sha256 text NOT NULL CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    PRIMARY KEY (manifest_sha256, kind),
    UNIQUE (identity_sha256)
);

CREATE TABLE caplab_v0.study_trial_assignments (
    manifest_sha256 text NOT NULL REFERENCES caplab_v0.study_registrations(manifest_sha256),
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    sequence integer NOT NULL CHECK (sequence > 0),
    block text NOT NULL,
    task text NOT NULL,
    condition text NOT NULL,
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    UNIQUE (manifest_sha256, sequence)
);

CREATE TABLE caplab_v0.study_attempts (
    manifest_sha256 text NOT NULL REFERENCES caplab_v0.study_registrations(manifest_sha256),
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    assignment_sha256 text NOT NULL UNIQUE REFERENCES caplab_v0.study_trial_assignments(identity_sha256),
    attempt_number integer NOT NULL CHECK (attempt_number = 1),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object')
);

CREATE TABLE caplab_v0.study_outcomes (
    manifest_sha256 text NOT NULL REFERENCES caplab_v0.study_registrations(manifest_sha256),
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    attempt_sha256 text NOT NULL UNIQUE REFERENCES caplab_v0.study_attempts(identity_sha256),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object')
);

CREATE TRIGGER study_registrations_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.study_registrations
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER study_objects_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.study_objects
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER study_evidence_records_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.study_evidence_records
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER study_identity_records_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.study_identity_records
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER study_trial_assignments_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.study_trial_assignments
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER study_attempts_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.study_attempts
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER study_outcomes_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.study_outcomes
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();

REVOKE ALL ON
    caplab_v0.study_registrations,
    caplab_v0.study_objects,
    caplab_v0.study_evidence_records,
    caplab_v0.study_identity_records,
    caplab_v0.study_trial_assignments,
    caplab_v0.study_attempts,
    caplab_v0.study_outcomes
FROM PUBLIC;

GRANT SELECT, INSERT ON
    caplab_v0.study_registrations,
    caplab_v0.study_objects,
    caplab_v0.study_evidence_records,
    caplab_v0.study_identity_records,
    caplab_v0.study_trial_assignments,
    caplab_v0.study_attempts,
    caplab_v0.study_outcomes
TO caplab_writer;

GRANT SELECT ON
    caplab_v0.study_registrations,
    caplab_v0.study_objects,
    caplab_v0.study_evidence_records,
    caplab_v0.study_identity_records,
    caplab_v0.study_trial_assignments,
    caplab_v0.study_attempts,
    caplab_v0.study_outcomes
TO caplab_reader, caplab_verifier;
