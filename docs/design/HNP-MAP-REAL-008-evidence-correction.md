# HNP-MAP-REAL-008 — Evidence correction: direct station–Chedi corridor

**Status:** IMPLEMENTATION BASELINE — replaces conflicting route/bridge and forced-reveal wording in MAP-REAL-001 and MAP-REAL-004. **Reason:** current source and map cross-check evidence establish a direct north/south Rotfai Road corridor and the historic Charoen Sattha (`สะพานเจริญศรัทธา` / Saphan Yak) context. The earlier invented 50 m × 12 m bridge, multi-turn procession, gate-first reveal rules, and numeric Chedi-visibility percentage are not user requirements or ground-supported geometry and must not drive production.

## Evidence hierarchy

1. **Current implementation geometry:** a dated OpenStreetMap extract, project references, public historical sources, and original authored meshes may be combined for the game. Credit [OpenStreetMap under its ODbL terms](https://www.openstreetmap.org/copyright) when its data is used. A field/right-cleared survey improves exact placement, present condition and access claims, but is **not** an approval gate for an original reference-led game map the user has authorized.
2. **Named bridge/historic context:** Silpakorn University's Western Region Information Center article, [“เจริญศรัทธา...สะพานแห่งศรัทธาของผู้เจริญ”](https://snc.lib.su.ac.th/westweb/?p=1644) (published 2018; updated 2021), describes Charoen Sattha/Saphan Yak as about 130 m from the station and gives historical dimensions 4 wa 1 sok (8.5 m) wide by 17 wa 1 sok (34.5 m) long. It also informs the four yak-bearing pavilion-column character. This supports a reference-led game asset; it is **not** a contemporary structural/access survey.
3. **Google Maps visual/navigation cross-check only:** current visual inspection by the project recorded station datum `13.824375, 100.0594199`, road/canal north-south alignment, and a direct station-to-temple corridor. Do not copy Google tiles/imagery/labels/geometry or treat this as surveyed path permission.
4. **Project aerial references:** `ref/game-document/image1.png`/`image2.png` support broad station–canal–town–Chedi relationship only. They are not texture or mesh sources.

When sources conflict, prefer dated OSM/field evidence for real-route claims; retain the bridge article for historic visual language and use original authored geometry where evidence has no exact mesh. Truthful place names such as `สะพานเจริญศรัทธา` and `สะพานยักษ์` may be used. Label only unverified present-day access, exact-survey dimensions/placement, and architectural detail `provisional`.

## Corrected scale and coordinate contract

| Datum | WGS84 | Approx. local offset from station | Use |
|---|---:|---:|---|
| Nakhon Pathom Station | `13.824375, 100.0594199` | origin | corrected visual-map datum; verify physical exit node |
| Wat Phra Pathom Chedi landmark | `13.8197278, 100.0600570` | E `+69.2 m`, N `-514.2 m`; straight-line `~518.8 m` | landmark only; verify public exterior threshold |
| Charoen Sattha / Saphan Yak | `~130 m` from station (article description) | corridor stationing `X≈130 m`, pending OSM/field placement | visual landmark / crossing candidate |

For the playable scene, use an **authored direct-route local axis**: Station exit `X=0`; Chedi exterior/prayer vicinity `X≈519`; `+X` is station→Chedi. Do not reuse MAP-REAL-001's MapB rotation as a runtime authority: its sign convention was not validated in Unity and can place the destination on the wrong X side. If a geo-to-Unity transform is needed, Unity must record the tested transform/axis once against the station and Chedi anchors; prior analysis indicates the required signed rotation is approximately `-82.35°` under the project’s Unity convention, but direct authored `+X` is safer until that check exists.

## Minimal implementable route and bridge

- Build one continuous, visibly paved road/sidewalk route: station forecourt/Rotfai Road exit `X=0` → town/canal approach → bridge stationing near `X=130` → direct urban road → verified temple exterior entry/prayer vicinity around `X=500–519`. Curves only where the dated map/field route requires them; no invented L-corners or hidden loading/teleport jumps.
- Replace the 50 m × 12 m invented deck with an **8.5 m × 34.5 m reference-led bridge envelope**. Its exact alignment, deck profile, present condition, and pedestrian permission remain `provisional` until source geometry/field check. Keep collision/path surface visibly matched to the rendered deck; do not substitute an invisible nav corridor.
- Bridge hero traits: four yak-bearing pavilion-column positions, a compact bridge approach, credible parapet/rail, canal banks/waterline, direct road continuation, modest wayfinding/signage after copy approval. It must read as a named local landmark, not a generic extra-wide elevated highway.
- Preserve station/platform reference-led construction and contextual town fronts. Do not force the Chedi out of view. Natural sightlines determined by direct road, building mass and bridge context are acceptable. The separately reviewed Chedi asset is authoritative; route-kit proxies cannot alter its scale or claim a surveyed temple model.

## Scope and acceptance

The route evidence in this packet supports continuous exterior travel and an exterior prayer point. The user-requested upper/lower and interior exploration may be authored as a clearly-labelled game simulation now; exact-survey fidelity and present-day access conditions remain `NOT RUN`/provisional until stronger evidence exists. Gate accessibility/hours likewise remain unverified, not a prohibition on the modeled simulation.

| Check | Status / acceptance |
|---|---|
| Direct station→road→bridge→Chedi route | NOT RUN — player walks/runs from station exit across one visible physical route; no teleport or dead-end collision. |
| Charoen Sattha bridge art | NOT RUN — 8.5 × 34.5 m envelope, compact direct-road placement, four yak pavilion-column reading, and canal/road context visible from gameplay camera. |
| Road/bridge traversability | NOT RUN — play evidence demonstrates pavement/deck/ramps/rails/banks colliders match visual geometry; bridge width clearance documented by scene owner. |
| Prayer | NOT RUN — exterior trigger point and entry/exit state recorded by Unity diagnostics; no interior/upper/lower claim. |
| Source fidelity/access | NOT RUN — exact-survey/field confirmation is unavailable; original reference-led game geometry may proceed with `provisional` labels. |
| Visibility | NOT A RELEASE GATE — record observed direct-route composition, but do not impose fabricated P0–P5 hiding percentages. |

## Required revisions to existing handoffs

- MAP-REAL-001 coordinates use a superseded station longitude (`100.058270`); do not use it for new placement.
- MAP-REAL-004’s multi-turn spline, bridge P4–P6 50 m/12 m contract, and numerical P0–P9 reveal rules are superseded.
- HNP-ART-MAP-005’s visual reset remains valid for material/detail quality, but its 50 m bridge/forced visual sequence is superseded by this document.
- Future art/Unity manifests must cite this correction, list source/version, and retain `provisional` labels where field evidence is absent.
