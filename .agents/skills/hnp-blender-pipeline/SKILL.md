---
name: hnp-blender-pipeline
description: Create, refine and validate Blender source assets and FBX exports for Hello Nakornpathom. Use for mesh, UV, materials, rigging, animation and export tasks; use hnp-design-qa for independent art review.
---

# Blender production for Hello Nakornpathom

Use the project root containing `AGENTS.md` and `hnp-game/`. Read `docs/agents/TEAM.md` for ownership and `GAME_PRODUCTION_PLAN.md` sections 1–3 for art direction, asset budgets and export contracts. For map work, read the extracted game document and `docs/design/MAP_LAYOUT.md`; references are in `ref/` and must remain unchanged.

## Before creating geometry

Inspect the actual `.blend`, export scripts, manifest and source images for the assigned asset. Resolve brief fields that affect the geometry: player scale, silhouette, camera distance, pivot, traversal/collider clearance, reference provenance and animation needs. Mark invented architectural details provisional. Prefer refining the current source over replacing an asset whose identity and GUID Unity already uses.

Discover callable Blender tools. A previous check found `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`; verify its existence/version rather than assuming it persists. Without MCP, use Blender background Python on an explicit input or new file. Do not write over the GUI's open source when dirty state cannot be established; write a separate task revision and hand it off. Scope object cleanup to the task collection.

## Quality and export decisions

- Approve the silhouette/proportions through task review before detailing. Use both a three-quarter preview and a view approximating the gameplay camera; test small-screen readability, not just a close-up render.
- Check evaluated geometry after modifiers: triangles, degenerate/duplicate faces, normals, intended open surfaces, UV distortion/seams and material slots. Do not blindly reject intentional open/non-manifold props or remove silhouette-critical geometry just to meet a number.
- Use meter units and the agreed pivot. Apply transforms with care around armatures; compare rest pose and animated poses after export. Test deformations at joints and clothing/attachments through required extreme poses.
- Shader nodes do not transfer as Unity materials. Bake necessary procedural appearance, use shared palettes/atlases where suitable, and state texture color-space intent. Capture missing textures as a failure.
- Export selected production meshes/armature to `art-export/<asset-id>/`. The plan's starting axis preset is -Z forward, Y up, no added leaf bones; calibration and round-trip results decide the final preset. Export only intended clips and record frame rate/ranges and root-motion intent.
- Re-import into a separate Blender scene/file and compare bounds, orientation, material slots and required animation. Never infer a skinned rig from procedural rigid-limb movement in the existing Traveller.

## Handoff

Keep `.blend` and source textures/scripts in `art-source/<asset-id>/`. Deliver FBX/textures, preview, reference paths and manifest containing revision/hash, units, dimensions, axis/pivot, evaluated triangles, materials, texture sizes, rig/clips and collision intent. Label measurements from old manifests as historical until re-measured.

Send visual review to Designer/QA, then export integration to Unity Engineer. Blender checks may PASS while Unity prefab validation is NOT RUN; preserve that distinction. A source mesh fix belongs here, while Unity shader/import/collider issues belong to the integrator. Do not import into Unity Assets yourself.
