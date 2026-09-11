# Investigate two selected presentation changes through rendering and HTTP

Under ADR 0026 and the active reviewer-ranking goal, authorize private
`reviewer-ranking-001/development/site-witness-1` custody for original
newsroom revisions: base `623c5f840a8dc813f404994fdfae605dd61cb894`,
nameplate change `566e5af24c0a7a7a00e04326de75bf613dedeb6d`, and favicon
change `c7535007644ffea29db055365257b4a6f2b4d905`. Both changes are in the
fixed sample and the latter directly follows the former. Preserve this
relationship; two covered changes do not establish two independent incidents.

Import exactly their tracked `newsroom/`, `README.md`, `pyproject.toml`,
`docs/publication.md` and `.gitignore`, with commit, parent, tree, path,
Git blob, mode and content hash. The original publication document supplies
historical rendering, escaping and read-only-origin requirements only. It
creates no current authority or admission. Copy no historical publication
data, model responses, credentials or live state.

For each revision, twice, create a new original PublicationStore with one
synthetic source/pick containing HTML-like text. Build using original
`build_site`, then run the original `newsroom.site` HTTP CLI on private
loopback. Exercise public pages, CSS, feed and favicon, and documented
dotfile, private-database, traversal, symlink-escape and write restrictions.
Create only synthetic private and symlink fixtures in the disposable capture.
Check the original ignore rule in a new disposable Git repository with no
user configuration: the Playwright working path versus a source-file control.
No original function, handler, clock or source file may be patched.

Render the actual served site in installed Playwright 1.63.0 with its matching
Chromium headless shell 153.0.8010.12 at widths 320, 768 and 1280. Retain
screenshots, computed nameplate geometry/style, link semantics, page errors
and requests. Render the served SVG separately when present. Pin browser,
Playwright package, Node, Python and system-font inputs before execution.
This tests original rendered behavior, not the presence of a planted marker
or a scripted reviewer's answer.

All execution is network-isolated; source, browser and inputs are read-only.
Retain absolute `/capture` symlink targets literally in capture inventories;
do not follow those links on the host or rewrite original builder output.
Only private build/database/capture and temporary browser state are writable.
Use a synthetic home with no credentials. No external website, model, live
publication, service or original repository may be mutated. Stop the
per-execution server/browser during cleanup. Limit each execution to 90
seconds, browser subprocess to 60 seconds and the sequence to 1200 seconds.
Expiry is consumption or 2026-09-11T01:00:00Z. Stop on input drift, process
failure, timeout or unsafe isolation; retain failures and do not automatically
restart. Preserve disagreeing outcomes rather than changing frozen criteria.

Assess supported rendering, delivery, escaping and access-control properties
separately from aesthetic approval or universal accessibility/security claims.
Keep other viewports, browser engines and untested scenarios explicit.
Update fixed-sample coverage only from established original behavior.
Authorize no case admission, reviewer score, historical rescoring or ranking.
