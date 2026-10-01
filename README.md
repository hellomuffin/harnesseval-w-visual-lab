# HarnessEval-W: Academic Project Page and Reproduction Study

**Open https://hellomuffin.github.io/harnesseval-w-visual-lab/**

A hosted visual introduction and independently executed reproduction study of [HarnessEval-W](https://mirros-lab.github.io/HarnessEval-W/).

- Six author-supplied videos, all 11 skills exercised on videos or controlled fixtures, and 100 public cases.
- A new locally generated Wan 2.2 video, real Analyze/Verify traces, recorded case validation, and interactive grading.
- Matched Muse-Glimmer-30B and GPT-5.5 semantic evaluation, including independent Analyze–Verify and a shared-specification condition.
- Exact new routing requests, reconstructed historical routing prompts, and recorded generation prompts are visible.
- Historical Qwen six-case overall: 0.754987. Author-cache replay: 0.787629.
- Numerical evidence is held fixed across judges; new routing experiments are shown separately from the fixed scoring plan. The full 330-case, 18-model leaderboard and human study are not reproduced.

This is a static website: videos, traces, plots, recorded validation and grading sliders work without a local server. New GPU inference is not available from the hosted UI. Browser scoring is independently checked against the released Python formula.

Original research, benchmark assets and released model videos belong to their respective authors. Sources: [paper](https://arxiv.org/html/2608.16859v2), [code](https://github.com/MirroS-Lab/HarnessEval-W), [dataset](https://huggingface.co/datasets/MirroS-Lab/HarnessEval-W). New reproduction artifacts, implementation patches and model revisions are under `evidence/`; code to reproduce the experiments is under `reproduction/`. Machine-specific workspace prefixes have been redacted in public text receipts; numerical evidence is unchanged. Model weights and runtime environments are not included.
