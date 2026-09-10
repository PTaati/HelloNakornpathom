# HNP-WORLD-003 — Web delivery

Date: 2026-09-10. Build: `builds/world003-r3/web`. Local preview: http://localhost:8081 . Port 8080 is an older build; do not use it for this acceptance test.

## Implemented

- Rebuilt the landmark in Blender from `ref/jd.jpg` and `ref/style.jpg`: broad stepped base/bell, narrow open collar, ribbed spire and contrasting ivory standing-Buddha portico facing the station. Architectural ornament is stylized, not a measured restoration.
- Four vehicle bodies (sedan/taxi, hatchback, pickup, minibus), six body colors, detailed windows/lights/wheels. Removed old static cars from the merged town source. Eighteen moving vehicles follow rounded closed road routes with spacing checks and rotating wheels.
- Twelve modeled pigeons with recognizable head/beak/body/tail/wings, randomized destinations and flapping/banking. Two-car train moves along the station rail.
- New authored Run clip alongside Idle/Walk, correct non-preview Animator clip bindings, immediate zero-speed parameter on stop, no root motion. Imported rig preserves the reviewed traveller's proportions.
- Thai Sarabun UI; icon jump/run, no HOME/fullscreen/standalone MAP control, top-left hidden time/music menu, tappable minimap, portrait and landscape layouts.
- Warm sky/sun/ambient palette and improved shadows; night toggle and existing generated music with mute. No external audio service or downloaded music.

## Main changed paths

- Sources and generators: `art-source/hnp-world-003/` (`build_assets.py`, `add_run.py`, `clean_town.py`, `.blend` files).
- Exports, previews, budgets and roundtrip manifests: `art-export/hnp-world-003/`.
- Runtime: `hnp-game/Assets/_HNP/Scripts/World/HnpWorldGame.cs`, `HnpWorldLife.cs`, `HnpWorldThaiUi.cs`, `HnpTravellerAnimatorBridge.cs`.
- Integration/build: `hnp-game/Assets/_HNP/Editor/HnpWorld003Integrator.cs`, `HnpWorldBuilder.cs`; corresponding world scene, chedi prefab, World003 imports/materials/Animator, cleaned town FBX, Mobile_RPAsset and sunset shader.
- Font: `hnp-game/Assets/_HNP/UI/Fonts/Sarabun-Regular.ttf`, licensed by accompanying `OFL.txt` (Google Fonts/Cadsondemak).
- Web template: `hnp-game/Assets/WebGLTemplates/HNP/index.html`.
- Reproduction: `tools/test_world003_web.py`, `tools/serve-world003.ps1`.

## Evidence and status

| Check | Result | Evidence |
|---|---|---|
| Blender staging/reference and export budgets | PASS | `reports/reviews/HNP-WORLD-003-staging-review.md`; export manifests |
| Independent final desktop visual review | PASS | `reports/reviews/HNP-WORLD-003-web-review.md`; no visual must-fix blocker, exact historical fidelity not claimed |
| Unity import / three real animation clips / Thai font | PASS | `reports/world/world003-build4.log`, `HNP003_INTEGRATION_PASS` |
| Unity Web build | PASS | Same log, `Build Finished, Result: Success`; 50,366,718 bytes total output including final loader stylesheet correction |
| 18 cars / 12 birds move; wing poses change | PASS | `reports/world/world003-web-20260910-203824/report.json` |
| Walk → Run → Idle / idle position stable / run off | PASS | Same JSON, Animator states plus controller positions; corresponding screenshots |
| Minimap, settings, day/night, music mute state | PASS | Same JSON and expanded-map/settings/night/muted screenshots |
| Portrait / landscape restoration | PASS | Desktop Chrome viewports 390×844 and 844×390; portrait/menu/map and landscape screenshots |
| Extra 32-second traffic road bounds sampling | PASS | `traffic_loop_0`…`traffic_loop_7` snapshots; this is sampled road containment, not exhaustive all-route collision proof |
| Browser page/console errors | PASS | Zero errors, Chrome 152.0.7977.83, software WebGL |
| Thai loading overlay before Unity download completes | PASS | `loading-portrait.png`; final CSS mirrored in source template and exported HTML, 390×844 overlay verified with loader delivery held by test |
| Real Android / iPhone, sustained mobile FPS, audio listening quality, train full-cycle/minigame handoff | NOT RUN | Desktop emulation is not physical-device acceptance |

WASM SHA-256: `c8d9dfbf533c23667c65451ff628b9cbf2dc973dd45f3192f5bcd81b5229758d`.

## Try it

Open http://localhost:8081 in this computer's browser. Press **เริ่มสำรวจ**, use the left joystick or WASD/arrows, drag the right side to look, tap the running-person icon to toggle running, and tap the jumping-person icon to jump (Space also works). Tap the minimap to enlarge it; use **กลับ** to close. Open the top-left hamburger to switch time/music. Rotate the viewport to check portrait/landscape.

To restart the local server: `powershell -File tools/serve-world003.ps1`. The server binds only to this computer (127.0.0.1); it is not an internet or phone-accessible deployment.

The earlier default `builds/web` had a locked loader during an attempted overwrite; it is not the delivered build. Fresh revision directories preserve earlier artifacts and avoid overwriting mapped files. Failed earlier test reports are retained for audit; the timestamped report above is the passing revision.
