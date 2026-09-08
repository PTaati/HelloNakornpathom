# Environment and connection trial — 2026-09-08

## Verified

- Unity `6000.6.0f1`, project `hnp-game`.
- Unity MCP relay exists at `%USERPROFILE%/.unity/relay/relay_win.exe`.
- Transport discovered from the Unity connection record: named pipe, targeted by project path. This is not an HTTP MCP endpoint.
- MCP initialize and tools/list: **PASS**, see `unity-tools.json`.
- MCP `Unity_RunCommand` read-only preflight: **PASS**, see `unity-preflight.json`. Confirmed correct project, not playing/compiling, SampleScene clean, WebGL build support available.
- Blender executable: `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`; actual reported version **5.2.1 LTS**.
- Blender background Python model generation, FBX export and preview: **PASS**. Source and outputs exist. Blender emitted a thumbnail cache write warning; the requested .blend, FBX and preview were written successfully.

## Unresolved / not executed

Update after user authorized continuation: Unity MCP reconnected, scene/prefab creation and Play Mode tests passed. See the current results below; the earlier blocked attempt is retained here as history.

- Blender MCP: **BLOCKED** — no Blender listening port or installed MCP add-on was found in the inspected Blender user directory. Asked for add-on/connection details. Model generation used Blender CLI, not MCP.
- Later Unity refresh call: **FAIL** — server returned `Unity not detected (no fresh discovery files found)`, see `unity-refresh.json`. The relay connection needs to be checked again before scene creation.
- Scene creation command: **BLOCKED** — execution approval was rejected by the user. Did not retry the action through another mechanism.
- Unity generated script .meta files and Assembly-CSharp binaries after source creation, but Play Mode correctness is **NOT RUN**.
- Saved StationPrototype scene, Unity bench visual/scale/collider validation, Web build and browser/mobile tests: **NOT RUN**.

No native Codex Unity/Blender tools were exposed in this session. Unity was reached with the installed official stdio relay through `tools/unity_mcp.py`.

## Resumed trial results

- User clarified that deny was accidental and authorized the pending work.
- Unity preflight reconnected: **PASS**, `unity-preflight-resume.json`.
- Scene creation and save: **PASS**, `unity-create-station.json`; `Assets/_HNP/Scenes/StationPrototype.unity` exists.
- Play Mode assertions: **PASS**, `unity-play-tests.json`: movement, jump, landing, duplicate pickup protection, departure requirements/radius, ending, restart, bench material/collider/height.
- Screenshot review found mirrored signs; fixed and saved, `unity-fix-signs.json`. `station-play.png` records the earlier view before this correction.
- A connection miss during script reload was recovered on the next attempt.
- Web build requested through the same running Editor; no second Unity process was opened against the project.
- Revised Web build **PASS**: `web-build.txt`, 50,429,967 bytes, 0 errors, 356 warnings. MCP transport timed out while the build continued; the BuildReport and actual browser load confirm completion.
- Chrome **PASS** for startup, input dispatch, orientation overlay and scene visual inspection: `web-smoke.json`, `web-desktop.png`, `web-landscape.png`.
- Assigned Mobile URP as default/quality pipeline and explicitly selected WebGL2 after the first browser visual check found invisible meshes. Retest renders scene objects correctly.
- Physical Android/iPhone testing remains **NOT RUN**. Blender MCP remains unverified; Blender model creation was via CLI.

## Reference update

`ref/style.jpg` appeared during this task and was inspected. It depicts stylized warm sunset lighting, low-poly trees, colorful streets and a prominent chedi. Treat it as an art reference; its driving-game text does not replace the tourism gameplay requirements. Current scene code is an initial blockout, not final visual matching.

## Source control

The existing root `.gitignore` contains `hnp-game/`, so Unity prototype code and Unity scene/assets are currently ignored by Git. This existing rule was left intact; local browser-test dependencies, Python caches and build output were added to ignore rules. Root art/source/tool/report files are visible to Git.
