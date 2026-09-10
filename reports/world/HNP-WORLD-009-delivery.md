# HNP-WORLD-009 delivery

Build: `builds/world009-r2/web` (Unity 6000.6.0f1).

## Changes

- Reviewed all 75 supplied field photos plus overall, Buddha, style, night and map references. Architectural interpretation: `docs/art/HNP-WORLD-009-reference-brief.md`.
- Rebuilt bell, collar openings, ribbed spire, white base railing, pointed front sanctuary and standing Buddha; added ceramic surfaces, courtyard paving and orange/green-roofed arched cloister.
- Removed only the old Town cloister islands; preserved other Town geometry and its collision mesh. Original reference photos untouched.
- Imported new models/materials, retained existing Chedi/Town GUIDs, regenerated minimap, fitted night-light outlines to the new model profile.
- Corrected arcade jamb intrusion found in r1; r2 retains all four clear stair entrances.

Sources: `art-source/hnp-world-009/HNP_TempleArt_v009.blend`, `HNP_Town_v009.blend` and reproducible generators. Exports, triangle/material/UV/bounds reports and round-trip hashes: `art-export/hnp-world-009/manifest.json`, `roundtrip.json`, `town-cleanup-manifest.json`.

Implementation: `HnpWorld009Integrator.cs`, `HnpTemple009Tests.cs`, `HnpNightLighting.cs`, world scene/prefab, World009 materials/textures, existing Chedi/Town FBX asset paths and minimap. Tests: `tools/test_world009_reference.py`, build-parameter support in `tools/test_world007_sprint.py`.

## Verification

- PASS build: `reports/world/world009-build2.log`.
- PASS import: `world009-integration/scene-validation.json` — 45 static meshes, 77,130 static triangles, zero missing references. Counts exclude runtime traffic/birds and player.
- PASS collision: `world009-integration/collision.json`; four cardinal stair routes (zero gate deviation) and two upper court arcs in `temple-routes.json`.
- PASS real Web input/reference regression: `world009-reference-20260910-225000/report.json`, including 10 game minutes/second, static idle, overhead camera, portrait/landscape, map and menu pause.
- PASS night/collision Web regression: `world008-night-20260910-225051/report.json`, day/night lighting, vehicle cabin/headlights, blocked inward movement/jump and retreat.
- PASS sprint/cooldown regression: `world007-sprint-20260910-225153/report.json`, including disabled-button countdown and portrait layout.
- PASS independent final visual review: `reports/reviews/HNP-WORLD-009-final.md`; r1 front-gate blocker resolved.
- Browser: desktop headless Chrome 152.0.7977.83, software WebGL; physical mobile and hardware performance NOT RUN.
- WASM SHA256: `fe1954193cc5fe0588dd63fa0fd68269f6558cf711799c8eeb34fb428e9699ef`.

## Replay

Start local server with `tools/serve-world003.ps1`, open `http://localhost:8081`, press the Thai start button. Walk along the central road toward the Chedi, climb the front stairs and try all four entrances. The solid Chedi must stop movement while the courtyard remains traversable. Drag to look upward; use the upper-left menu to toggle night and inspect the temple and moving cars. Tap the minimap to expand. Run lasts five seconds, followed by a five-second disabled-button cooldown. Rotate the viewport and repeat.

## Limits

The architecture is reference-led stylized game art, not a measured reconstruction. Distances and repeated decorative details remain gameplay-compressed/provisional. Surrounding city traffic, character proportions and unrelated map buildings were preserved, not remodeled in this task. r1 and initial detail previews were rejected and are not the delivery build. The current Unity version logs a forward-looking mesh pre-bake warning; current build succeeds and collision checks pass.
