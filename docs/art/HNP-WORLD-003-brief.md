# HNP-WORLD-003 — art and mobile UI correction brief

**Status:** implementation brief; baseline rejected by user.  
**Trace:** user direction; G01 (train), G02 (road/crossing), G04 (route/map), G07/G09/G10 (controls, run and traveller), P01 (mobile landscape). Station-left → central road/canal → chedi-right remains mandatory.

## Sources and limits

- `ref/style.jpg`: target is a polished warm golden-hour mobile-city composition: orange sun, peach sky, saturated but separated road/foliage/roofs, road traffic with readable vehicle forms, and the chedi as a large destination silhouette. It is style reference only, not a surveyed map.
- `ref/jd.jpg`: geometry reference for the chedi: broad stepped circular base, smooth golden bell, narrow collar/open dark ring, long ribbed tapering spire, and a bright white/cream front portico on the stair axis. Exact ornament is **provisional**.
- TAT article supplied by root, [10 things to do in Nakhon Pathom](https://www.tourismthailand.org/Articles/10-things-to-do-in-nakhon-pathom), supports a standing Buddha at the north-front niche. It does not authorize inferred decorative detail.
- Rejected evidence: `reports/world/web-test-20260910-194920/web-walking.png` and `web-night.png`. These are desktop/browser screenshots, not physical mobile evidence.

## Chedi: mandatory silhouette correction

Replace the narrow/tall current proportion (reported previous art scale: 54.12 m high / 40.48 m base diameter) with **provisional game dimensions**: base diameter about **46 m**, total height about **44 m**. From gameplay camera the vertical read must be:

1. stepped base, y=0–6.3 m (about 14% of total height), broad and visibly layered;
2. one smooth bell, about diameter 17.5 m at y=6.3, continuously narrowing to about 7 m at y=22 (about 36% of total height), not a balloon/stack of cones;
3. short narrow collar with an unmistakable dark/open ring, y=22–26;
4. ribbed conical spire, y=26–44 (about 41% of total height), finishing in a fine point.

Put the white/cream, vertically proportioned front portico at the main stair axis as the contrast cue. Do not substitute repeated small red triangular facades. The north-front Buddha niche is allowed only as a simple standing figure/void until detailed reference is approved. Preserve cleared stairs, terrace route, collider clearance and direct avenue sightline.

## Golden-hour town treatment

Use sunlight from a low side angle: bright warm cream/gold lit planes; cool blue-grey shadow planes; peach-gold sky toward the sun and pale blue opposite. Keep road charcoal rather than orange-brown, water turquoise-blue, foliage at least three readable greens, roofs terracotta/deep red, and white/cream building walls. Avoid one orange wash, flat grey sky, black night silhouettes, or a uniformly emissive chedi. At night, route edges, portico/stairs, crossing, station exit and landmark silhouette stay readable through restrained warm lamps/windows.

## Road life and birds

Every visible vehicle must move on an authored closed road loop; do not leave parked/static traffic in the gameplay corridor. Use 6–8 active instances maximum near the player (profile before raising), with at least four recognisable body families: compact hatchback, sedan/taxi, pickup, and local bus/van. Give each a cabin/window band, wheel/axle read, lights/bumper or grille indication, and 3–5 palette variants (for example teal/blue, red/coral, green/yellow taxi, cream/white). Maintain lane direction, spacing, spawn/despawn outside the camera, and a clearly visible pedestrian-safe crossing gap. Ambience remains non-blocking until the G02 collision/retry system is explicitly delivered.

Birds must read as birds at gameplay distance: V/wing silhouette, 2–3 wing poses or procedural flap, individual phase/height/turn variation and small loose flocks around chedi/trees. They must not read as black pixels, intersect the chedi, cover UI, or use colliders. Limit to a visible flock of 5–8; cull/fade at distance/night.

## UI correction (Thai, mobile landscape)

- Remove fullscreen and `HOME` entirely. Remove the standalone `MAP` button.
- The minimap itself is the map button: tap opens/closes the full map; it has a clear location marker and 44 px minimum hit region without an added text bar.
- Top-left has one 44 px hamburger/menu icon. Its hidden panel contains only Thai time-of-day and sound controls: `เวลา` and `เสียง`, with icon + current state. It is closed by default and must not cover the chedi/crossing while closed.
- Use Thai UI strings: `สถานีนครปฐม`, `ค้นพบ 1/5`, `แผนที่`, `เวลา`, `เสียง`, `พระปฐมเจดีย์`, and `หมุนหน้าจอเป็นแนวนอน`. Replace English route/help/HUD text. Keep brand wordmark only if it does not displace Thai game information.
- Bottom-right is icon-first: jump icon and running-person icon, both ≥44 px with a short Thai accessible label/tooltip (`กระโดด`, `วิ่ง`). No persistent English `JUMP`/`RUN` button text. Bottom-left movement pad remains; right-side drag remains camera control.
- Run must select an actual Run animation state/clip at running speed, not merely accelerate the controller while using Walk. Idle, Walk, Run and Jump/Air must transition without root drift, foot slide or limb snap.

## Evidence gates

| ID | Acceptance | Required evidence |
|---|---|---|
| W3-A | Chedi matches the four-part camera silhouette and front portico hierarchy. | Blender preview plus Unity gameplay-camera day/night comparison beside `ref/jd.jpg`; dimensions/triangle/material report. |
| W3-B | Town reads as golden hour, with separated palette and readable night navigation. | Station/road/chedi screenshots at both times; no orange wash/black route. |
| W3-C | All visible vehicles visibly drive loops; each type is recognisable and no ambience blocks the player. | 30–60 s gameplay video or sequential captures, actor count/route report, traversal result. |
| W3-D | Birds read as flapping birds rather than dots. | 3-phase/capture evidence from gameplay camera. |
| W3-E | Thai minimal UI: hamburger panel, clickable minimap, no fullscreen/Home/MAP text button, icon controls and no overlap at 667×375, 844×390, 932×430. | Browser captures and interaction log; real-device safe-area check remains separate. |
| W3-F | Actual Run clip/state is used at run speed and transitions cleanly. | Blender/FBX clip manifest, Unity Animator evidence, 30 s idle/walk/run/jump video. |

All Unity import, Play Mode, WebGL and physical-device checks are `NOT RUN` until evidence is captured. Do not claim mobile validation from desktop screenshots.
