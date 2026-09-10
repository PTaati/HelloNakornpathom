# HNP-WORLD-008 — solid monument and night lighting

Build: `builds/world008-r4/web`. Source reference: user-supplied `ref/jd-night.jpg`, interpreted as stylized amber contour lighting and warm-white front shrine, not an exact surveyed installation. No reference photo was modified or copied into a game texture.

## Changes

- Replaced the legacy CapsuleCollider on `Chedi solid core` with a static flat-sided cylinder MeshCollider, radius 23 m, height 50 m, bottom below ground. Added mesh collision matching the actual shrine/monument surfaces. The old capsule's rounded bottom left a large gap inside the broad visible base.
- Added automatic night lighting driven by the existing accelerated day/night clock: ten existing street-lamp heads and downward light pools, paired headlights on 18 moving cars, restrained red tails, warm window/interior illumination, gold Chedi bell ribs/base/collar/spire rings and separate front shrine floods.
- Lights are shadowless, capped at three landmark floods + four nearest street lights + eight nearest vehicle lights. URP permits up to eight additional lights per object. Emission/outline cues remain visible on all cars/monument when distant; actual illumination uses the bounded selection. These budgets are implementation limits, not a claim of phone performance.
- Found and repaired a source vehicle UV defect: merged glass retained a `Palette` UV layer while other parts used `UVMap`; exported UV0 therefore pointed at the wrong palette cell. Repaired Blender copies/FBXs preserve geometry and material budgets, with 24 corrected loops per sedan/hatchback/pickup and 48 per minibus. Original v003 `.blend` files remain untouched; existing Unity asset paths and `.meta` GUIDs are preserved.

## Main paths

- Runtime: `hnp-game/Assets/_HNP/Scripts/World/HnpNightLighting.cs`, `HnpWorldLife.cs`; `Art/Shaders/HnpNightGlow.shader`.
- Editor: `HnpWorld003Integrator.BuildNight008`, `HnpCollision008Tests.cs`; saved world scene and Mobile_RPAsset.
- Vehicle source/export: `art-source/hnp-world-008/`, `art-export/hnp-world-008/`; corrected future-export UV naming in `art-source/hnp-world-003/build_assets.py`.
- Runtime emission mask: `hnp-game/Assets/_HNP/Art/World003/VehicleNightEmission.png`, generated from the existing palette's lamp/window cells, linear color space.
- Reproduction: `tools/test_world008_night.py`; local server restart `tools/serve-world003.ps1`.

## Tests and evidence

| Check | Result | Evidence |
|---|---|---|
| UV source/export review | PASS | `reports/reviews/HNP-WORLD-008-uv-review.md`, export `vehicle-uv-manifest.json`, four real Blender previews |
| Independent final reference/visual review | PASS | `reports/reviews/HNP-WORLD-008-final-review.md`; scoped desktop night/day/portrait evidence |
| Four cardinal directions × walk/run × grounded/jump | PASS | 16 CharacterController probe cases using a translated copy of the actual boundary; `reports/world/world008-collision.json`. Minimum/final radius 23.3599854 m in all cases |
| Collider wall heights | PASS | 12 cardinal rays at ground/base/jump heights, `reports/world/world008-build6.log` |
| Unity import/compile/build | PASS | Same build log, `Build Finished, Result: Success` |
| Actual Web route collision and recovery | PASS | `reports/world/world008-night-20260910-214807/report.json`: player held at x=26.449997 before and after jump; retreat to x=22.129997 succeeds |
| Night/day light switching and counts | PASS | Same JSON: night emission 1.7, 10 street / 36 headlight / 18 cabin fixtures, 18 attached cars, at most 15 active lights; daylight emission/active lights return to zero |
| Desktop night/day/portrait render and errors | PASS | Same folder screenshots; Chrome 152.0.7977.83 software WebGL, 1280×720 and 390×844. Zero page/console errors |
| Physical Android/iPhone, sustained performance and full traffic-loop regression | NOT RUN | Viewport emulation is not phone validation. Older traffic-loop PASS applies only to its earlier build |

WASM SHA-256: `fc40e980520263d63bbcf9b01d8963751a0801735e1ab030930d88f75af450ef`.

The shader/intensity/UV fixes were iterated using actual renders. Earlier compile/test/visual failures remain in their timestamped files; the r4 paths above identify the delivered revision. The independent final visual review is recorded separately in `reports/reviews/HNP-WORLD-008-final-review.md`.

## Try it

Open http://localhost:8081 and hard-refresh the older tab. Start exploration, walk toward the Chedi and hold forward/run/jump against its front boundary; it should stop the player and allow retreat. Open the top-left menu and switch time to night to see lights immediately, or allow the 144-second day cycle to advance naturally. Daytime switches the new lighting off. Sprint/cooldown, Thai UI and 90-degree upward camera remain unchanged.

Known limitation: close passing traffic can occupy much of the already-close third-person camera view. This predates the lighting task; no new traffic avoidance/vehicle gameplay collision system was introduced. No public deployment performed; the preview server is local-only.
