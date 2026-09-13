# HNP-RELEASE-20260913 — final deployed Web QA

**Decision:** **PASS — deployed desktop Web release.**  
**Task / requirements:** HNP-RELEASE-20260913; G02, G03, G04, G06, G07, P01.  
**Scope limitation:** this is a stylised, reference-led playable route, not a survey-accurate or photorealistic reconstruction of the real location. Physical mobile validation is **NOT RUN**.

## Deployed identity and environment

- URL: `https://go2jd.taati.dev/`
- Deployment: `6eccd3b`, successful run `34738416899`
- Live `release.json` build ID: `74e3a5a4f7cd-e38217f5f90c`
- Live asset identity: `web.data` `74e3a5a4f7cd3bfe49655da42594e550314acfc0bc44f71ab7f1f035af3b75b3`; `web.wasm` `e38217f5f90cee070b157e8c0c7189599bd160b26e8087267ffc033c15788a4a`
- Browser: Chrome 152.0.7977.84, Windows desktop; actual renderer ANGLE / NVIDIA GeForce RTX 4070 SUPER / Direct3D11.
- Machine-readable run: `reports/qa/release-20260913-web-20260913-114104/report.json`

## Live acceptance

| Check | Status | Actual evidence |
|---|---|---|
| Build linkage and page errors | **PASS** | URL returned the stated live release record; harness recorded no page/console errors. |
| G02 route and bridge | **PASS** | Real keyboard travel crossed the bridge and reached prayer vicinity without teleport; screenshot `bridge-crossed.png` shows avatar on the bridge surface/rails rather than below the deck. |
| G03 prayer | **PASS** | Shrine image is present in daylight `prayer-approach.png`; E starts prayer, map pause preserves progress, completion count is exactly one and movement is restored. |
| G04 map | **PASS** | Actual minimap opens the bounded map and BACK closes it; paused diagnostic is true while open. |
| G06 return | **PASS** | The visible Settings RETURN control was opened/clicked and reset player X to 0. |
| G07/P01 input/orientation | **PASS (desktop scope)** | W/Shift movement and pointer-emulated pad movement work. Portrait overlay pauses active clock/player for 900ms; landscape resumes. |
| Day/night readability | **PASS** | `night.png` shows lit landmark, road/avatar/HUD; TIME UI restored daylight for clear bridge and shrine composition. |
| Physical Android/iPhone | **NOT RUN** | Desktop viewport/pointer emulation cannot establish real mobile-browser acceptance. |

## Evidence

- `reports/qa/release-20260913-web-20260913-114104/landscape-start.png`
- `reports/qa/release-20260913-web-20260913-114104/night.png`
- `reports/qa/release-20260913-web-20260913-114104/map-open.png`
- `reports/qa/release-20260913-web-20260913-114104/bridge-crossed.png`
- `reports/qa/release-20260913-web-20260913-114104/prayer-approach.png`

No further browser rerun is required for this deployed build. The outstanding physical-mobile check is a separate release evidence gap, not a reason to relabel this desktop live run as mobile PASS.
