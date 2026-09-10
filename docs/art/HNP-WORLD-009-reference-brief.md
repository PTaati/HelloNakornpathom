# HNP-WORLD-009 — photo-faithful Chedi / temple reference brief

**Task:** HNP-WORLD-009  
**Owner of this brief:** Design/QA; Unity and art-source mutation are out of scope.  
**Requirements:** G02 (route/temple approach), G07 (movement/camera), P01 (mobile Web landscape).  
**Purpose:** Replace the generic v003 landmark read with a recognisable, low-poly interpretation of the supplied real site photography while retaining the Chedi as the road-facing destination.

## Evidence hierarchy and what is factual

1. **Overall front silhouette:** `ref/jd.jpg` is the primary proportion reference; `ref/jd-night.jpg` controls night hierarchy. It shows a very broad circular lower mass, a rounded bell, a narrow transition/gallery, and a tapered ribbed spire. Do not derive macro proportions from a near-ground field photo alone.
2. **True front worship interior:** `ref/pra.jpg` shows the tall standing gold Buddha, deep red/brown vaulted ceiling, ornate gold pointed surround, white architectural frame, and flanking gold figures. This is **not** the same as a small side oval niche.
3. **Field-photo architectural detail:** all 75 new `ref/IMG_20211023*.jpg` files were inspected in chronological contact sheets. Key factual sets are below. They show the actual terracotta, white base, stairs, perimeter and side shrines; they do not provide a survey, so metres and unseen rear/interior detail remain **provisional**.

| Reference set | Directly observed design information |
| --- | --- |
| `IMG_20211023_160817`, `161058`, `161233`, `161311`, `161317`, `161723`, `162322` | Rounded bell; several strong lower terracotta moulding/ring courses; dark, repeated-bay/gallery transition; tall, regularly ribbed/tiered spire. `161311` and `161058` are the best close façade/profile evidence. |
| `IMG_20211023_160743`, `160905`, `160913`, `160926`, `161118`, `161123`, `161227`, `161447`, `161603`, `162201`, `162203` | White lower façade/cloister with pilasters, arch/oval openings, dark grillework, weathered stone, and repeated secondary standing-Buddha niches. These are perimeter/side details, not replacements for the primary front sanctuary. |
| `IMG_20211023_160750`, `160806`, `161010`, `161355`, `161357`, `161451`, `161510`, `161605`, `161710`, `161828` | Dark red-brown tiled/frieze bands, coloured cloth bands, roof/edge courses, decorative grille and paving palette. |
| `IMG_20211023_160454`, `160521`, `160944`, `161307`, `161339`, `161403`, `161420`, `161823`, `162159` | Perimeter rail, tall posts/gates, broad steps, courtyard circulation, guardian/statue context. |
| Remaining field files: `160436`, `160438`, `160533`, `160557`, `160718`, `160758`, `160802`, `160841`, `160844`, `160852`, `160953`, `160955`, `160958`, `160959`, `161037`, `161038`, `161120`, `161201`, `161207`, `161221`, `161236`, `161250`, `161254`, `161329`, `161343`, `161422`, `161443`, `161455`, `161457`, `161459`, `161511`, `161600`, `161633`, `161713`, `161735`, `161824`, `162157`, `162201`, `162203`, `162322` | Inspected as corroborating material, paving, wall, stair, gate, shrine and courtyard views. Use them for variation/aging only after the major silhouette and façade hierarchy below are satisfied. |

**Filename convention:** every six-digit item in the table is the exact timestamp portion of `ref/IMG_20211023_<timestamp>.jpg` (for example, `161311` means `ref/IMG_20211023_161311.jpg`). This abbreviated display avoids repeating a long identical prefix; no filename is inferred.

## Current v003 gap

`art-export/hnp-world-003/HNP_Chedi_v003-preview.png` (46 × 49.95 × 44 m, 27,172 triangles, four materials) has a readable stylized destination but is **not photo-faithful**: it is a single glossy gold bell with a very large simple needle/spire, a plain drum, and an isolated white triangular pavilion over a black opening. It lacks the real layered terracotta base/frieze, repeated gallery openings, white classically articulated base, guardians, broad stair/perimeter language, and the distinct deep primary sanctuary shown in `pra.jpg`.

## Required remodel hierarchy

1. **Macro silhouette first.** Keep the broad round base and visibly curved/near-hemispherical bell; do not make a straight-sided cone. Keep the spire clearly narrower and shorter in visual dominance than v003. A ~30–35% overall-height spire read is a **provisional visual target** from `jd.jpg`, subject to blockout review.
2. **Bell and collar.** Create 4–5 readable lower terracotta ring courses, then a dark/open repeated-bay collar or gallery at the bell-to-spire transition. Include the support/gable rhythm visible in `161311`/`161037`, not a featureless white cylindrical drum.
3. **Lower ring and façade.** Under the bell, add the dark red-brown tiled/frieze band with repeated small pointed/leaf-like finials. Add a white/ivory articulated lower façade: broad cornices, fluted pilasters, recessed dark grille openings, broad stairs, and paired dark guardian figures. These must read from the approach camera as a layered monument rather than a gold object placed on the road.
4. **Primary front sanctuary.** Preserve a tall, front-facing gabled/pointed hierarchy, but make it a deep opening integrated into the façade. Inside, stage the standing gold Buddha against a dark red/brown recess with a gold ornamental pointed surround and white structural frame. The small oval side niches remain secondary repeated cloister detail.
5. **Ground/perimeter.** Use muted cream/aged white, terracotta/red-brown, charcoal grille/guardian, and dark stone paving. Perimeter rail/posts and stair landings may be modular. Keep the central road sightline clear per `docs/design/MAP_LAYOUT.md`; use an exterior collision ring/pedestal perimeter so the solid Chedi remains impassable while the intended worship entry remains a later, explicitly designed G03 interaction.
6. **Night.** Preserve the established night treatment: warm gold delineates ring courses, bell ribs, collar/spire and the primary sanctuary; white façade stays dimmer cream. Avoid a uniform orange shell. `jd-night.jpg` is an appearance reference, not a mandate for a literal lighting installation.

## Integration / budget contract

- Retain current integration envelope unless Unity owner approves a change: ground pivot, root at the existing Chedi placement; currently proposed base radius 23 m / total height 44 m is **provisional but compatible** with v003's 46 m footprint and 44 m height.
- Preserve Blender local front `-Z`, Unity `Y +90°` only if verified by the export manifest; do not infer it from this brief.
- Main landmark budget: **≤30,000 LOD0 triangles**, shared atlas/prebaked texture preferred and no more than necessary material slots. Current 27,172-triangle model leaves little headroom: trade tiny unseen repetition for the silhouette, front sanctuary and approach-facing façade.
- Export must provide source, FBX, preview (front/three-quarter/approach), manifest with dimensions/triangles/materials/texture sizes/pivot/axis/collision intent, and round-trip result. Unity/gameplay/mobile acceptance is **NOT RUN** until separate import and device evidence exists.

## Acceptance for art staging

| Check | Required result |
| --- | --- |
| Front silhouette | At road camera distance, broad circular bell and subordinate ribbed spire match `jd.jpg` hierarchy; no v003 needle-over-bell read. |
| Architectural identity | Preview visibly includes terracotta lower rings/frieze, open/dark collar bays, white articulated lower façade, stairs/guardians, and the deep primary sanctuary. |
| Front vs side distinction | `pra.jpg`-informed tall Buddha sanctuary is at the front; oval/arched side Buddha niches are repeated secondary details only. |
| Palette | Terracotta/aged white/dark grille are present in daylight; gold is a landmark/accent and night-light response, not a blanket substitute for site materials. |
| Gameplay fit | Central road sightline stays clear; perimeter collision intent is documented and does not accidentally make the intended front interaction impossible. |
| Budget/export | Manifest and Blender round-trip PASS within the stated budget. Unity import, collision function, Web/device visual quality: NOT RUN until independently tested. |
