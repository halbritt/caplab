SELECT pg_advisory_xact_lock(hashtextextended('caplab_v0:migration', 0));

CREATE TABLE caplab_v0.invalid_attempt_observations (
    observation_id text PRIMARY KEY,
    campaign_id text NOT NULL CHECK (campaign_id = 'caplab-p5-recovery-2026-07-16'),
    fixture_sha256 text NOT NULL CHECK (fixture_sha256 ~ '^[0-9a-f]{64}$'),
    fixture_byte_count bigint NOT NULL CHECK (fixture_byte_count > 0),
    disposition text NOT NULL CHECK (disposition IN ('invalid', 'ambiguous')),
    reason_codes jsonb NOT NULL CHECK (
        jsonb_typeof(reason_codes) = 'array'
        AND jsonb_array_length(reason_codes) > 0
    ),
    observed_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE caplab_v0.custody_requests (
    custody_request_id text PRIMARY KEY,
    operation_id text NOT NULL UNIQUE,
    campaign_id text NOT NULL CHECK (campaign_id = 'caplab-p5-recovery-2026-07-16'),
    request_sha256 text NOT NULL CHECK (request_sha256 ~ '^[0-9a-f]{64}$'),
    content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    manifest_sha256 text NOT NULL CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    authorization_sha256 text NOT NULL CHECK (authorization_sha256 ~ '^[0-9a-f]{64}$'),
    expires_at timestamptz NOT NULL CHECK (expires_at = '2026-07-23T23:59:59Z'::timestamptz),
    requested_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE caplab_v0.custody_dependency_events (
    dependency_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    operation_id text NOT NULL,
    dependency_kind text NOT NULL CHECK (
        dependency_kind IN ('registration', 'result', 'claim', 'dataset', 'campaign')
    ),
    dependency_identity text NOT NULL,
    event_type text NOT NULL CHECK (event_type IN ('retained', 'released')),
    occurred_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE caplab_v0.purge_tombstones (
    custody_request_id text PRIMARY KEY REFERENCES caplab_v0.custody_requests(custody_request_id),
    operation_id text NOT NULL UNIQUE,
    campaign_id text NOT NULL,
    request_sha256 text NOT NULL CHECK (request_sha256 ~ '^[0-9a-f]{64}$'),
    content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    object_key text NOT NULL,
    local_copy_key text NOT NULL,
    manifest_sha256 text NOT NULL CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    identity_sha256 jsonb NOT NULL CHECK (jsonb_typeof(identity_sha256) = 'object'),
    authorization_sha256 text NOT NULL CHECK (authorization_sha256 ~ '^[0-9a-f]{64}$'),
    row_counts jsonb NOT NULL CHECK (jsonb_typeof(row_counts) = 'object'),
    purged_at timestamptz NOT NULL
);

CREATE TRIGGER invalid_attempt_observations_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.invalid_attempt_observations
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER custody_requests_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.custody_requests
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER custody_dependency_events_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.custody_dependency_events
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();
CREATE TRIGGER purge_tombstones_append_only
    BEFORE UPDATE OR DELETE ON caplab_v0.purge_tombstones
    FOR EACH ROW EXECUTE FUNCTION caplab_v0.reject_mutation();

CREATE VIEW caplab_v0.current_custody_dependencies AS
SELECT dependency.operation_id, dependency.dependency_kind, dependency.dependency_identity
FROM (
    SELECT DISTINCT ON (operation_id, dependency_kind, dependency_identity)
        operation_id,
        dependency_kind,
        dependency_identity,
        event_type
    FROM caplab_v0.custody_dependency_events
    ORDER BY
        operation_id,
        dependency_kind,
        dependency_identity,
        dependency_event_id DESC
) AS dependency
WHERE dependency.event_type = 'retained';

CREATE OR REPLACE FUNCTION caplab_v0.reject_mutation() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    purge_request_id text;
BEGIN
    purge_request_id := current_setting('caplab.p5_purge_request_id', true);
    IF TG_OP = 'DELETE'
       AND current_user = 'caplab_owner'
       AND purge_request_id IS NOT NULL
       AND purge_request_id <> ''
       AND EXISTS (
           SELECT 1
           FROM caplab_v0.custody_requests AS custody
           WHERE custody.custody_request_id = purge_request_id
             AND custody.expires_at > clock_timestamp()
             AND NOT EXISTS (
                 SELECT 1
                 FROM caplab_v0.purge_tombstones AS tombstone
                 WHERE tombstone.custody_request_id = custody.custody_request_id
             )
       )
    THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION 'CAPLAB v0 rows are append-only';
END;
$$;

CREATE FUNCTION caplab_v0.purge_p5_operation(p_custody_request_id text)
RETURNS TABLE (
    custody_request_id text,
    operation_id text,
    campaign_id text,
    request_sha256 text,
    content_sha256 text,
    object_key text,
    local_copy_key text,
    manifest_sha256 text,
    identity_sha256 jsonb,
    authorization_sha256 text,
    row_counts jsonb,
    purged_at timestamptz
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, caplab_v0
AS $$
DECLARE
    custody caplab_v0.custody_requests%ROWTYPE;
    retained_operation caplab_v0.operation_requests%ROWTYPE;
    retained_registration caplab_v0.registrations%ROWTYPE;
    retained_artifact caplab_v0.artifacts%ROWTYPE;
    retained_identity jsonb;
    audit_count bigint;
    event_count bigint;
    registration_count bigint;
    attempt_artifact_count bigint;
    artifact_count bigint;
    manifest_count bigint;
    attempt_count bigint;
    trial_assignment_count bigint;
    trial_context_count bigint;
    administration_count bigint;
    agent_configuration_count bigint;
    model_count bigint;
    operation_count bigint;
    completed_at timestamptz;
    deleted_counts jsonb;
BEGIN
    SELECT *
    INTO custody
    FROM caplab_v0.custody_requests
    WHERE caplab_v0.custody_requests.custody_request_id = p_custody_request_id
    FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'unknown P5 custody request' USING ERRCODE = 'P5001';
    END IF;
    IF custody.campaign_id <> 'caplab-p5-recovery-2026-07-16' THEN
        RAISE EXCEPTION 'custody request is not the authorized P5 campaign'
            USING ERRCODE = 'P5002';
    END IF;
    IF custody.expires_at <= clock_timestamp() THEN
        RAISE EXCEPTION 'P5 custody request has expired' USING ERRCODE = 'P5003';
    END IF;
    IF EXISTS (
        SELECT 1
        FROM caplab_v0.purge_tombstones AS existing
        WHERE existing.custody_request_id = custody.custody_request_id
    ) THEN
        RAISE EXCEPTION 'P5 custody request is no longer pending' USING ERRCODE = 'P5001';
    END IF;

    PERFORM pg_advisory_xact_lock(hashtextextended('caplab-operation:' || custody.operation_id, 0));
    PERFORM pg_advisory_xact_lock(hashtextextended('caplab-content:' || custody.content_sha256, 0));

    SELECT *
    INTO retained_operation
    FROM caplab_v0.operation_requests
    WHERE caplab_v0.operation_requests.operation_id = custody.operation_id
    FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'unknown P5 operation identity' USING ERRCODE = 'P5001';
    END IF;
    IF retained_operation.campaign_id <> custody.campaign_id
       OR retained_operation.request_sha256 <> custody.request_sha256
    THEN
        RAISE EXCEPTION 'operation request differs from P5 custody identity'
            USING ERRCODE = 'P5002';
    END IF;

    SELECT *
    INTO retained_registration
    FROM caplab_v0.registrations
    WHERE caplab_v0.registrations.operation_id = custody.operation_id
    FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'P5 operation is not registered' USING ERRCODE = 'P5001';
    END IF;
    IF retained_registration.campaign_id <> custody.campaign_id
       OR retained_registration.content_sha256 <> custody.content_sha256
       OR retained_registration.manifest_sha256 <> custody.manifest_sha256
    THEN
        RAISE EXCEPTION 'registration differs from P5 custody identity'
            USING ERRCODE = 'P5002';
    END IF;

    SELECT *
    INTO retained_artifact
    FROM caplab_v0.artifacts
    WHERE caplab_v0.artifacts.content_sha256 = custody.content_sha256
    FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'P5 artifact identity is absent' USING ERRCODE = 'P5001';
    END IF;

    retained_identity := jsonb_build_object(
        'model', retained_registration.model_sha256,
        'agent_configuration', retained_registration.agent_configuration_sha256,
        'administration', retained_registration.administration_sha256,
        'trial_context', retained_registration.trial_context_sha256,
        'trial_assignment', retained_registration.trial_assignment_sha256,
        'attempt', retained_registration.attempt_sha256,
        'analysis', retained_registration.analysis_sha256
    );

    IF EXISTS (
        SELECT 1
        FROM caplab_v0.current_custody_dependencies AS dependency
        WHERE dependency.operation_id = custody.operation_id
    ) THEN
        RAISE EXCEPTION 'retained dependency prevents P5 purge' USING ERRCODE = 'P5004';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM caplab_v0.registrations AS other
        WHERE other.operation_id <> custody.operation_id
          AND (
              other.content_sha256 = retained_registration.content_sha256
              OR other.manifest_sha256 = retained_registration.manifest_sha256
              OR other.model_sha256 = retained_registration.model_sha256
              OR other.agent_configuration_sha256 = retained_registration.agent_configuration_sha256
              OR other.administration_sha256 = retained_registration.administration_sha256
              OR other.trial_context_sha256 = retained_registration.trial_context_sha256
              OR other.trial_assignment_sha256 = retained_registration.trial_assignment_sha256
              OR other.attempt_sha256 = retained_registration.attempt_sha256
              OR other.analysis_sha256 = retained_registration.analysis_sha256
          )
    ) THEN
        RAISE EXCEPTION 'shared registration identity prevents P5 purge'
            USING ERRCODE = 'P5004';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM caplab_v0.operation_requests AS other
        WHERE other.operation_id <> custody.operation_id
          AND (
              other.request_body ->> 'content_sha256' = custody.content_sha256
              OR other.request_body ->> 'manifest_sha256' = custody.manifest_sha256
              OR EXISTS (
                  SELECT 1
                  FROM jsonb_each_text(other.request_body -> 'identity_sha256') AS identity(layer, value)
                  WHERE value IN (
                      retained_registration.model_sha256,
                      retained_registration.agent_configuration_sha256,
                      retained_registration.administration_sha256,
                      retained_registration.trial_context_sha256,
                      retained_registration.trial_assignment_sha256,
                      retained_registration.attempt_sha256,
                      retained_registration.analysis_sha256
                  )
              )
          )
    ) THEN
        RAISE EXCEPTION 'shared incomplete-operation identity prevents P5 purge'
            USING ERRCODE = 'P5004';
    END IF;

    PERFORM set_config('caplab.p5_purge_request_id', custody.custody_request_id, true);

    DELETE FROM caplab_v0.audit_events
    WHERE caplab_v0.audit_events.operation_id = custody.operation_id;
    GET DIAGNOSTICS audit_count = ROW_COUNT;

    DELETE FROM caplab_v0.operation_events
    WHERE caplab_v0.operation_events.operation_id = custody.operation_id;
    GET DIAGNOSTICS event_count = ROW_COUNT;

    DELETE FROM caplab_v0.registrations
    WHERE caplab_v0.registrations.operation_id = custody.operation_id;
    GET DIAGNOSTICS registration_count = ROW_COUNT;

    DELETE FROM caplab_v0.attempt_artifacts
    WHERE caplab_v0.attempt_artifacts.attempt_sha256 = retained_registration.attempt_sha256
      AND caplab_v0.attempt_artifacts.content_sha256 = retained_registration.content_sha256;
    GET DIAGNOSTICS attempt_artifact_count = ROW_COUNT;

    DELETE FROM caplab_v0.artifacts
    WHERE caplab_v0.artifacts.content_sha256 = retained_registration.content_sha256;
    GET DIAGNOSTICS artifact_count = ROW_COUNT;

    DELETE FROM caplab_v0.manifests
    WHERE caplab_v0.manifests.manifest_sha256 = retained_registration.manifest_sha256;
    GET DIAGNOSTICS manifest_count = ROW_COUNT;

    DELETE FROM caplab_v0.attempts
    WHERE caplab_v0.attempts.identity_sha256 = retained_registration.attempt_sha256;
    GET DIAGNOSTICS attempt_count = ROW_COUNT;

    DELETE FROM caplab_v0.trial_assignments
    WHERE caplab_v0.trial_assignments.identity_sha256 = retained_registration.trial_assignment_sha256;
    GET DIAGNOSTICS trial_assignment_count = ROW_COUNT;

    DELETE FROM caplab_v0.trial_contexts
    WHERE caplab_v0.trial_contexts.identity_sha256 = retained_registration.trial_context_sha256;
    GET DIAGNOSTICS trial_context_count = ROW_COUNT;

    DELETE FROM caplab_v0.administrations
    WHERE caplab_v0.administrations.identity_sha256 = retained_registration.administration_sha256;
    GET DIAGNOSTICS administration_count = ROW_COUNT;

    DELETE FROM caplab_v0.agent_configurations
    WHERE caplab_v0.agent_configurations.identity_sha256 = retained_registration.agent_configuration_sha256;
    GET DIAGNOSTICS agent_configuration_count = ROW_COUNT;

    DELETE FROM caplab_v0.model_identities
    WHERE caplab_v0.model_identities.identity_sha256 = retained_registration.model_sha256;
    GET DIAGNOSTICS model_count = ROW_COUNT;

    DELETE FROM caplab_v0.operation_requests
    WHERE caplab_v0.operation_requests.operation_id = custody.operation_id;
    GET DIAGNOSTICS operation_count = ROW_COUNT;

    IF registration_count <> 1 OR artifact_count <> 1 OR manifest_count <> 1
       OR attempt_count <> 1 OR trial_assignment_count <> 1
       OR trial_context_count <> 1 OR administration_count <> 1
       OR agent_configuration_count <> 1 OR model_count <> 1
       OR operation_count <> 1
    THEN
        RAISE EXCEPTION 'P5 purge closure was incomplete' USING ERRCODE = 'P5005';
    END IF;

    completed_at := clock_timestamp();
    deleted_counts := jsonb_build_object(
        'audit_events', audit_count,
        'operation_events', event_count,
        'registrations', registration_count,
        'attempt_artifacts', attempt_artifact_count,
        'artifacts', artifact_count,
        'manifests', manifest_count,
        'attempts', attempt_count,
        'trial_assignments', trial_assignment_count,
        'trial_contexts', trial_context_count,
        'administrations', administration_count,
        'agent_configurations', agent_configuration_count,
        'model_identities', model_count,
        'operation_requests', operation_count
    );

    INSERT INTO caplab_v0.purge_tombstones (
        custody_request_id,
        operation_id,
        campaign_id,
        request_sha256,
        content_sha256,
        object_key,
        local_copy_key,
        manifest_sha256,
        identity_sha256,
        authorization_sha256,
        row_counts,
        purged_at
    ) VALUES (
        custody.custody_request_id,
        custody.operation_id,
        custody.campaign_id,
        custody.request_sha256,
        custody.content_sha256,
        retained_artifact.object_key,
        retained_artifact.local_copy_key,
        custody.manifest_sha256,
        retained_identity,
        custody.authorization_sha256,
        deleted_counts,
        completed_at
    );

    PERFORM set_config('caplab.p5_purge_request_id', '', true);

    RETURN QUERY
    SELECT
        tombstone.custody_request_id,
        tombstone.operation_id,
        tombstone.campaign_id,
        tombstone.request_sha256,
        tombstone.content_sha256,
        tombstone.object_key,
        tombstone.local_copy_key,
        tombstone.manifest_sha256,
        tombstone.identity_sha256,
        tombstone.authorization_sha256,
        tombstone.row_counts,
        tombstone.purged_at
    FROM caplab_v0.purge_tombstones AS tombstone
    WHERE tombstone.custody_request_id = custody.custody_request_id;
END;
$$;

REVOKE ALL ON
    caplab_v0.invalid_attempt_observations,
    caplab_v0.custody_requests,
    caplab_v0.custody_dependency_events,
    caplab_v0.purge_tombstones
FROM PUBLIC;
REVOKE ALL ON FUNCTION caplab_v0.purge_p5_operation(text) FROM PUBLIC;

GRANT USAGE ON SCHEMA caplab_v0 TO caplab_custodian;
GRANT SELECT, INSERT ON
    caplab_v0.invalid_attempt_observations,
    caplab_v0.custody_requests,
    caplab_v0.custody_dependency_events
TO caplab_custodian;
GRANT SELECT ON caplab_v0.purge_tombstones TO caplab_custodian;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA caplab_v0 TO caplab_custodian;
GRANT EXECUTE ON FUNCTION caplab_v0.purge_p5_operation(text) TO caplab_custodian;

GRANT SELECT ON
    caplab_v0.invalid_attempt_observations,
    caplab_v0.custody_requests,
    caplab_v0.custody_dependency_events,
    caplab_v0.purge_tombstones,
    caplab_v0.current_custody_dependencies
TO caplab_verifier;
