# Station prototype validation

Scope: first playable station trial, not the complete game. Unity 6000.6.0f1, Blender 5.2.1 LTS.

| Check | Result | Evidence |
|---|---|---|
| Unity MCP discovery / project inspection | PASS | unity-preflight-resume.json |
| Blender model generation via CLI | PASS | ../art-export/station/bench-manifest.json |
| Saved station scene / bench prefab | PASS | unity-create-station.json |
| Movement, jump and landing | PASS, Play Mode assertions | unity-play-tests.json |
| Pickups, duplicate pickup protection | PASS, Play Mode assertions | unity-play-tests.json |
| Departure gating, ending, restart | PASS, Play Mode assertions | unity-play-tests.json |
| Bench height, URP materials, compound collider | PASS | unity-play-tests.json |
| Sign orientation | Fixed after initial screenshot review | unity-fix-signs.json |
| Initial Web build | Compiled, but visual check FAIL: meshes invisible; corrected in revised build | Explicit Mobile URP default/quality and WebGL2 configuration |
| Revised Web build | PASS: 0 errors, 356 warnings, 50,429,967 bytes | web-build.txt / web-build-hashes.json |
| Browser startup/input/orientation | PASS: Chrome 152.0.7977.76, no page or console errors | web-smoke.json |
| Browser visual inspection | PASS: station, train, character and benches visible; signs readable | web-desktop.png / web-landscape.png |
| Physical Android and iPhone | NOT RUN | No physical device access |
| Blender MCP | NOT CONNECTED | No add-on/endpoint found; CLI used explicitly |

The initial automated browser test only proved startup/input dispatch/orientation behavior. Its visual inspection caught missing scene meshes; automated startup alone is insufficient for a pass. The build configuration now explicitly assigns Mobile URP as default and quality pipeline, and selects OpenGLES3 (WebGL2). Retest screenshots were inspected and show the scene meshes correctly. Runtime log confirms Mobile_RPAsset and OpenGLES3. The two setting changes were validated together; this does not isolate which one alone caused the original rendering failure.

The revised build's synchronous MCP request outlasted the relay connection, so `unity-build-request.json` records a transport failure; Unity continued and wrote a successful BuildReport. Completion is established by `web-build.txt`, the generated file hashes, and the actual browser load, not by the MCP call status.

Build warnings include AI inference shader variants and Unity's Web support library warnings. Browser logs also note unsupported/stripped optional postprocessing and a light-cookie format fallback. The starter scene does not use those postprocessing effects. These warnings are retained as limitations, not reported as a warning-free build.

Browser dimensions checked: 1280×720 and 844×390 landscape; 390×844 portrait overlay; return to landscape. Keyboard start/move/jump were dispatched and the resulting scene was inspected. Mobile touch and native fullscreen acceptance remain NOT RUN on actual hardware.

The prototype uses original Blender bench geometry; character, train and station architecture are Unity primitive blockouts. Collecting three postcards is a temporary trial objective, not a replacement for the source game's complete route and minigames.

No production performance claim: local headless Chrome uses software rendering, not mobile hardware. Current build disables compression for easy local hosting. Fullscreen behavior and mobile multitouch require physical-device verification.
