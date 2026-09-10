# HNP-WORLD-009 — read-only integration audit

Date: 2026-09-10. Scope is source/serialized-scene inspection only; no Unity, CLI, asset, scene, or tool action was performed.

## Current ownership and replacement boundary

`NakornpathomWorld.unity` has exactly two relevant independent scene roots:

- `Town — map reference`: a prefab instance of `Assets/_HNP/Art/World/HNP_Town.fbx` (scene source GUID `2f2cf5d7ba6c61543bb60751ddd36729`) at origin, with X scale `-1`. The Builder adds `MeshCollider`s only to child `MeshFilter`s whose names begin `COLL_`; it disables those renderers. Therefore the visible Town is otherwise imported/merged geometry, not separately editable scene buildings/terraces.
- `Phra Pathom Chedi`: separate prefab instance (scene source GUID `a77a1fbd0bfd4cd4fac3947d63850d53`), world position `(53, 2.9, 0)`, plus a separate `Chedi solid core` collider at `(53,23,0)`, scale `(46,25,46)`. The scene additionally has four MeshColliders on Chedi submeshes.

There is no existing named cloister/terrace root to selectively delete around radius 31–34. A scene-only deletion of individual Town geometry is unsafe because the FBX is merged and collider children are identified by naming convention, not functional area.

### Recommended removal/replacement options

1. **Preferred — preserve Town asset GUID and all route collision:** export `HNP_Town_v009.fbx` with only the obsolete temple-radius visible geometry removed, then copy/import it at the existing `Assets/_HNP/Art/World/HNP_Town.fbx` path while preserving its `.meta`. The Town source GUID remains stable. Keep every `COLL_` child for station, canal, roads, bridges, and outer plaza; explicitly retain the central road and temple approach collision.
2. **Lowest-risk visual overlay:** leave Town and its colliders untouched; add v009 cloister as a separate root centered on `(53,2.9,0)` and hide only identified obsolete renderer submeshes after reviewing imported `MeshFilter` names/bounds. Do **not** delete the Town root. This avoids breaking station/road collision but may create z-fighting where the old merged visual remains.
3. **Avoid:** `DestroyImmediate(oldTown)` followed by instantiate, as current `HnpWorld003Integrator.Integrate` does. It recreates the scene root and does not itself preserve scene-instance identity or existing added collider components. It should only be used with a documented scene backup and full traversal/collision retest.

## Chedi/rich-cloister integration constraints

- Do not alter `Chedi solid core` while adding a **walkable** radius-31–34 cloister: the current core's scaled cylinder is the authoritative anti-penetration boundary and collision tests expect it.
- Place rich cloister visual paths outside the core collision envelope and use a separate annular path collider only if it is a continuous, walkable surface. Avoid a ring of individual colliders that can snag the CharacterController.
- Preserve the landmark root transform: Chedi export is expected local center/ground at zero and scene placement remains `(53,2.9,0)`. Any new cloister uses the same center; do not bake a second world offset.

## HnpNightLighting hazards

`HnpNightLighting` currently assumes the legacy Chedi silhouette and material set.

- `Awake` immediately constructs materials from `vehicleAtlas` and `glowShader`; either missing reference throws before the scene is playable. Require both after import.
- `Start` uses `GameObject.Find("Phra Pathom Chedi")` with no null guard and constructs ribs/rings from fixed radii/heights (base radius 22.8 down to spire height ~42). A new cloister will not automatically gain lighting, and a changed Chedi profile can cause floating or embedded light lines.
- It obtains `r.materials`, enables emission, and retains material instances. Verify every replacement material supports `_EmissionColor`; otherwise night writes can warn or fail visually.
- Fixed flood/portico coordinates assume the old entrance location. Re-aim after inspecting the new Chedi entrance and ensure spot lights do not illuminate the station/road through walls.
- `LogNightDiagnostics` dereferences `Chedi solid core`; preserve this object/name or revise the diagnostic before QA.

## Required integration checks

1. Import audit: no missing mesh/material/controller references; Town `.meta` GUID unchanged if path-replaced; record new model bounds, root/axis, collider count and renderer count.
2. Cloister path: CharacterController walks clockwise and counter-clockwise at radii 31, 32.5, and 34, including all joins; jump/land at each quadrant; no climb into Chedi core, no seam snag, no fall below ground.
3. Route regression: station → canal → central road → temple entry, plus north/south outer bridge routes. Confirm existing `COLL_` road/station geometry remains after any Town update.
4. Night: capture day/night at four cardinal cloister points; check new path lighting, Chedi rings/portico alignment, material emission, and no flood-light leaks.
5. Performance: measure active extra lights/LineRenderers at cloister camera and verify the existing fixture culling still reserves road lights.

Status: **ADVISORY ONLY / NOT RUN** for import, collider, Play Mode, Web, and mobile checks.
