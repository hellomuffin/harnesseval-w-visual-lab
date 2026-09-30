from pathlib import Path
import os,json,sys,subprocess,copy,time,datetime
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'upstream/src'))
from harnesseval.skills import skill_intentional_change_vlm as skill
from harnesseval.skill_backend.intentional_change_vlm import OpenAICompatibleBackend
from harnesseval.skills import skill_physical_law as law
from harnesseval.skill_backend.physical_law import LocalBackend
U=R/'upstream';A=R/'artifacts';out=A/'controls';out.mkdir(exist_ok=True)
m=json.loads((U/'runs/example/results_example/manifest.json').read_text());case=next(c for c in m['cases'] if c['taxonomy']['probe_family']=='intentional_transition');cid=case['case_id'];initial=U/case['world']['initial_observation']['path'];video=next((U/'runs/example/results_example/generation').glob(f'**/{cid}/output.mp4'))
run_suffix=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S') if '--fresh' in sys.argv else ''
backend=OpenAICompatibleBackend(base_url='http://127.0.0.1:8000/v1',model='local-judge',wire_api='chat_completions',timeout=600,retries=1)
rows=[]
for name in ['original','frozen','reversed']:
 p=out/f'{name}.mp4'
 if not p.exists():
  if name=='original':p.symlink_to(video)
  elif name=='frozen':subprocess.run(['ffmpeg','-y','-i',str(video),'-vf','select=eq(n\\,0),loop=loop=-1:size=1:start=0','-t','4.04','-r','24','-an','-c:v','libx264','-pix_fmt','yuv420p',str(p)],check=True,capture_output=True)
  else:subprocess.run(['ffmpeg','-y','-i',str(video),'-vf','reverse','-an','-c:v','libx264','-pix_fmt','yuv420p',str(p)],check=True,capture_output=True)
 # Distinct local path identity; no shipped cache is reused.
 r=skill.evaluate(p,case,initial,backend,cache_root=out/'cache'/run_suffix/name)
 rows.append({'name':name,'video':'evidence/controls/'+name+'.mp4','result':r['result'],'cache':'evidence/controls/cache/'+('/'.join(filter(None,[run_suffix,name]))),'cache_hit':r['cache_hit']})
 (out/'results.json').write_text(json.dumps({'semantic':rows},indent=2));print(name,r['result']['score'],flush=True)
reps=[]
for i in range(3):
 r=skill.evaluate(video,case,initial,backend,cache_root=A/'repeats'/run_suffix/str(i))
 reps.append({'run':i+1,'score':r['result']['score'],'cache_hit':r['cache_hit'],'metrics':r['result'].get('metrics')})
 (A/'repeats/results.json').write_text(json.dumps({'judge':'Qwen3-VL-8B-Instruct','case_id':cid,'runs':reps,'scope':'Single-case repeatability; not the human Bradley–Terry envelope experiment.'},indent=2));print('repeat',i,r['result']['score'],flush=True)
# Independent controlled animation: image coordinates increase downward.
import cv2,numpy as np
physics=[]
for kind in ['gravity_arc','inverted_arc','frozen_ball']:
 raw=out/f'{kind}-raw.mp4';p=out/f'{kind}.mp4';v=cv2.VideoWriter(str(raw),cv2.VideoWriter_fourcc(*'mp4v'),24,(640,360))
 for i in range(144):
  t=i/143;frame=np.full((360,640,3),235,np.uint8)
  cv2.line(frame,(0,330),(640,330),(80,90,80),2)
  x=int(80+480*t);y=int(290-800*t+800*t*t)
  if kind=='inverted_arc':y=350-y
  if kind=='frozen_ball':x,y=80,290
  cv2.circle(frame,(x,y),17,(25,120,210),-1);cv2.line(frame,(x-10,y),(x+10,y),(40,40,40),2);cv2.line(frame,(x,y-10),(x,y+10),(40,40,40),2)
  v.write(frame)
 v.release();subprocess.run(['ffmpeg','-y','-i',str(raw),'-c:v','libx264','-pix_fmt','yuv420p',str(p)],capture_output=True,check=True)
 c={'case_id':'control_'+kind,'taxonomy':{'probe_family':'physical_transition'},'world':{'source_tags':{'scene':'projectile_field'}},'non_model_facing':{'physical_engine':{'model_id':'projectile_2d'}}}
 r=law.evaluate(p,c,LocalBackend(),cache_root=out/'physics-cache')
 physics.append({'name':kind,'video':'evidence/controls/'+p.name,'result':r['result']});print(kind,r['result'],flush=True)
(out/'results.json').write_text(json.dumps({'semantic':rows,'physics':physics},indent=2))
