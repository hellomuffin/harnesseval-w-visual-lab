from pathlib import Path
import os,time
R=Path(__file__).resolve().parents[1]
os.environ['HARNESSEVAL_LINEAR_PATCH_EMBED']='1';os.environ['HARNESSEVAL_VISION_CHUNK_T']='4'
from harnesseval.metrics.physical_plausibility import PhysicalPlausibilityEvaluator
m=PhysicalPlausibilityEvaluator(model_path=str(R/'weights/qwen3vl-a3b-visual-plausibility'))
p=next((R/'upstream/runs/example/results_example/generation').glob('**/harnesseval_w_drift_0001_old_town_lane/output.mp4'))
inputs=m.prepare_video(str(p));print({k:tuple(v.shape) for k,v in inputs.items() if hasattr(v,'shape')},flush=True)
print(m.score_prepared(inputs),flush=True)
