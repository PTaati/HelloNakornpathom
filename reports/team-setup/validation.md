# HNP-TEAM-002 validation — 2026-09-09

Setup validation only. Repository model/config settings do not represent a completed game or a new asset release.

## Configuration and discovery

- Codex CLI: 0.153.2.
- `.codex/config.toml`: child default Terra/medium; max 3 child threads; no root model or permission override.
- Blender profile: Sol/high. Unity and Designer/QA profiles: Terra/medium.
- All three repository skills passed the bundled skill-creator quick_validate.py.
- Native discovery: invoked installed `node .../@openai/codex/bin/codex.js debug prompt-input` locally. Exit 0; generated prompt contained all three skill names. Only presence was inspected; full prompt was not saved.
- TOML parsing, reference existence and official skill validation results are in `validation.json`.

## Independent skill exercises

All agents were newly spawned with explicit model/reasoning and `fork_turns=none`, read their config/skill and project baseline, and returned results. Existing inherited-model agents were not reused for these checks.

| Role / runtime task | Exercise | Observed outcome |
|---|---|---|
| Blender / blender_artist_sol | Inspect Traveller manifest, source/export existence, preview/ref; explain unsaved GUI handling; run --version only | PASS behavior: distinguished rigid-limb prototype from skinned rig, old measurements from fresh audit, flagged missing deformation/gameplay-camera evidence; protected GUI source. CLI 5.2.1 LTS, hash 9e2066aef7ef |
| Unity / unity_engineer_terra | Discover relay tools; reason about importing FBX while QA owns Editor | PASS behavior: saved actual tools/list result, did not mutate Editor, used staging and required ownership handoff. Relay transport PASS; Editor capabilities BLOCKED because tools=[] |
| Designer/QA / designer_tester_terra | Review old world validation and actual previews/reference, decide current release readiness | PASS behavior: independently identified missing physical-device/performance evidence and technical model checks; did not treat historical desktop smoke as current mobile PASS |

Designer/QA used the phrase PARTIAL PASS for mixed visual/technical results. Updated the skill to require one allowed status per individual check, distinguish BLOCKED from NOT RUN, and separate a failed release gate from unexecuted constituent tests. This is a focused reporting correction, not a new game test result.

The visual exercise raised candidate issues (Traveller cowboy-hat readability, stylized chedi details, dark gaps in a world preview). These are setup-review observations for a future scoped asset review, not verified runtime bugs or authorization to change art.

## Actual limitations

- Unity relay capability evidence: `unity-tools.json`; initialize/tools/list worked but returned an empty list. No RunCommand or other Editor action was called.
- Blender source-scene inspection, new geometry measurement, FBX round-trip, Unity import/prefab/Play Mode, Web build, physical Android/iPhone, and performance checks: NOT RUN in setup scope.
- IDE UI visibility: NOT RUN; CLI skill discovery and explicit skill reads passed. Reload Codex if its UI has not refreshed.
- No model-cost benchmark was performed. The configuration implements the approved tier choices; retries and token usage still affect actual task cost.

Revalidate skills from the project root with PYTHONPATH pointing to tools/.python, PYTHONUTF8=1, and the bundled quick_validate.py for each `.agents/skills/hnp-*` folder. Parse TOML with Python tomllib or the installed pip vendored tomli on Python 3.10. Do not upgrade Unity or global packages to validate these instruction files.
