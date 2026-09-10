# HNP-WORLD-002 — Living-world presentation pass

Status: Unity integration and test build delivered; broader art polish and physical-mobile acceptance remain OPEN.

## 2026-09-10 integration and Web delivery

This section supersedes the historical staging-only status below. See `reports/world/HNP-WORLD-002-web-delivery.md` for the current build and test evidence.

- Imported the rigged traveller, enabled looping Idle/Walk clips, created its Animator controller and wrapper prefab, and replaced the legacy pose driver in the world scene. Kept the existing FBX GUID and scene visual reference.
- Added portrait layout and removed both the Web rotation blocker and fullscreen landscape lock. Enlarged controls, separated MAP/TIME/SOUND, moved fullscreen away from gameplay controls, and cleared held input on orientation changes.
- Built the Unity Web player to `builds/web` and served it locally at `http://127.0.0.1:8080/`.
- Current runtime includes moving traffic/train/birds, a manual TIME control, an automatic time cycle and Start-gated procedural music. Vehicle/bird geometry is still provisional, not final reference-quality art.
- Editor ownership: root used a clean automated Unity session; Unity exits after building. The pre-integration scene checkpoint is `reports/world/NakornpathomWorld.pre-v002.unity`.

## Historical staging record (superseded by the delivery above)

## Goal

Polish the warm stylized world and mobile-landscape HUD; make the traveller's idle/walk transition stable; add non-blocking traffic, a train, birds, market dressing, a day/night loop and Start-gated music. Preserve the station-left → canal/central road → chedi-right route.

## Inputs

- `ref/style.jpg`, `ref/jd.jpg`, `ref/jd-night.jpg`
- `docs/design/MAP_LAYOUT.md`, `docs/design/HNP-WORLD-002.md`
- Existing `NakornpathomWorld.unity` and HNP-WORLD-001 exports

## Delivered scope

- Runtime source: compact teal/gold HUD, 44px minimum interactive controls, Start-gated procedural chime audio/mute, 240-second daylight loop, deterministic collider-free cars/train/birds/market dressing, and pause behavior for focus, portrait and map overlays.
- Runtime pose source: filtered movement-to-idle limb blending; player root remains untouched.
- Traveller staging asset: a new rigged child traveller with in-place Idle and Walk clips. It is not imported into Unity yet and must use an Animator, not the legacy rigid-limb pose script.

## Ownership and handoff

- Editor owner: `none` — multiple Unity processes were detected and dirty/play state could not be established. No scene, prefab, import, ProjectSettings or build changes were made.
- Unity runtime report: `reports/world/HNP-WORLD-002-runtime-source-report.md`.
- Traveller source/export/contract: `art-source/hnp-world-002-traveller/`, `art-export/hnp-world-002-traveller/`.

## Acceptance status

| Check | Status | Evidence |
|---|---|---|
| Runtime source scope/static review | PASS | `reports/world/HNP-WORLD-002-runtime-source-report.md` |
| Blender source and FBX round-trip | PASS | traveller manifest and round-trip report |
| Independent design/source review | PASS with runtime execution pending | `reports/reviews/HNP-WORLD-002-source-retest.md` |
| Traveller independent visual review | PASS — source/export evidence | Cute silhouette/readability, budget and regenerated manifest/round-trip are consistent: Idle→Walk neutral-pose delta is now `0.0`; Unity import/playback remains NOT RUN. See `reports/reviews/HNP-WORLD-002-traveller-review.md` |
| Unity compile, scene/prefab import, Play Mode | NOT RUN | Shared Editor state was not safe to take over |
| WebGL/browser and physical mobile | NOT RUN | Need clean Unity integration and an actual build/device |

## Next safe step

After the current Unity Editor owner has saved/exited Play Mode and transferred ownership, import the staged FBX into a separate wrapper prefab at the documented provisional scale, wire its Animator clips, and run compile, traversal and day/night/audio Play Mode checks before making a WebGL build.
