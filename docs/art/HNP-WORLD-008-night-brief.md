# HNP-WORLD-008 — Chedi night-lighting and boundary brief

**Task / scope:** HNP-WORLD-008, implementation brief only; Unity ownership remains with Root.  
**Requirements:** G02 route/crossing and G07 movement; P01 mobile Web landscape visual legibility.  
**Sources inspected:** `ref/jd-night.jpg`; baseline captures `reports/world/world006-camera-20260910-210914/cycle-0.png` and `cycle-12.png`. The reference is a visual guide, not evidence for an exact architectural reconstruction.

## Intent

Make the Chedi a warm, recognisable night landmark against a deep blue-black sky, while keeping the road, traveller, traffic and controls readable. The current `cycle-12.png` is too uniformly dark: vehicles lack head/tail/cabin cues, street lamps do not create a readable route, and the Chedi’s lit silhouette does not yet carry the reference’s distinctive gold outline.

## Required visual cues

- **Chedi:** warm gold/amber tracing on the stacked base rings, long bell ribs, collar, and tiered spire. Keep a darker gold bell interior between lit ribs so it reads as form, not a flat orange glow. Illuminate the white front portico/niche separately with a warmer-white focal light; it must remain visible from the approach.
- **Street route:** evenly spaced warm street-lamp pools on both road edges, enough to read the curb, lane and player route without bleaching the night sky. Lamps should lead toward, not compete with, the Chedi.
- **Traffic:** front-facing vehicles show a paired warm-white headlight cue; rear-facing vehicles show restrained red tail lights; visible cabin/window areas carry a faint warm interior cue. Lights must move with vehicle heading and must not form a full-screen flare.
- **Boundary:** Chedi exterior is impassable. Place the collision boundary at/just outside the outer stepped base or enclosure so the player cannot enter, walk through, jump over, or clip into the monument. Preserve a visually obvious perimeter and leave the road/approach unobstructed. Exact clearance is **provisional** pending the final collider dimensions.

## Acceptance checks

| Check | Status target | Observable acceptance |
| --- | --- | --- |
| Chedi night identity | PASS | In a night approach capture, broad base, bell, collar/spire and front portico resolve as separate gold/cream layers, recognisably following the hierarchy of `jd-night.jpg`. |
| Route lighting | PASS | Road edges, lane immediately ahead, traveller silhouette and lamps remain legible at night; UI is not obscured or visually overpowered. |
| Vehicle lighting | PASS | At least one approaching and one receding road vehicle visibly show the correct white-vs-red directional cue; cabin cue is subtle and does not erase vehicle colour/form. |
| Chedi collision | PASS | From four cardinal approach directions, hold walk and Run into the boundary and attempt Jump: player is stopped outside it with no penetration, climbing, camera-through, or loss of control. |
| Traffic compatibility | PASS | Vehicle traffic keeps using its loops and neither jams permanently against nor enters the Chedi boundary during a sustained night observation. |
| Regression | PASS | Day lighting, Thai menu/time control, minimap and existing movement remain readable/functional after the night change. |
| Mobile device / performance | NOT RUN | Desktop screenshots or emulation cannot validate real-phone brightness, thermal/performance impact, touch safe areas, or browser rendering. |

## Evidence required for retest

Provide current-build day and night approach captures, one capture each for approaching/receding vehicle lights, and a short reproducible collision test record (build path/hash, input steps, expected/actual). A night screenshot alone cannot prove directionality, collision, or traffic continuity.
