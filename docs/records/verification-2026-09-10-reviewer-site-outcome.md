# Original nameplate and icon behavior

The two selected newsroom presentation changes preserve the named rendering,
source-text and origin-access properties in six original executions. This
supplies bounded control candidates for specific reviewer allegations. It does
not establish that either complete change is defect-free or measure reviewer
performance.

The sequence is base `623c5f840a8dc813f404994fdfae605dd61cb894`, nameplate
change `566e5af24c0a7a7a00e04326de75bf613dedeb6d`, then icon change
`c7535007644ffea29db055365257b4a6f2b4d905`. The nameplate change is the icon
change's parent. They belong to one presentation cluster, not two independent
incidents. Both selected changes remain in the unchanged 32-change sample.

## Observed behavior

| Property | Original observations |
| --- | --- |
| Nameplate | At 320, 768 and 1280 CSS-pixel widths, the nameplate and document remain inside the viewport. The new mark is beside Newsroom. Every recorded nameplate accessibility snapshot identifies the link as AI Newsroom at `/`. |
| Icon | Only the icon revision references and serves `/icon.svg`: HTTP 200, original asset bytes and `image/svg+xml`. The two earlier revisions return 404. Chromium renders the SVG document with AI text. |
| Published content | Original SQLite store and builder preserve the synthetic story. HTML-like title and pick text render literally, with no DOM scripts. RSS preserves the title. |
| Origin restrictions | Pages, CSS and feed return 200 with the original origin headers. Tested dotfiles, database, traversal and file/SVG symlink escapes return 404; POST returns 501. Reads leave the database unchanged. |
| Ignore rule | Only the icon revision ignores `.playwright-mcp/probe.txt`. A source-file control remains unignored. |

Each revision ran twice with the original builder, store and HTTP CLI. The
72 recorded method/path observations exclude readiness and browser requests;
server logs also retain those requests. Playwright 1.63.0 drove pinned Chromium
153.0.8010.12 with pinned font inputs. Six executions completed in 18.174
seconds, with 256 capture files and 18 literal symlink targets retained.

The primary agent directly inspected the retained base and changed 320-pixel
header images, the icon revision's 1280-pixel header, and its 64-pixel SVG
rendering. This inspection supports the stated appearance observations;
it is not delegated aesthetic approval or a complete accessibility review.
The automated verifier checks actual geometry, HTTP bytes, persistent state
and DOM observations, rather than treating source markup as proof of rendering.

## Authority and custody

The [execution authorization](authorization-2026-09-10-reviewer-site-witness.md)
names these exact historical imports and bounded executions under ADR 0026.
The 124 imported source-file instances retain original commit, parent, tree,
Git blob, path, mode and SHA-256. The original `docs/publication.md` requirement
is identical at all three revisions: Git blob
`30e7c6293f58089167390e0213aa3e386e09843f`, SHA-256
`cdae09c8f712917a9b85920757d010c60396d76e92c835697a60d6672153a8be`.
Historical model opinions do not supply the outcome labels.

Private custody root:
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/site-witness-1`.
The [receipt](../product/studies/reviewer-ranking-001/site-development-receipt.json)
pins 37 process, plan, inventory and assessment files. The plan pins source,
probe, runtime, browser and font inputs. Capture inventories preserve absolute
namespace `/capture` symlink targets literally; host verification does not
follow them.

- Plan SHA-256: `616181db05c7db2ae175adb259ce6918919d7c1ca25d49966dc7d750e7c783c3`.
- Verification SHA-256: `9264c1cff77e150f07d6f2eb9b652c6390f833c4c77b3565739e70d032ae2f88`.
- Assessment SHA-256: `1305ac9d7acdbd9ef3e11e6e15004c7b58eefec80e06e3d605420f78bf021aee`.
- Repository check log SHA-256: `9952eaf2b04bd2809a1093766946219cc4063ca7185020e4a620231f0e67ced0`.

## Verification and limits

All frozen named properties hold. Three focused tests reject clipped
nameplates, executable DOM content, permissive private SVG delivery and wrong
SVG MIME, and verify that custody inventory does not read symlink targets.
`make check` completed successfully: 1,560 tests in 206.686 seconds, seven skips.
Repository checks validate CAPLAB support code; the original executions above
supply the selected-change observations.

No native reviewer ran. No case is admitted and no ranking is eligible. Browser
tab favicon UI, other browser engines, other viewport widths and universal
security or accessibility remain unassessed. The shared presentation sequence
must not be treated as independent incidents in later analysis. The feasibility
projection is now 11 bounded changes, three base-only trees and 18 pending.
