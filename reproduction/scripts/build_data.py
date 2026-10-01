from pathlib import Path
import json,sys,subprocess,hashlib,datetime,cv2
R=Path(__file__).resolve().parents[1];U=R/'upstream';A=R/'artifacts';S=R/'site';sys.path.insert(0,str(U/'src'))
from harnesseval.protocols import SKILLS,SKILL_SPECS,CORE_SKILLS,FAMILIES
import numpy as np
from harnesseval.pipeline.planner import build_plan, planner_messages, PROMPT_VERSION
read=lambda p:json.loads(p.read_text())
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False))
names={'exploratory_transition':'Explore a city','intentional_transition':'Tip the mug','physical_transition':'Turn up the wind','drift_resistance':'Walk through an old town','return_revisit_consistency':'Leave, then return','offscreen_evolution':'Look away from a flame'}
short={'exploratory_transition':'Exploration','intentional_transition':'Intentional change','physical_transition':'Physical response','drift_resistance':'Long-horizon drift','return_revisit_consistency':'Revisit','offscreen_evolution':'Offscreen evolution'}
manifest=read(U/'runs/example/results_example/manifest.json');release=U/'runs/example/results_example/run/harnesseval'
replays=[];cases=[]
for case in sorted(manifest['cases'],key=lambda c:FAMILIES.index(c['taxonomy']['probe_family'])):
 cid=case['case_id'];f=case['taxonomy']['probe_family'];plan=read(U/f'benchmark/plans/{f}/{cid}.skill_plan.json')
 gen=U/f'runs/example/results_example/generation/outputs/{case["taxonomy"]["primary_axis"]}/{f}/seedance-2.0-standard/{cid}'
 video=gen/'output.mp4';initial=U/case['world']['initial_observation']['path']
 media=S/'media'/cid;media.mkdir(parents=True,exist_ok=True)
 cap=cv2.VideoCapture(str(video));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS);frames=[]
 for i in range(6):
  idx=round((n-1)*i/5);out=media/f'{i}.jpg'
  if not out.exists():
   cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,img=cap.read()
   if ok:img=cv2.resize(img,(480,round(img.shape[0]*480/img.shape[1])));cv2.imwrite(str(out),img)
  frames.append({'image':f'media/{cid}/{i}.jpg','time':round(idx/fps,2)})
 cap.release()
 bundles={}
 for label,base in [('released',release/'metric_cache'),('fresh',A/'fresh/cache')]:
  p=base/f'bundles/seedance-2.0-standard/{f}/{cid}.metrics.json'
  bundles[label]=read(p) if p.exists() else {}
 traces={};tool_evidence={}
 for label,base in [('released',release/'metric_cache'),('fresh',A/'fresh/cache')]:
  traces[label]={}
  tool_evidence[label]={}
  for p in (base/'skills/viewpoint_trajectory').glob(f'**/{cid}.pose.npz'):
   with np.load(p) as poses:
    centers=poses['cam_c2w'][:,:3,3]
    tool_evidence[label]['trajectory']=centers[::max(1,len(centers)//200)].tolist()
  for p in (base/'skills/drift_degradation').glob(f'**/{cid}.json'):
   raw=read(p)
   if 'chunks' in raw:
    from harnesseval.formulas import quality_dimensions
    tool_evidence[label]['chunks']=[{'id':x['chunk_id'],'quality':quality_dimensions(x['metrics'])} for x in raw['chunks']]
  for p in (base/'skills/return_consistency').glob(f'**/{cid}.json'):
   raw=read(p);pairs=raw.get('evidence',{}).get('pairs',[])
   if pairs:
    plan_samples=raw.get('sample_plan',{}).get('sampled_frame_indices',[])
    selected=pairs[0].get('similarities',[])
    if selected and plan_samples:
     pair=selected[-1];pair_frames=[]
     cap=cv2.VideoCapture(str(video))
     for key in ['reference_sample','return_sample']:
      idx=plan_samples[pair[key]];out=media/f'{label}-{key}.jpg'
      if not out.exists():
       cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,img=cap.read()
       if ok:cv2.imwrite(str(out),cv2.resize(img,(384,216)))
      pair_frames.append({'image':f'media/{cid}/{label}-{key}.jpg','time':round(idx/fps,2)})
     cap.release();tool_evidence[label]['return_pair']={'frames':pair_frames,'metrics':pair}
  for family in ['intentional_change','physical_response','offscreen_evolution']:
   for stage in ['stage1','stage2','analyze_agent','verify_agent']:
    for p in (base/f'skills/{family}/{stage}').glob(f'**/{cid}.json'):
     d=read(p)
     for key in ['expected_spec','judgment','sampling']:
      if key in d:traces[label][key]=d[key]
     traces[label]['judge']=d.get('response_metadata',{}).get('model','unknown')
 # Reconstruct text directly from the pinned release and unmodified manifest case.
 routing_prompt={'prompt_version':PROMPT_VERSION,'source':'Reconstructed from the released planner and original manifest; historical raw routing requests were not retained.','messages':planner_messages(case),'initial_observation':'upstream/'+str(initial.relative_to(U)),'initial_observation_sha256':hashlib.sha256(initial.read_bytes()).hexdigest(),'generated_rollout_included':False}
 localp=A/f'fresh/plans/{f}/{cid}.skill_plan.json' 
 case.update(generation_prompt=read(gen/'metadata.json').get('prompt'),routing_prompt=routing_prompt,title=names[f],family_label=short[f],video='upstream/'+str(video.relative_to(U)),image='upstream/'+str(initial.relative_to(U)),frames=frames,duration=round(n/fps,2),plan=plan,fresh_plan=read(localp) if localp.exists() else None,bundles=bundles,traces=traces,tool_evidence=tool_evidence)
 cases.append(case)
 try:
  rebuilt=build_plan(plan,case,'replay-validation');replays.append({'case':cid,'valid':rebuilt['selected_skill_ids']==plan['selected_skill_ids']})
 except Exception as e:replays.append({'case':cid,'valid':False,'error':str(e)})
audits=[]
for p in (A/'fresh/cache/run_audits').glob('**/*.json'):
 d=read(p);audits.append({'path':'evidence/'+str(p.relative_to(A)),**{k:d.get(k) for k in ['created_at','status','status_counts','cache_hits','cache_misses','outcomes','run_context']}})
public=[]
for p in (R/'public-set/data').glob('*.json'):
 d=read(p)
 if isinstance(d,dict) and 'cases' in d:
  for c in d['cases']:
   im=next((R/'public-set/data/initial_observations').glob(c['case_id']+'.*'),None)
   public.append({'id':c['case_id'],'family':c['taxonomy']['probe_family'],'action':c.get('interaction',{}).get('action',{}),'image':'public/data/initial_observations/'+im.name if im else None})
data={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':subprocess.check_output(['git','-C',str(U),'rev-parse','HEAD'],text=True).strip(),'cases':cases,'skills':[{'id':x,**SKILL_SPECS[x]} for x in SKILLS],'audits':audits,'routing_validation':replays,'public':public,'reported':read(release/'models/seedance-2.0-standard/evaluation/summary.json')}
for key,path in [('generation',A/'construction/generation.json'),('baseline',A/'baseline/results.json'),('controls',A/'controls/results.json'),('construction',A/'construction/result.json'),('repeats',A/'repeats/results.json'),('score_replay',A/'replay/summary.json'),('fresh_report',A/'fresh/evaluation/summary.json')]:
 data[key]=read(path) if path.exists() else None
dump(S/'data/demo.json',data)
for name,target in [('upstream',U),('evidence',A),('public',R/'public-set')]:
 p=S/name
 if not p.exists():p.symlink_to(target,target_is_directory=True)
print('Built',len(cases),'rollout cases,',len(public),'public cases,',len(audits),'fresh audit records')
