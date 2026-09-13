# HNP-RELEASE-20260913

Status: RELEASE_VERIFIED (physical mobile NOT RUN; full surveyed reconstruction not claimed)
Editor owner: unity_engineer (`/root/game_system`)

## Goal and inputs

Finish the pending MAP007 scene correction, validate the station → street → Yak Bridge → temple prayer journey, produce the canonical Web build, commit and push, then test https://go2jd.taati.dev/ after deployment. Inputs: saved NakornpathomWorld scene, MAP007 v002 Blender checkpoint, MAP004 route evidence, user feedback and project reference documents.

## Ownership

- Blender artist: MAP007 source, export, previews and geometry reports.
- Designer/tester: independent art and gameplay review in reports/reviews and reports/qa.
- Unity engineer: exclusive Editor, Unity code/assets/settings, integration and build.
- Root: release tooling, Git tracking, task record, deploy verification and coordination.

## Acceptance

- Review actual station, street, bridge and temple visuals and resolve actionable art failures.
- Import approved Blender production assets with working materials and colliders.
- Test continuous travel to prayer and exit, map/return, relevant touch and browser behavior.
- Build into builds/web; inspect the generated build rather than relying on previous test results.
- Push source and canonical Web output; verify deployed file hashes and browser gameplay.
- Record PASS / FAIL / BLOCKED / NOT RUN separately. Physical Android/iPhone testing cannot be claimed from desktop emulation. Precise unsurveyed architectural dimensions remain provisional in documentation.

## Findings

- Previous code-only commit 1f8794a did not include a new canonical Web build. The GitHub workflow publishes builds/web and does not run Unity.
- Initial Unity preflight: saved clean scene, idle, relay available. Evidence: reports/tmp/hnp-release-20260913-preflight.json.
- MAP007 v002 starts as a Blender checkpoint requiring review/export before integration.
- Fidelity correction after source review: prior MAP004 turns and numerical Chedi-occlusion gates were authored assumptions, not user requirements. Use the direct station / Rotfai Road / Charoen Sattha Bridge / north shrine corridor. A Google Maps visual cross-check and Silpakorn Library's bridge history contradict the previous station datum and bridge treatment; the design owner is recording the replacement contract.
- Confirmed authored Unity anchors: station (0,0), bridge centre (130,0), Chedi centre (519,0), path toward +X. Historical bridge dimensions 34.5 x 8.5 m inform the model; this is not a current measured survey.
- Web release tooling creates per-binary cache keys and a SHA-256 manifest. GitHub checks the manifest before publishing. Stamp/idempotence/hash test PASS on a separate temporary copy of the previous build; fresh release still requires its own browser QA.
- Git ignore corrected so required Unity Assets, Packages and ProjectSettings can be tracked; generated Unity caches remain ignored.
- Release verifier self-test PASS against a loopback HTTP server serving the separate stamped test copy: all five hashes and Wasm MIME validated. Evidence `reports/qa/HNP-RELEASE-20260913-verifier-selftest.json`; this is tooling validation, not a public deployment result.
- Official height cross-check: TAT Japan gives 120.45 m. Scale is based on measured aggregate rendered bounds (47.30959 m before adjustment), not the nominal 44 m source label; uniform scaling produces a measured 120.45 m result without vertically stretching the architecture. Unsurveyed footprint details remain provisional. Source: https://www.thailandtravel.or.jp/phra-pathom-chedi/ .
- The initial browser preflight failed with an actual `HnpNightLighting.Start` exception from an obsolete scene-object name. This is a failed interim build, not release acceptance. The engineer is correcting the active hero lookup and direct-route lighting, alongside the continuous temple-entry collision test.
- A physics-only roundtrip passed, but visual review exposed a separate source defect: v004 M03 full annular mouldings cross the previously authored prayer corridor at player height after real-height scaling. Read-only Blender BVH evidence: `reports/qa/HNP-RELEASE-20260913-source-aperture.json`. Root owns the narrow v005 M03 source repair, using surface clipping to remove only intersecting surfaces (not hiding colliders or inventing Boolean caps). Source and FBX roundtrip: 8,385 triangles, zero degenerate faces, UV present, clear centerline rays; independent review and Unity integration remain separate gates.
- MAP007 integration defects were independently caught before publication: resetting FBX root rotations broke single-mesh axis conversion; stationary camera/physics could pass below the raised bridge; the old flat bridge collision was not valid for the new visual deck. Neutral placement wrappers now preserve imported transforms; the station wrapper faces the route (Y=180, X=-15). The Blender bridge revision adds visible ground lead-ins and matching collision on both ends, and splits canal-bank blockers outside the road opening. These changes require final scene and browser retests, not reuse of the interim PASS.
- Interim browser functional PASS: `reports/qa/release-20260913-web-20260913-110051/report.json`. It verifies actual night/time UI, map/BACK pause, portrait clock/player freeze, pointer-emulated movement, keyboard bridge/prayer journey, prayer progress freeze/completion and reverse movement with zero browser errors. It predates final MAP007/v005 visual integration and is **not** final release acceptance.

## Validation

Art: M03 v005 narrow independent review PASS (`reports/reviews/HNP-ART-CHEDI-001-v005-aperture-review.md`). MAP007 v003 source/exports/all 12 FBX roundtrips and final art staging review PASS (`reports/reviews/HNP-ART-MAP-007-v003-final-handoff-review.md`). Unity integration/route regression: PASS (`reports/qa/HNP-RELEASE-20260913-unity-gates.json`). Final build: PASS (`reports/world/build-20260913-112851.txt`), built in an isolated output after a transient canonical-file lock, then hash-checked and promoted to builds/web. Release ID: `74e3a5a4f7cd-e38217f5f90c`.

Final local hardware-browser validation: PASS (`reports/qa/release-20260913-web-20260913-113643/report.json`, Chrome 152 / NVIDIA RTX 4070 SUPER / D3D11). Actual keyboard route crosses the visible bridge deck, reaches prayer, completes once, exits and returns through the visible Settings RETURN button. Map and portrait pauses, night/day switching and pointer-emulated movement pass with zero browser errors. This supersedes interim runs. Physical mobile: NOT RUN. Public deployment and live gameplay: pending push.

The scene is a playable reference-led stylized reconstruction, not a photorealistic or fully surveyed 1:1 architectural replica. Street frontage and unsurveyed dimensions remain provisional.

## Published release

- Source and canonical Web build committed and pushed as `6eccd3b9beb532ae65cc9bce8b6315e29481c0fb`.
- GitHub Pages deployment PASS: https://github.com/PTaati/HelloNakornpathom/actions/runs/34738416899 .
- Public URL: https://go2jd.taati.dev/ . All five deployed file hashes match the tested build, including the ordinary HTML entry point; Wasm MIME PASS. Evidence: `reports/qa/HNP-RELEASE-20260913-deployment.json`.
- Live browser gameplay PASS: `reports/qa/release-20260913-web-20260913-114104/report.json`. Actual keyboard/pointer interactions repeat the route, bridge crossing, prayer completion, map/portrait pause, night/day and Settings RETURN tests with zero browser errors. Hardware desktop Chrome 152; physical Android/iPhone NOT RUN.
- The subsequent evidence-only commit does not change any deployed game bytes. Its deployment can be verified against the same release ID and hashes without treating it as a new game build.
