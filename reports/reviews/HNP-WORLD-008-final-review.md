# HNP-WORLD-008 — final r4 night / Chedi boundary review

**Date:** 2026-09-10  
**Reviewer:** independent design/QA  
**Build evidence:** `builds/world008-r4/web`, hash `fc40e980520263d63bbcf9b01d8963751a0801735e1ab030930d88f75af450ef`; `reports/world/world008-night-20260910-214807/report.json`; collision evidence `reports/world/world008-collision.json` and `reports/world/world008-build6.log`.  
**Visual evidence:** `night-approach.png`, `night-portrait.png`, `night-traffic.png`, and `day.png` in that same report folder; reference `ref/jd-night.jpg`. No Unity, browser, scene, or art mutation was performed by this reviewer.

## Result

| Acceptance area | Status | Evidence / finding |
| --- | --- | --- |
| Chedi night identity | **PASS** | The r4 night approach resolves the stepped base, gold bell/ribs, collar/spire, and cream front portico as distinct layers against the blue-black sky. It is a successful stylized reading of the light hierarchy in `jd-night.jpg`, not a claim of exact architectural or photographic fidelity. |
| Street-route lighting | **PASS** | Downward lighting leaves roof planes dark while curb/near-road and shop-front pools remain readable, leading to the landmark without a broad roof/wall wash. |
| Vehicle night cues and UV repair outcome | **PASS** | `night-approach.png` and `night-traffic.png` visibly distinguish warm-white headlights from red rear lights. Side/rear windows now carry a restrained warm cabin cue, consistent with the corrected UV staging evidence. |
| Day regression | **PASS** | `day.png` retains the warm daylight landmark, route, Thai UI and control readability; night-specific visual emission is absent in the report's restored-day snapshot. |
| Chedi is impassable | **PASS (reported Web + collision test)** | The r4 report records the approach held at `x=26.45` through sprint and Jump, followed by successful retreat to `x=22.13`; collider remains present in all snapshots. `world008-collision.json` records all 16 cardinal CharacterController cases (walk/sprint × jump/no-jump) PASS at a minimum radius of `23.3599854`. |
| Functional night regression | **PASS (reported)** | `report.json` has overall PASS and records 10 street fixtures, 36 headlight fixtures, 18 cabin fixtures, 15 active realtime lights total, and night-to-day restoration. The 15-light count is not a Chedi-outline element count. It explicitly marks physical mobile **NOT RUN**. |
| Real-phone rendering, touch, brightness and performance | **NOT RUN** | Desktop Web screenshots/reported browser checks cannot establish real mobile-device rendering, touch ergonomics, device brightness or performance. |

## Scope boundary / known limitation

Close third-person traffic-camera occlusion is a documented pre-existing world003 behavior. Per task direction it is outside this HNP-WORLD-008 lighting/collider retest and is neither re-gated nor treated as a new regression here.

## Conclusion

**PASS for the scoped r4 desktop/Web evidence.** The Chedi now reads as the requested night landmark, street/vehicle lighting has the needed directional clarity without relighting roofs, the UV repair is visible in runtime cabin cues, and the Chedi boundary has reported walk/sprint/jump coverage. Physical-mobile acceptance remains **NOT RUN**.
