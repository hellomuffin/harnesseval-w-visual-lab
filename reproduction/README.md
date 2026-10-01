# HarnessEval-W — an explorable reproduction lab

Open **https://hellomuffin.github.io/harnesseval-w-visual-lab/**. The hosted edition includes the videos and recorded evaluation evidence, plus independently checked browser grading. Source and evidence: https://github.com/hellomuffin/harnesseval-w-visual-lab. It needs no local server. GPU validation is presented as recorded executions on the hosted page.

The page includes six playable case studies, selected/skipped skill routing, Analyze and Verify traces, all 11 skills, an interactive Python-backed score calculator, a 100-case gallery, a reconstructed case-authoring experiment, frozen/reversed video controls, physical-law controls, and a claim-by-claim audit. You can edit the new book case's action and ask the local vision judge to validate it.

## What is actually reproduced

- Six **author-supplied** Seedance 2.0 Standard rollouts are evaluated afresh. These videos are not presented as our generated model outputs.
- Pretrained local backends: CLIP, aesthetic head, MUSIQ, HPSv3, RAFT, AMT-S, PAVRM, MegaSAM/Depth Anything/UniDepth, and optical-flow physics checks.
- New skill plans and semantic Analyze/Verify evaluations use **Qwen3-VL-8B-Instruct on a local GPU**, replacing the authors' GPT-5.5. This is a judge substitution, not an exact model replication.
- Fresh completion audit: **6/6 case scores, zero missing**, with 34 numerical benchmark task results. All 11 skills have numerical outputs when the three physical-law control fixtures are included. Fresh overall **0.754987**; author-cache replay **0.787629**. The substituted judge and adapted runtime mean this is not an exact model/environment replication.
- 3,000 independent Appendix C score vectors match the three released semantic aggregation formulas.
- A new initial image, real local planner, validator and skill routing demonstrate case construction. The full original case-construction program is absent; this experiment is a reconstruction. Its initial image was created with the built-in imagegen tool, not a local image model.
- Every partial, failed or not-applicable result remains distinguishable from a numeric success. See `artifacts/report.json` and each run audit.

The **330-case × 18-model leaderboard, 5,000 human choices, population correlations, human-alignment WBench comparison and fine-tuning analyses are not reproduced**. The public set provides 100 case definitions/images/plans; it does not provide every required generated rollout and human annotation. Recursive skill acquisition is the paper's future work.

## Start the demo

```bash
.venv/bin/python scripts/build_data.py
.venv/bin/python server.py
```

For live action validation, start the local judge in another terminal (about 38 GB on GPU 1):

```bash
scripts/start_judge.sh
```

Do not run that judge while PAVRM is using both GPUs. The site still displays all saved evidence when the judge is offline and reports an explicit offline error if live validation is requested.

## Re-run the experiments

The current workspace includes the code, weights, environments and compiled CUDA extensions. The scripts resolve workspace paths dynamically.

```bash
# Fetch original code dependencies and model files; downloads resume.
python scripts/download_models.py
python scripts/fetch_dependencies.py

# Rebuild inventory and machine-specific backend paths.
.venv/bin/python scripts/prepare_run.py

# Start scripts/start_judge.sh first for these semantic skills.
.venv/bin/python scripts/run_skill.py intentional_change_verifier_vlm
.venv/bin/python scripts/run_skill.py physical_response_verifier_vlm
.venv/bin/python scripts/run_skill.py offscreen_evolution_verifier
.venv/bin/python scripts/stress_tests.py --fresh
.venv/bin/python scripts/construct_case.py

# Released planner, fresh output directory (does not overwrite shipped plans).
.venv/bin/harnesseval plan \
  --manifest upstream/runs/example/results_example/manifest.json \
  --output-root artifacts/fresh/plans --assets-root upstream \
  --model local-judge --base-url http://127.0.0.1:8000/v1 \
  --wire-api chat_completions --workers 1 --timeout 600 --refresh

# Stop the local judge before the large two-GPU metric.
CUDA_VISIBLE_DEVICES=0,1 OMP_NUM_THREADS=4 \
  .venv/bin/python scripts/run_skill.py physical_plausibility_inspector
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=4 \
  .hpsenv/bin/python scripts/run_skill.py render_quality_inspector
CUDA_VISIBLE_DEVICES=0 .venv/bin/python scripts/run_skill.py motion_quality_inspector
CUDA_VISIBLE_DEVICES=0 .venv/bin/python scripts/run_skill.py appearance_consistency_inspector
CUDA_VISIBLE_DEVICES=0 .venv/bin/python scripts/run_skill.py return_consistency_verifier
CUDA_VISIBLE_DEVICES=0 .venv/bin/python scripts/run_skill.py viewpoint_trajectory_verifier
.venv/bin/python scripts/run_skill.py physical_law_validator

# Chunk-level drift stages + final merge, sequenced to avoid GPU contention.
.venv/bin/python scripts/complete_metrics.py

.venv/bin/python scripts/replay_scores.py
.venv/bin/python scripts/score_fresh.py
.venv/bin/python scripts/formula_checks.py
.venv/bin/python scripts/write_report.py
.venv/bin/python scripts/build_data.py
.venv/bin/python scripts/check_ui.py
```

`run_skill.py` uses the official skill runner, shipped plans, and a separate `artifacts/fresh/cache`. Subsequent executions may hit this **newly produced local cache**. For an independent repeat, use a new cache root with the upstream CLI. `stress_tests.py --fresh` assigns timestamped new cache directories to every control and repeat, preserving previous experiments.

## Environment and adaptations

Original checkout: `upstream/`; commit recorded in `artifacts/report.json`. Dependency commits are pinned in `scripts/fetch_dependencies.py`; download revisions and checkpoint SHA-256 receipts are under `artifacts/`. The new source checkout is locally patched, with reviewable diffs in `artifacts/*.patch`.

- Hardware: two NVIDIA L40S GPUs, about 45 GB usable each.
- `.venv`: Python 3.12, host Torch 2.9.1/CUDA 12.8, Transformers 4.57.6, metric dependencies. This differs from the authors' environment; exact package lists are saved in `artifacts/venv-freeze.txt`.
- `.hpsenv`: Transformers 4.51.3 / tokenizers 0.21.4, required by the released HPSv3 checkpoint namespace. It reuses `.venv`'s other packages. See `artifacts/hpsenv-freeze.txt`.
- `.cuda`: CUDA 12.8 compiler. `scripts/build_megasam.py` builds the two MegaSAM extensions, updates obsolete tensor dtype dispatch, and targets L40S compute capability 8.9. Those changes affect build compatibility, not evaluation formulas.
- AMT's released checkpoint needs the older `torch.load(weights_only=False)` behavior. This is applied specifically to that downloaded checkpoint.
- HPSv3's pinned dependency lacks the `move_to_device` / `reward_prepared` API expected by HarnessEval. The compatibility patch adds that interface without changing model weights or reward computation.
- PAVRM's single-patch Conv3d was prohibitively slow on this runtime. An opt-in equivalent linear projection is used. Large visual batches are optionally split along independent temporal patch groups to fit memory; language attention still sees all frames. FP32/BF16 projection checks and temporal-chunk equivalence checks are saved in `artifacts/patch-equivalence.json` and `artifacts/vision-equivalence.json`. The Qwen3 MoE expert container also uses its existing sparse branch under no-grad, avoiding expansion of all tokens across all 128 experts. Only that parameter-only module switches branches, not the rest of the model. `artifacts/experts-equivalence.json` tests the dense/sparse outputs. These runtime adaptations are disclosed, not claimed to be bitwise identical to the authors' environment.

## Known scientific discrepancies

1. The semantic code executes **two calls**, with eight questions answered together by Verify; it does not launch eight independent question agents.
2. Appendix C describes visual + causal physical observation; this backend returns **PAVRM raw / 5 only**.
3. Appendix C uses equal mean/worst revisit-pair weights; the code uses **0.7 / 0.3**, with an additional non-static gate.
4. The wind/flag case selects a physical-law diagnostic but has no matching engine. It is **not applicable**, not a passed physics test.
5. Our local mug controls score **1.0 original, 0.45 frozen, 0.875 reversed (an earlier independent run gave 0.75)**. This exposes partial credit for preserved scene/target properties even when the action is wrong. Three local original-mug evaluations each scored 1.0; this is not a replication of the paper's human-fit robustness statistic.

## Files

- `site/`: responsive page, vanilla HTML/CSS/JavaScript; no Node build required.
- `server.py`: static/media serving plus actual upstream formula execution and local VLM validation.
- `scripts/`: downloads, setup, real evaluations, report generation and browser verification.
- `artifacts/`: logs, fresh caches, control videos, construction receipts, numerical checks, screenshots and source patches.
- `public-set/`: downloaded public benchmark cases and initial observations.
- `weights/`, `dependencies/`, `upstream/`: original research models and code, with their own licenses.

The generated initial observation is `artifacts/construction/initial.png`. Its prompt: an indoor photorealistic kitchen with a closed red hardcover book fully visible on a pale wood counter, blue mug and potted herb as anchors, white tiled backsplash, fixed slightly elevated three-quarter camera, no people, writing, logos or motion. The detailed generation and local authoring provenance is in `artifacts/construction/result.json`.

## Matched protocol experiment

`scripts/compare_wbench.py` imports the official WBench question generator and score aggregation from `baselines/WBench`. It substitutes the local Qwen judge and HarnessEval's 12-frame sampler to compare the same three clips. WBench scores original/frozen/reversed **1.0 / 0.2 / 1.0**; the latest independent HarnessEval control execution gives **1.0 / 0.45 / 0.875**. These scores use different rubrics and are not calibrated probabilities. Harness also uses an initial-image Analyze specification. This is not an architecture-only ablation or a human alignment experiment. Full raw answers and pinned source commit: `artifacts/baseline/results.json`.

MegaSAM's embedded UniDepth expects the retired pure-Python xFormers Nystrom attention component. We restored the BSD-licensed implementation from xFormers v0.0.27.post2 as `legacy_nystrom.py`, using the current compatible xFormers kernels. Its exact source is preserved in `research/xformers_nystrom.py` and `artifacts/legacy_nystrom.py`.

Re-run the small numerical checks with `.venv/bin/python scripts/check_runtime_adaptations.py`. These test disclosed runtime adaptations on small random configurations, not full-model scientific equivalence.

## Generate and grade a new local rollout

The constructed red-book case also has a real [Wan 2.2 TI2V 5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers) image-to-video job. Its weights are revision-pinned in `artifacts/download-generator.json`. Generation uses an isolated Diffusers 0.37.1 install under `.genlibs` because 0.35.1 has a Wan 2.2 tiled-VAE channel mismatch. Torch SDPA avoids conflicting host FlashAttention-3 extensions. The evaluation environments stay unchanged.

```bash
.venv/bin/python scripts/download_generator.py
.venv/bin/pip install --no-deps --target .genlibs diffusers==0.37.1
# Run on a free GPU; temporarily stop the judge if using its GPU 1.
CUDA_VISIBLE_DEVICES=1 .venv/bin/python scripts/generate_case_video.py --generate-only
# Restart scripts/start_judge.sh, then grade the saved video (no regeneration).
.venv/bin/python scripts/generate_case_video.py
.venv/bin/python scripts/build_data.py
```

Settings: seed 42, 97 frames at 24 fps, 1152 × 768, 50 denoising steps, guidance 5.0. The prompt contains the case action plus a fixed-camera instruction. The video and semantic grade supplement the authors' six videos; they do not reproduce the full 18-model leaderboard. See `artifacts/construction/generation.json` for the exact prompt, revision, runtime and grading evidence.

The new video scores **1.0** on the intentional-change semantic skill, with a case-audit warning. A direct test of the released audit (`scripts/check_case_audit.py`) shows that replacing the concise intended change “open” with the full authored instruction changes its word-overlap value from **0.185848 (warning)** to **0.504689 (ok)**, with anchors and eight video judgments held fixed. The numerical grade is unchanged. This diagnostic is wording-sensitive; it is not an independent visual verification of success.

The offscreen semantic verifier gives the supplied torch clip **0.0**, yet its complete case score is **0.604199**: the released policy averages three core skills (offscreen semantics, trajectory and revisit), then blends that core mean 50/50 with observation quality. The demo shows both the primary skill and the full aggregation explicitly. A positive case score does not mean the principal requested behavior passed.
