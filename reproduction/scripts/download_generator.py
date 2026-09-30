import os,json
from pathlib import Path
os.environ['HF_HUB_DISABLE_XET']='1'
from huggingface_hub import HfApi,snapshot_download
R=Path(__file__).resolve().parents[1];repo='Wan-AI/Wan2.2-TI2V-5B-Diffusers';info=HfApi().model_info(repo)
print(repo,info.sha,flush=True)
snapshot_download(repo,revision=info.sha,local_dir=R/'weights/generator',max_workers=4)
(R/'artifacts/download-generator.json').write_text(json.dumps({'repo':repo,'revision':info.sha,'path':'weights/generator'},indent=2))
