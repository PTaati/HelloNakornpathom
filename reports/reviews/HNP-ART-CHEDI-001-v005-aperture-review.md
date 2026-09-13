# HNP-ART-CHEDI-001 v005 aperture — Independent narrow review

**Decision:** **PASS — approve M03 aperture repair for Unity staging.**  
**Scope:** M03 `ReferenceFacade` v005 only; M01/M02/M04 remain the separately reviewed v004 assets. Unity import, collisions, play path and mobile Web are **NOT RUN**.

## Evidence inspected

- `art-export/HNP-ART-CHEDI-001/manifest-v005-aperture.json`
- `HNP_Chedi_v005_open-prayer-corridor.png`
- `HNP_Chedi_v005_three-quarter.png`
- `HNP_Chedi_M03_ReferenceFacade_v005.fbx` SHA-256 independently recomputed as `A7314E802D190845D75F1FEC4BEC013D6A87C0B0FF8884F1CD22390396D7BD90`, matching manifest.

## Result

| Check | Status | Observation |
|---|---|---|
| Prayer corridor obstruction fixed | **PASS (visual + reported geometry)** | The straight corridor preview has uninterrupted floor and clear side liners to the prayer photo/altar; no decorative full annulus visibly crosses the player centreline. Manifest reports no centreline obstructions. |
| Surface treatment after repair | **PASS (scoped visual)** | Current corridor render shows clean white liners without the earlier Boolean cutter-cap triangulation flecks. Retain surface-only clipping; do not reintroduce cutter caps. |
| Prayer reference/photo | **PASS (scoped visual)** | Prayer photo, frame, altar step and long approach remain intact/readable. |
| Exterior regression | **PASS (scoped visual)** | Three-quarter silhouette remains intact. It is darkly lit, so this image is not a full exterior lighting approval, but no M03-aperture regression is evident. |
| Export integrity | **PASS (reported + hash)** | v005 reports 8,385 triangles, five meshes, zero degenerate faces, no missing UVs, and matching roundtrip bounds. |
| Survey/access fidelity | **NOT RUN** | Opening remains an authored adaptation, as manifest declares; not a surveyed historic interior claim. |
| Unity/collider/playable corridor | **NOT RUN** | M03 FBX must be imported with the authored visible route/collider contract and exercised at player height. |

## Handoff note

Approve this **narrow M03 repair** for integration. Keep the surface-only opening as delivered; any future exterior lighting pass is separate and must not delay the aperture fix. Unity must validate the visible floor/threshold and player capsule through the corridor before marking traversal PASS.
