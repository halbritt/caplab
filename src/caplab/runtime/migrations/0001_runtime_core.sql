SELECT pg_advisory_xact_lock(hashtextextended('caplab_v0:migration', 0));

CREATE SCHEMA IF NOT EXISTS caplab_v0 AUTHORIZATION caplab_owner;
REVOKE ALL ON SCHEMA caplab_v0 FROM PUBLIC;

CREATE TABLE caplab_v0.schema_migrations (
    filename text PRIMARY KEY,
    file_sha256 text NOT NULL CHECK (file_sha256 ~ '^[0-9a-f]{64}$'),
    applied_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    runtime_commit text NOT NULL CHECK (runtime_commit ~ '^[0-9a-f]{40}$')
);

CREATE TABLE caplab_v0.operation_requests (
    operation_id text PRIMARY KEY,
    request_sha256 text NOT NULL CHECK (request_sha256 ~ '^[0-9a-f]{64}$'),
    campaign_id text NOT NULL,
    request_body jsonb NOT NULL CHECK (jsonb_typeof(request_body) = 'object'),
    requested_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE caplab_v0.operation_events (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation_id text NOT NULL REFERENCES caplab_v0.operation_requests(operation_id),
    event_type text NOT NULL,
    event_body jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(event_body) = 'object'),
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE caplab_v0.model_identities (
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object')
);

CREATE TABLE caplab_v0.agent_configurations (
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object')
);

CREATE TABLE caplab_v0.administrations (
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object')
);

CREATE TABLE caplab_v0.trial_contexts (
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object')
);

CREATE TABLE caplab_v0.trial_assignments (
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object')
);

CREATE TABLE caplab_v0.attempts (
    identity_sha256 text PRIMARY KEY CHECK (identity_sha256 ~ '^[0-9a-f]{64}$'),
    assignment_sha256 text NOT NULL REFERENCES caplab_v0.trial_assignments(identity_sha256),
    attempt_number integer NOT NULL CHECK (attempt_number > 0),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    UNIQUE (assignment_sha256, attempt_number)
);

CREATE TABLE caplab_v0.artifacts (
    content_sha256 text PRIMARY KEY CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    object_key text NOT NULL UNIQUE,
    local_copy_key text NOT NULL UNIQUE,
    media_type text NOT NULL,
    byte_count bigint NOT NULL CHECK (byte_count >= 0)
);

CREATE TABLE caplab_v0.attempt_artifacts (
    attempt_sha256 text NOT NULL REFERENCES caplab_v0.attempts(identity_sha256),
    content_sha256 text NOT NULL REFERENCES caplab_v0.artifacts(content_sha256),
    artifact_kind text NOT NULL,
    PRIMARY KEY (attempt_sha256, content_sha256, artifact_kind)
);

CREATE TABLE caplab_v0.manifests (
    manifest_sha256 text PRIMARY KEY CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object')
);

CREATE TABLE caplab_v0.registrations (
    registration_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation_id text NOT NULL UNIQUE REFERENCES caplab_v0.operation_requests(operation_id),
    campaign_id text NOT NULL,
    content_sha256 text NOT NULL REFERENCES caplab_v0.artifacts(content_sha256),
    manifest_sha256 text NOT NULL REFERENCES caplab_v0.manifests(manifest_sha256),
    model_sha256 text NOT NULL REFERENCES caplab_v0.model_identities(identity_sha256),
    agent_configuration_sha256 text NOT NULL REFERENCES caplab_v0.agent_configurations(identity_sha256),
    administration_sha256 text NOT NULL REFERENCES caplab_v0.administrations(identity_sha256),
    trial_context_sha256 text NOT NULL REFERENCES caplab_v0.trial_contexts(identity_sha256),
    trial_assignment_sha256 text NOT NULL REFERENCES caplab_v0.trial_assignments(identity_sha256),
    attempt_sha256 text NOT NULL REFERENCES caplab_v0.attempts(identity_sha256),
    analysis_sha256 text NOT NULL CHECK (analysis_sha256 ~ '^[0-9a-f]{64}$'),
    registered_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE caplab_v0.audit_events (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation_id text REFERENCES caplab_v0.operation_requests(operation_id),
    event_type text NOT NULL,
    event_body jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(event_body) = 'object'),
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE FUNCTION caplab_v0.reject_mutation() RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'CAPLAB v0 rows are append-only';
END;
$$;

CREATE TRIGGER schema_migrations_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.schema_migrations
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER operation_requests_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.operation_requests
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER operation_events_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.operation_events
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER model_identities_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.model_identities
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER agent_configurations_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.agent_configurations
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER administrations_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.administrations
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER trial_contexts_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.trial_contexts
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER trial_assignments_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.trial_assignments
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER attempts_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.attempts
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER artifacts_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.artifacts
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER attempt_artifacts_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.attempt_artifacts
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER manifests_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.manifests
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER registrations_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.registrations
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER audit_events_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.audit_events
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();

CREATE VIEW caplab_v0.current_operation_state AS
SELECT DISTINCT ON (request.operation_id)
    request.operation_id,
    request.request_sha256,
    request.campaign_id,
    event.event_type,
    event.occurred_at
FROM caplab_v0.operation_requests AS request
LEFT JOIN caplab_v0.operation_events AS event USING (operation_id)
ORDER BY request.operation_id, event.event_id DESC NULLS LAST;

CREATE VIEW caplab_v0.registration_integrity AS
SELECT
    registration.operation_id,
    registration.campaign_id,
    artifact.content_sha256,
    artifact.object_key,
    artifact.local_copy_key,
    artifact.byte_count,
    registration.manifest_sha256,
    request.request_sha256
FROM caplab_v0.registrations AS registration
JOIN caplab_v0.artifacts AS artifact USING (content_sha256)
JOIN caplab_v0.operation_requests AS request USING (operation_id);

CREATE VIEW caplab_v0.reconciliation AS
SELECT
    integrity.*,
    (integrity.object_key =
        'objects/sha256/' || left(integrity.content_sha256, 2) || '/' || integrity.content_sha256
    ) AS object_locator_matches,
    (integrity.local_copy_key = integrity.object_key) AS local_locator_matches
FROM caplab_v0.registration_integrity AS integrity;

REVOKE ALL ON ALL TABLES IN SCHEMA caplab_v0 FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA caplab_v0 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA caplab_v0 FROM PUBLIC;
REVOKE ALL ON caplab_v0.schema_migrations FROM caplab_writer;
GRANT SELECT ON caplab_v0.schema_migrations TO caplab_writer;

GRANT USAGE ON SCHEMA caplab_v0 TO caplab_writer, caplab_reader, caplab_verifier;
GRANT SELECT, INSERT ON
    caplab_v0.operation_requests,
    caplab_v0.operation_events,
    caplab_v0.model_identities,
    caplab_v0.agent_configurations,
    caplab_v0.administrations,
    caplab_v0.trial_contexts,
    caplab_v0.trial_assignments,
    caplab_v0.attempts,
    caplab_v0.artifacts,
    caplab_v0.attempt_artifacts,
    caplab_v0.manifests,
    caplab_v0.registrations,
    caplab_v0.audit_events
TO caplab_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA caplab_v0 TO caplab_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA caplab_v0 TO caplab_reader, caplab_verifier;

ALTER DEFAULT PRIVILEGES FOR ROLE caplab_owner IN SCHEMA caplab_v0
    REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE caplab_owner IN SCHEMA caplab_v0
    REVOKE ALL ON SEQUENCES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES FOR ROLE caplab_owner IN SCHEMA caplab_v0
    REVOKE ALL ON FUNCTIONS FROM PUBLIC;
