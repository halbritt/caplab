# Preserve independent references for the Claude findings

Under ADR 0026 and the active reviewer-ranking goal, authorize preserving the
public upstream systemd release references `v243` and `v244` in the private
`claude-output-1/references` directory. Resolve the exact release commits,
then retrieve only `src/core/service.c` at each revision and
`man/systemd.service.xml` at v244 from the official systemd/systemd repository.
Retain repository URL, tag, resolved commit, path, Git blob identity, byte hash
and retrieval time. These references may support or refute the report's
version-compatibility premise; they do not establish this host's deployment
version or execute a service. No upstream source is admitted as CAPLAB product
authority. No source code execution, service changes or other imports.

Also authorize retaining a new finding assessment tied to all four complete
native finding IDs and independent source/witness locators. Prior reports,
witnesses and assessments remain unchanged. The existing optional-RSS witness
may be referenced after hash verification, without copying or rerunning it.
New operational claims without a decisive requirement or behavioral witness
must remain unresolved. An advisory or uncertain finding does not become an
incorrect blocker. Keep native auxiliary model use and reported limitations
visible. No case admission, score, ranking or qualification is authorized.

The reference fetch allowance expires on consumption or 2026-09-11T02:00:00Z.
