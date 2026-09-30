"""Generate an actual local open-model rollout, then run the released semantic grader."""
from pathlib import Path
import os,json,time,sys,subprocess
R=Path(__file__).resolve().parents[1];os.environ.setdefault('CUDA_VISIBLE_DEVICES','0');os.environ['OMP_NUM_THREADS']='4'
# Keep the generation job separate from the metric job on GPU 0.
while not (R/'artifacts/download-generator.json').exists():time.sleep(5)
while not (R/'artifacts/construction/output.mp4').exists():
 usage=int(subprocess.check_output(['nvidia-smi','--id='+os.environ['CUDA_VISIBLE_DEVICES'],'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip())
 if usage<1500:break
 time.sleep(5)
sys.path.insert(0,str(R/'.genlibs'))
import torch,diffusers
# Host includes two incompatible FlashAttention-3 registrations. Use Torch SDPA.
import diffusers.utils.import_utils as iu
iu._xformers_available=False;iu._flash_attn_available=False;iu._flash_attn_3_available=False
from diffusers import WanImageToVideoPipeline,AutoencoderKLWan
from diffusers.utils import export_to_video,load_image
out=R/'artifacts/construction';model=R/'weights/generator';case=json.loads((out/'manifest.json').read_text())['cases'][0]
prompt=case['interaction']['action']['text']+' Fixed camera, one continuous shot, natural realistic motion.'
settings={'height':768,'width':1152,'num_frames':97,'num_inference_steps':50,'guidance_scale':5.0}
metadata={'model':'Wan-AI/Wan2.2-TI2V-5B-Diffusers','revision':json.loads((R/'artifacts/download-generator.json').read_text())['revision'],'seed':42,'prompt':prompt,'negative_prompt':'blurry, distorted, subtitles, camera movement, low quality','settings':settings,'fps':24,'diffusers':diffusers.__version__,'scope':'New locally generated example; separate from the six author-provided Seedance videos. Not a reproduction of the complete model leaderboard.'}
if (out/'output.mp4').exists():metadata=json.loads((out/'generation.json').read_text())
(out/'generation.json').write_text(json.dumps(metadata,indent=2));t=time.time()
if not (out/'output.mp4').exists():
 vae=AutoencoderKLWan.from_pretrained(model,subfolder='vae',torch_dtype=torch.float32)
 pipe=WanImageToVideoPipeline.from_pretrained(model,vae=vae,torch_dtype=torch.bfloat16)
 pipe.enable_model_cpu_offload();pipe.vae.enable_tiling()
 frames=pipe(image=load_image(str(out/'initial.png')),prompt=prompt,negative_prompt=metadata['negative_prompt'],generator=torch.Generator('cpu').manual_seed(42),**settings).frames[0]
 export_to_video(frames,str(out/'output.mp4'),fps=24)
 metadata['generation_seconds']=time.time()-t;(out/'generation.json').write_text(json.dumps(metadata,indent=2))
 del pipe,vae;import gc;gc.collect();torch.cuda.empty_cache()
if '--generate-only' in sys.argv:
 print('Generated local video',flush=True);sys.exit(0)
sys.path.insert(0,str(R/'upstream/src'))
from harnesseval.skills import skill_intentional_change_vlm as skill
from harnesseval.skill_backend.intentional_change_vlm import OpenAICompatibleBackend
backend=OpenAICompatibleBackend(base_url='http://127.0.0.1:8000/v1',model='local-judge',wire_api='chat_completions',timeout=600,retries=1)
r=skill.evaluate(out/'output.mp4',case,out/'initial.png',backend,cache_root=out/'evaluation')
metadata['evaluation']=r;metadata['video']='evidence/construction/output.mp4'
(out/'generation.json').write_text(json.dumps(metadata,indent=2));print('Generated and evaluated',r['result']['score'],flush=True)
