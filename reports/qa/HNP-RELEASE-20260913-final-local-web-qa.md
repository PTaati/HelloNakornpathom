# HNP-RELEASE-20260913 — final local Web QA

**Task / requirements:** HNP-RELEASE-20260913; G02, G03, G04, G06, G07, P01.  
**Decision:** **PASS — canonical local Web build on hardware desktop browser.**  
**Release limitation:** physical mobile is **NOT RUN**; desktop pointer emulation is not a substitute.

## Build and environment

- Build: `builds/web` (canonical promoted build)
- WASM SHA-256: `e38217f5f90cee070b157e8c0c7189599bd160b26e8087267ffc033c15788a4a`
- Data SHA-256: `74e3a5a4f7cd3bfe49655da42594e550314acfc0bc44f71ab7f1f035af3b75b3`
- Browser: Chrome 152.0.7977.84, Windows desktop, 844×390 landscape and 390×844 portrait check
- Actual WebGL renderer: ANGLE / NVIDIA GeForce RTX 4070 SUPER / Direct3D11. This is a hardware desktop functional run, not a SwiftShader CPU performance claim.
- Machine-readable evidence: `reports/qa/release-20260913-web-20260913-113643/report.json`

## Results

| Requirement / acceptance | Status | Evidence / actual result |
|---|---|---|
| G07, P01 — third-person spawn and mobile-landscape UI | **PASS** | `landscape-start.png` shows the avatar from behind on the playable start surface; no custom camera-inside-avatar evidence was used. |
| G02 — direct road/bridge traversal, no teleport | **PASS** | Real W plus Shift input reached bridge X=145.46 at Y=2.82, then prayer vicinity X=461.88/Y=6.86. `bridge-crossed.png` visibly shows avatar above the deck floor with rails. |
| G03 — prayer interaction | **PASS** | `prayer-approach.png` shows the nonblank shrine photo and visible ไหว้พระ control; E entered Active, map pause held prayer progress constant, then completed exactly once and restored movement. |
| G04 — map bounds/pause | **PASS** | Actual minimap click opened the full map and BACK closed it; diagnostics show paused state while map is open. `map-open.png` keeps the route/map inside the visible panel. |
| P01 — orientation pause/resume | **PASS** | Portrait overlay was visible. Over 900 ms the active seconds and player vector were unchanged; landscape resumed afterwards. |
| P01 — touch input | **PASS (desktop emulation only)** | Real pointer drag on the move pad advanced X from 0.0 to 4.90. Physical Android/iPhone remains **NOT RUN**. |
| G06 — return | **PASS** | After road return movement, tester opened the actual Settings menu and clicked its visible RETURN button. Player reset to X=0 without SendMessage/state setter. |
| Night readability | **PASS** | `night.png` and `bridge-crossed.png` retain a readable avatar/road edge, lit landmark and HUD. Night diagnostics reported street/headlight/cabin lighting. Daylight was restored through the visible TIME UI for the bridge/prayer composition proof. |
| Console/page errors | **PASS** | Harness recorded none. |

## Evidence images

- `reports/qa/release-20260913-web-20260913-113643/landscape-start.png`
- `reports/qa/release-20260913-web-20260913-113643/night.png`
- `reports/qa/release-20260913-web-20260913-113643/map-open.png`
- `reports/qa/release-20260913-web-20260913-113643/bridge-crossed.png`
- `reports/qa/release-20260913-web-20260913-113643/prayer-approach.png`

## Remaining gate

**NOT RUN:** the same final build needs one live-URL run after deployment and a physical Android Chrome and/or iPhone Safari session before claiming real mobile acceptance. These are separate from the local desktop PASS above.
