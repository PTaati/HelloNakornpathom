# HNP-DEPLOY-001 — restore canonical build/deploy path

status: COMPLETE
editor_owner: root

Goal: rebuild current saved game into the existing `builds/web` directory and keep the existing GitHub Pages pipeline working after commit/push. No new output folders or public deployment from this session.

Diagnosis: prior build helper wrote revision folders while both Pages workflows uploaded `builds/web`. Those five canonical files are tracked by Git, but had not been refreshed. Two workflows also shared the `pages` concurrency group with cancellation enabled.

Changes: latest build entrypoints/local server target `builds/web`; retain `deploy-pages.yml` and remove redundant `pages.yml`; add explicit required-output validation. Deleted workflow remains recoverable from Git history. Existing art/gameplay unchanged.

Acceptance: canonical build success, browser test on canonical files, one deploy workflow, tracked changed outputs ready to commit/push. Actual remote Actions/Pages run NOT RUN until these changes are pushed.

## Verification / handoff

- PASS Unity build directly into `builds/web`: `reports/world/canonical-web-build.log`.
- PASS Chrome desktop gameplay regression on that exact folder: `reports/world/world009-reference-20260911-085404/report.json` (movement, clock, map, idle, overhead camera, night and portrait).
- PASS `git status` shows new canonical data/wasm/loader/index as tracked modifications. Framework JS content remains unchanged.
- PASS PowerShell parser for reusable `tools/build-web.ps1`; it invokes the existing `HnpWorldBuilder.Build` canonical method. This wrapper was syntax-checked, not separately rerun after the successful equivalent Unity build.
- One remaining workflow in working tree: `.github/workflows/deploy-pages.yml`, push main + manual dispatch, uploads existing `builds/web`.
- Local server now uses `builds/web`; prior output folders retained but unused by this pipeline.
- Commit/push and actual GitHub Actions/Pages run: NOT RUN in this session. No claim that a remote deployment already succeeded. Physical mobile NOT RUN.

Future use: close Unity, run `powershell -File tools/build-web.ps1`, review and commit `builds/web` together with the workflow/launcher changes, then push main. No Unity build happens on GitHub; this preserved pipeline publishes the committed local build.
