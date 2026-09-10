# HNP-WORLD-002 — Living warm-stylized world: design and acceptance brief

**Status:** READY FOR IMPLEMENTATION. This brief is scoped to `NakornpathomWorld`; it does not declare the wider game complete.

**Task / requirement trace:** user request; G01 (train arrival), G02 (safe vehicle crossing), G04 (explorable upper/lower areas and map), G07 (mobile movement/camera), G09 (animation), G10 (default outfit), P01 (mobile-landscape Web). Atmosphere/NPC detail is P2 in the production plan. G03/G05/G06/G08/G11/G12/G13 remain out of scope.

## Evidence and starting point

- Layout: `ref/game-document/image2.png` and `docs/design/MAP_LAYOUT.md`: station-left → canal/central road → chedi-right is mandatory. Distances remain compressed, provisional game metres.
- Art: `ref/style.jpg` supports the warm stylized direction; `ref/jd.jpg` and `ref/jd-night.jpg` support the chedi silhouette/lighting only. Architectural detail not visible in those sources is **provisional**, not a claim of real-world accuracy.
- Current art previews inspected: `art-export/world/world-preview.png`, `art-export/world/traveller-preview.png`. The golden chedi reads well as the landmark and the traveller reads as cute and clothed; the preview also shows simple boxy vehicles and sparse road life.
- Current code reviewed read-only: `HnpWorldGame` provides free exploration, orientation overlay, touch pads, map, 60 fps request and procedural limb posing; `HnpTravellerPose` has only movement-driven walk/head motion. No world traffic/birds/train cycle, runtime day/night, audio source, music control, idle clip/state, or view-mode switch is present. Existing train geometry is in `StationPrototype`, not the world scene.

## Design contract

### Player and camera (G07/G09/G10)

Keep the existing cute 2.25 m traveller and cream button shirt, dark shorts, sandals and cowboy hat. Preserve the readable head/hat silhouette at the default third-person camera distance. Replace the movement-only pose with a stable state contract: **Idle**, **Walk**, **Run**, **Jump/Air**. Idle may use a very small breathing/weight-shift and occasional head glance; it must not translate feet or drift the root. Walk/run must plant feet without visible sliding at the actual controller speeds. Jump must return cleanly to idle/walk on landing. A first-person/alternate camera mode is required by G07 but its intended meaning is unresolved; expose it only after producer confirmation rather than silently defining it here.

### UI and visual language (P01)

Landscape is the primary 1280×720 composition. Retain a dark-teal, warm-gold UI frame, but reduce permanent visual competition: brand/place card top-left, minimap top-right, movement bottom-left, look/right-side gesture area, jump/run bottom-right. Add a compact **sound** toggle beside the map and an unobtrusive day/night label only while changing. All tappable controls need a 44 CSS-px minimum physical target equivalent, safe-area anchoring, clear pressed state, and must not obscure the traveller, road gap, or chedi approach. Portrait remains a blocking rotate overlay; it pauses world simulation and audio fades/pauses rather than continuing unseen.

### Landmark, town, and lighting

The chedi remains the focal point from the central approach: stepped circular base, bell body, collar, ringed taper and gabled entrances. Do not make its gold a uniformly emissive orange; preserve readable lit/shadow planes. Houses and stalls should use a small repeated kit: cream/plaster walls, teak/brown structure, red/copper pitched roof, teal accents, and a 2–3 tone faceted tree family. Add architectural ornaments, signs, exact roof construction or station details only after new reference approval (**provisional**).

Runtime time of day is a short, non-real-time loop: day → warm late afternoon → blue night → day, approximately 3–5 real minutes per complete loop (**provisional tuning**). It changes directional/ambient light, sky/fog, emissive lantern/window accents and bird activity; it must not change walkable geometry, collision, route readability or gameplay timing. Night needs minimum route readability at the station exit, bridge, road crossing, stairs and temple entry.

### Lively but safe movement (G01/G02/G04)

Use deterministic, authored loop/spline paths, never free physics traffic:

| System | Design | Safety/visibility contract | Initial active budget |
|---|---|---|---:|
| Road vehicles | Cute stylized cars/small local vehicles on road loops; varied color/speed/spacing. | Vehicle is visually distinct from crossing gap. Crossing route retains a persistent safe gap; collision/retry is only enabled with G02 rules/checkpoint and owner approval. Otherwise vehicles are non-blocking ambience. | 4 near player; 8 total |
| Birds | Small distant flocks circling chedi/trees, with infrequent perch-to-flight transition. | No collider, no screen-covering flock, cull by distance/night. | 1 flock, 6–10 sprites/meshes |
| Train | Visible arrival/departure cycle at the station, once on initial arrival and then a clearly signposted non-blocking ambient loop. | Player never starts inside moving train, is not pushed, and train cannot block the station exit. Train stop/open-door state hands control to player for G01. | 1 train |

Traffic visual variety is not permission to invent a punishment economy. G02's collision/checkpoint/penalty specification remains the source of truth; if this task implements only ambience, label collision **not enabled**.

### Music and sound (P01)

First user gesture on **Start Exploring** is the only automatic-audio permission point: request fullscreen if supported and call audio start there. If blocked, show `Tap for sound` without blocking play. Provide a persistent mute/unmute control; obey it across pause, focus loss, portrait overlay and reload if save support exists. Music is one seamless low-volume warm local loop, crossfading to a quieter night variation; use licensed/original audio only and record source/license in the asset manifest. Ambient train, birds, road and UI sounds are optional layers with capped concurrency; no autoplay before gesture and no stacked duplicate loops after Start/retry/resume.

## Production budgets and handoff

- Existing traveller: 7,384 triangles, nine palette materials, procedural rigid limbs (manifest). It meets the 12k triangle target but exceeds the plan's preferred ≤3 materials; consolidate/atlas only if profiling or batching evidence warrants it, without degrading costume readability.
- Existing town/chedi: 25,418 / 19,064 triangles including collision. Chedi is within the 30k landmark target; preserve its silhouette. New vehicle prefab ≤6k triangles and ≤2 shared materials; bird instance ≤300 triangles or billboard; train visible set ≤20k triangles/atlas. Use pooled instances and primitive/compound colliders.
- Mobile gate remains P95 frame time ≤33.3 ms for 5 minutes, tracked memory ≤256 MB, cold compressed initial download ≤30 MB and control available ≤20 s at 20 Mbps/100 ms. Current 52 MB uncompressed build is not evidence against the compressed gate; it must be measured after implementation.
- Blender owner delivers source/export/preview/manifest and animation/budget evidence. Unity owner alone owns scene/prefab/import/runtime implementation. QA does not alter either.

## Observable acceptance and QA

| ID | Requirement | Start/action | Expected result and evidence |
|---|---|---|---|
| W2-01 | G10, G09 | Spawn; remain still 60 s, walk/run/stop/jump repeatedly on flat ground and stairs. | Outfit matches; no root drift, limb pop, foot slide, clipping or stuck state. Gameplay video plus clip/state and prefab evidence. |
| W2-02 | G01 | Fresh save; tap Start; observe train arrival/stop/disembark. Repeat after reload and after focus loss. | Audio begins only after gesture; train never overlaps/pushes player; control transfers once; station exit remains clear. Video/log/state evidence. |
| W2-03 | G02 | Approach crossing at least ten cycles; attempt safe gaps and, if enabled, deliberate hit/retry. | Gap is readable and reachable; no vehicle enters pedestrian-safe geometry. If collision enabled, one deterministic retry/checkpoint and no duplicate penalty. If disabled, label ambience-only. |
| W2-04 | G04 | Walk station → bridge/road → chedi → upper/lower/fair areas at day and night, map open/closed. | Mandatory route and chedi sightline remain readable; all existing collider/traversal checks still pass; map marker agrees with position. |
| W2-05 | user request, P2 | Observe 2 full time cycles at station, road and temple. | Continuous bounded lighting/sky/lantern change, no lighting pop, black geometry or loss of route readability; birds obey day/night rule. Capture day/night pairs plus frame-time trace. |
| W2-06 | P01 | On real Android Chrome and iPhone Safari: fresh load, tap Start, mute/unmute, rotate, background/resume, fullscreen accepted/rejected. | Gesture-safe audio, usable fallback, safe-area UI, no stuck input/audio duplication. Record model/RAM/OS/browser/build/hash. Desktop viewport checks are supplementary only. |
| W2-07 | P01 | Five-minute heavy view (traffic + train + birds + night) and 15-minute zone loop on each physical baseline device. | Meets performance/memory/stability gates, or report measured fail and profile. |

Current evidence status (2026-09-10): W2-01–W2-07 **NOT RUN** for the new feature because no implementation/build exists. Prior HNP-WORLD-001 desktop Chrome traversal and browser smoke are historical evidence only, not acceptance for HNP-WORLD-002 or real mobile validation.

## Decisions requiring producer confirmation

1. Is G02 vehicle collision/retry to be delivered in this increment, or should road vehicles remain non-blocking ambience until the crossing minigame task?
2. Confirm G07's requested second view: first-person toggle, fixed follow camera, or another interpretation.
3. Approve the proposed 3–5 minute visual day/night loop and an original/licensed music direction before audio production.
