# HNP-WORLD-002 — Web test delivery, 2026-09-10

## Build and launch

- Unity 6000.6.0f1; scene `Assets/_HNP/Scenes/NakornpathomWorld.unity`.
- Output: `builds/web`; local-only server `http://127.0.0.1:8080/` (Python process 30836 at handoff). HTTP 200 and WebAssembly MIME `application/wasm` verified.
- Build PASS: 0 errors, 357 warnings, 49,864,607 bytes, 61.02 seconds. Authoritative summary: `reports/world/build-20260910-194823.txt`; full log: `reports/world/world002-release-build.log`.
- WebAssembly SHA256: `831C7CB55BADEF82E42439D0D599EEE86CB960BFA89930E21D8708C91500124C`.
- If the local server stops, run from the repository root: `python -m http.server 8080 --directory builds/web --bind 127.0.0.1`. No public deployment or Git push was performed.

## Changes

- `hnp-game/Assets/_HNP/Editor/HnpTravellerV002Integrator.cs`: safe scene checkpoint, serialized visual-root lookup, legacy driver removal, preserved controller/prefab identities, looping Idle/Walk import, model-root Animator, integration/build entry point.
- `hnp-game/Assets/_HNP/Scripts/World/HnpTravellerAnimatorBridge.cs`: finds the child Animator and feeds player speed into Idle/Walk transitions.
- `hnp-game/Assets/_HNP/Scripts/World/HnpWorldGame.cs`: portrait-capable gameplay, input reset on rotation, responsive HUD/control spacing and sizing, Start initializes daylight, music no longer suspended merely by portrait orientation.
- Traveller FBX and Unity-generated metadata, `HNP_Traveller_Child_v002.controller`, `Traveller_Child_v002.prefab`, and `NakornpathomWorld.unity` integrated. Source/export: `art-source/hnp-world-002-traveller/` and `art-export/hnp-world-002-traveller/`; original Blender-made asset, not generated bitmap art. FBX GUID retained: `5bff754cb7d1a9948b1c51f2e9f78d6d`.
- `hnp-game/Assets/WebGLTemplates/HNP/index.html`: no portrait blocker or forced landscape fullscreen; fullscreen button avoids gameplay controls and hint text.
- `hnp-game/Assets/_HNP/Editor/HnpWorldBuilder.cs`: timestamped build summaries, with fallback when Windows locks the previous `build.txt`.
- `tools/test_world_web.py`: waits for the splash, uses frame-visible press/release intervals, tests TIME/SOUND and portrait, and writes each test to a new evidence folder.

## Validation

Environment: Windows desktop, Chrome 152.0.7977.83, headless WebGL2/SwiftShader. Viewports 1280x720, 844x390 and 390x844; these are not physical phones. Fresh browser context, no saved progress prerequisite. Root performed integration and this smoke review; this is not a new independent art sign-off.

Current evidence: `reports/world/web-test-20260910-194920/`, especially `web-smoke.json`. Earlier retries are retained and are not the authoritative final result.

| Check | Status | Expected / actual and evidence |
|---|---|---|
| Unity compile and Web build | PASS | Integration and build completed; current timestamped summary above |
| Traveller import, scale and materials | PASS | 1.310976 wrapper import scale, looping Idle/Walk metadata, visible model without magenta/missing materials; `web-walking.png`, `web-idle.png` |
| Basic walk to idle | PASS | Hold W for 2.2 seconds, release for 0.6 seconds; character advances and returns to neutral sampled pose. This does not prove every collision/animation edge case |
| Browser load and script errors | PASS | Unity instance starts; no page errors or console errors; `web-smoke.json` |
| Portrait and landscape restoration | PASS | Rotate viewport and restore; canvas remains visible, no rotate blocker, separated controls; `web-portrait.png`, `web-landscape.png` |
| TIME control | PASS | Click TIME: scene illumination darkens and label becomes NIGHT; click again restores warm daylight; `web-night.png`, `web-muted.png` |
| SOUND UI state | PASS | Click SOUND: MUTED appears; click again restores ON; `web-muted.png`, `web-portrait.png` |
| Actual audible output quality | NOT RUN | Headless browser did not provide a listening test |
| Editor Play Mode tests | NOT RUN | Used an automated integration/build session and the actual Web player instead |
| Full traversal, simultaneous multitouch, physical-phone safe areas/performance | NOT RUN | Requires targeted regression and real Android/iPhone hardware |
| Final art/reference-completeness gate | FAIL | Current cars/train/birds remain primitive provisional geometry. Full detailed city/vehicle art and a convincing night sky/lighting pass remain outstanding |

Warnings are not zero: the build includes package shader warnings (for example Sentis integer-modulus warnings), obsolete API warnings, and browser notices about stripped/unsupported postprocessing effects. No package upgrade or cache modification was used to suppress them.

The previous intermediate build succeeded but could not overwrite locked `build.txt`; one smoke retry also hit a locked screenshot. Timestamped reporting/evidence resolved those reporting failures. The final build and test both completed.

## How to reproduce manually

1. Open the local URL and press START. WASD/arrows move, Shift runs, Space jumps; drag the right side to look.
2. Release movement and verify the traveller settles to idle; repeat movement and stop near a wall.
3. MAP/M opens the map; BACK returns. HOME returns to the station.
4. TIME changes the time; SOUND toggles the procedural chime loop. Audio starts only after START.
5. Try both orientations. On touch screens use the left pad, right camera area and JUMP/RUN buttons.

This handoff is a runnable test build, not a claim that all earlier requested reference-quality art and real-mobile release criteria are complete. Next: user playtest, then final vehicle/city art, night-sky polish and physical-mobile regression.
