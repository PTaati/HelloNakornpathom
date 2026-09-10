# HNP-WORLD-010 — primary front sanctuary photo chamber

**Task / scope:** HNP-WORLD-010; replace only the crude front Buddha treatment of the v009 Chedi. Blender Artist owns source/export; Root owns Unity.  
**Requirements:** G02 route/temple approach, G03 prayer destination, G07 movement/camera, P01 mobile Web landscape.  
**Primary reference:** user-provided `ref/pra.jpg` (387 × 792 px, portrait ratio 0.4886). It depicts a front-facing standing gold Buddha in a tall, red/gold ceremonial interior.

## Required outcome

- Remove the primitive front standing-Buddha mesh from the visible sanctuary. Use `pra.jpg` itself as the visible, upright portrait image—no crop that loses the head, feet, gold surround, or front-facing orientation; do not mirror/rotate it.
- Put that image on the back wall of a real **rectangular projecting front chamber** attached to the Chedi, not on an unbacked billboard or inside the former open A-frame. The chamber needs visible side walls, a roof/ceiling, floor/threshold, and a clear rectangular inner recess framing the full portrait.
- Keep a Chedi-compatible exterior transition: existing terracotta/ivory/red-gold language may frame the chamber, but the new rectangular interior must read as an intentional prayer destination and not a generic pavilion.
- Preserve the central approach, existing stair openings and upper-court circulation. The opaque Chedi body remains impassable; the chamber must not introduce a new gate/jamb/collider into the four cardinal stair centerlines.

## Staging contract

- Image plane/recess must face the approach camera under the existing local-front convention; verify in a front preview and export manifest. The supplied photo’s aspect ratio is authoritative; chamber width/height is **provisional** but must letterbox/pillarbox rather than distort the photo.
- Front projection depth, chamber outer roof and sidewalls must remain within the established Chedi integration envelope unless Root explicitly approves a bounds change.
- Document image filename/hash, colour-space/UV set, mesh material count, visible and collider triangle counts, bounds/pivot/axis, collision intent, and FBX round-trip result.
- Do not claim an external exact reconstruction of the real interior: the projection, chamber dimensions, unseen sides and interaction logic are **provisional** gameplay adaptations.

## Acceptance

| Check | Pass condition |
| --- | --- |
| Photo correctness | `pra.jpg` is complete, upright, front-facing and undistorted; no primitive Buddha remains visible in front of it. |
| Chamber form | Front/three-quarter/inside previews show a projecting rectangular chamber with connected roof, side walls, rectangular recess/back wall and floor—not a freestanding image plane. |
| Readability | At normal mobile landscape approach distance, the gold Buddha and red/gold interior are immediately recognisable; the surrounding Chedi silhouette stays readable. |
| Route/collision regression | Four cardinal stair centerlines retain clear approach/retreat; chamber does not create new wall/jamb occlusion. Re-run the v009 `gateDeviation: 0` route check after Unity integration. |
| Export | Source/FBX/manifest/round-trip all PASS within the existing Chedi budget or a documented exception. |
| Runtime/device | Unity import, gameplay camera, Web and physical-device validation are NOT RUN until separately evidenced. |
