# HNP-WORLD-010 — final r1 Web visual review

**Date:** 2026-09-10  
**Build:** `builds/world010-r1/web`  
**Wasm SHA-256:** `7222c7d2919792cf35531f027501c720f3fb6d5ec48042e14437684863047369`  
**Desktop browser evidence:** Chrome `152.0.7977.83`; physical mobile: **NOT RUN**.  
**Reviewed evidence:** `reports/world/world010-integration/{shrine-front.png,shrine-oblique.png,overviewthree-quarter.png,photo-validation.json,collision.json,temple-routes.json}`; `reports/world/world010-shrine-20260910-232325/{shrine-day.png,shrine-night.png,shrine-portrait.png,report.json}`; `reports/world/world008-night-20260910-232426/report.json`; `reports/world/world009-reference-20260910-232520/report.json`; source reference `ref/pra.jpg`. No Unity, scene, art, or browser was modified by this reviewer.

## Result

| Acceptance area | Status | Evidence / finding |
| --- | --- | --- |
| Source photo correctness | **PASS** | The day, night and portrait Web captures show the supplied Buddha photo upright and unmirrored: its raised hand remains viewer-left, matching `pra.jpg`. `photo-validation.json` records the expected 387×792 reference hash/GUID and five unblocked front rays; the Web diagnostic reports the same 0.488636 aspect on an unlit photo material. |
| Rectangular projecting chamber | **PASS (stylized visual)** | The integration front/oblique/overview captures show a gabled, rectangular-front chamber attached to the Chedi, with roof, opaque side walls, threshold/floor and a deep dark recess/back plane. It removes the earlier primitive statue treatment and makes the real photo immediately legible. Chamber proportions and simplified exterior remain a gameplay adaptation, not a claim of exact architecture. |
| Gameplay-camera readability | **PASS (desktop Web capture)** | The shrine remains clear above the third-person traveller at normal approach distance. The avatar covers a small lower portion of the photo in the close captures, but not the Buddha identity or orientation; the unobscured Unity front capture confirms the full portrait. Night retains readable unlit photo content. |
| Chedi collision and circulation | **PASS (reported)** | Integration evidence reports 16 cardinal movement/jump/sprint collision cases PASS; four cardinal stair centerlines are `gateDeviation: 0`, and both upper-court arcs pass. The r1 Web night/collision report is PASS with the inward approach blocked after sprint/jump and retreat succeeding. |
| Reported r1 Web function | **PASS (reported)** | `world010-shrine-20260910-232325/report.json` is PASS with no errors after real WASD/drag capture and photo day/night/portrait diagnostics. The matching r1 night/collision report is PASS with no errors. This reviewer independently inspected the outputs but did not rerun browser interaction. |
| Clock/map/camera reference regression | **PASS (reported)** | The final matching-r1 reference record is PASS with no errors: clock advances, the menu pauses it, night state is recorded, and camera sky pitch is reported. This reviewer did not rerun those interactions. |
| Physical mobile release | **NOT RUN** | Desktop Chrome screenshots and automation do not establish phone performance, brightness, safe-area/touch ergonomics, or real Android/iPhone browser behavior. |

## Conclusion

**PASS for the scoped HNP-WORLD-010 r1 desktop/Web visual release.** The actual `pra.jpg` is shown correctly in a connected rectangular shrine chamber, without the prior crude statue, and current integration/Web evidence supports the preserved route and collision contract. Physical-device validation remains **NOT RUN**.
