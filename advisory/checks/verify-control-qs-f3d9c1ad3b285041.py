"""Deterministic re-runnable check for control qs-f3d9c1ad3b285041
("Fleet Catalog Resolution" explanation).

Allegations (fable 5.1 and glm-flash, independently): (a) the
`fleet-catalog-resolution@2` section states that overlay resolution happens
once per invocation at the session-construction seam and that every verb that
opens graph and catalog — `drive`, `status`, `accept`, and kin — resolves the
same way, "this is session construction"; the checks section then states that
checks resolution sits in `buildSession` (the session-construction seam) "not in
the graph-and-catalog opening the recording path calls", so `accept`/`reject`
do NOT pass through session construction. The two sections place the recording
path on opposite sides of the same seam. (b) The heading declares
`checks-resolve-to-repo@1` while the section's body delivers and describes
`@2` ("The check half arrived at `checks-resolve-to-repo@2`") under that
heading.

In-set check: both are properties of the text. (a) present => DEFECTIVE.
Exit 0 = DEFECTIVE. Exit 1 = SOUND on this test.
"""
import json, re, sys
sys.path.insert(0, "/home/halbritt/git/caplab/src")
from caplab.advisory import cas
BODY_SHA = None
for line in open("/home/halbritt/git/caplab/advisory/substrates.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    if rec["substrate_id"] == "qs-f3d9c1ad3b285041":
        BODY_SHA = rec["sha256"]
doc = cas.load(BODY_SHA)
assert doc is not None, "control body missing from the CAS"
every_verb = bool(re.search(r"Every verb that opens graph and catalog resolves the same way[^.]*`accept`[^.]*this is session construction", doc, re.S))
recording_outside = bool(re.search(r"checks resolution sits in `buildSession`[^.]*not in the graph-and-catalog opening the recording path calls", doc, re.S))
heading_v1 = bool(re.search(r"^## Companion:.*\(`checks-resolve-to-repo@1`\)", doc, re.M))
body_delivers_v2 = bool(re.search(r"The check half arrived at `checks-resolve-to-repo@2`", doc))
results = {"accept_resolves_at_session_construction": every_verb,
           "recording_path_bypasses_session_construction": recording_outside,
           "seam_contradiction": every_verb and recording_outside,
           "heading_declares_v1": heading_v1, "body_delivers_v2_under_it": body_delivers_v2}
print(json.dumps(results, indent=1))
defective = results["seam_contradiction"]
print("VERDICT:", "control is DEFECTIVE: the recording path (accept/reject) is placed on both sides of the session-construction seam"
      if defective else "control is SOUND on this test")
sys.exit(0 if defective else 1)
