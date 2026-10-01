"""Matched semantic-judge comparison using released prompts, sampling, and formulas.
Credentials are read from OPENAI_API_KEY or an unexported private file, never receipts.
"""
from pathlib import Path
import argparse,base64,copy,hashlib,json,os,sys,time
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'upstream/src'))
from harnesseval.skill_backend.intentional_change_vlm import OpenAICompatibleBackend
from harnesseval.skills import skill_intentional_change_vlm as intentional,skill_physical_response_vlm as physical,skill_offscreen_evolution as offscreen
from harnesseval.pipeline.planner import planner_messages,build_plan,initial_observation_path
from harnesseval.io import value_digest
A=R/'artifacts/judge-comparison';U=R/'upstream'
MODULES={'intentional_transition':intentional,'physical_transition':physical,'offscreen_evolution':offscreen}
def read(p):return json.loads(Path(p).read_text())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False))
def compact(x):
 if isinstance(x,dict):return {k:compact(v) for k,v in x.items()}
 if isinstance(x,list):return [compact(v) for v in x]
 if isinstance(x,str) and x.startswith('data:image/'):
  head,body=x.split(',',1);b=base64.b64decode(body);return {'type':'image_reference','mime':head.split(';')[0][5:],'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 return x
class Judge(OpenAICompatibleBackend):
 def __init__(self,name,schema=intentional.BACKEND_OUTPUT_SCHEMA):
  self.name=name;self.schema=schema
  key=(os.environ.get('OPENAI_API_KEY') or (R/'.private/openai-key').read_text().strip()) if name=='gpt' else None
  super().__init__('https://api.openai.com/v1' if name=='gpt' else 'http://127.0.0.1:8001/v1','gpt-5.5' if name=='gpt' else 'meta-models/Muse-Glimmer-30B',api_key=key,wire_api='chat_completions',timeout=900,retries=1)
  self.settings={'reasoning_effort':'medium','temperature':'API default (temperature=0 unsupported)','max_completion_tokens':16384} if name=='gpt' else {'temperature':0,'max_tokens':16384,'reasoning_strength':'medium','structured_output':'JSON requested in prompt; native Muse channel protocol'}
  self.config_digest=value_digest({'base_digest':self.config_digest,'settings':self.settings})
 def _targets_and_body(self,messages):
  urls,body=super()._targets_and_body(messages)
  if self.name=='gpt':body.pop('temperature',None);body.update(reasoning_effort='medium',max_completion_tokens=16384)
  else:body.update(max_tokens=16384,chat_template_kwargs={'reasoning_strength':'medium','structured_output':'JSON requested in prompt; native Muse channel protocol'})
  return urls[:1],body
 def infer(self,messages):
  out=super().infer(messages);out['schema_version']=self.schema
  out['provenance']={'settings':self.settings,'request_sha256':value_digest(messages)}
  return out

def tasks():
 cases=read(U/'runs/example/results_example/manifest.json')['cases'];items=[]
 for c in cases:
  f=c['taxonomy']['probe_family']
  if f not in MODULES:continue
  v=next((U/'runs/example/results_example/generation').glob('**/'+c['case_id']+'/output.mp4'))
  items.append((f,c,v,U/c['world']['initial_observation']['path']))
 mug=next(x for x in items if x[0]=='intentional_transition')
 for kind in ['frozen','reversed']:items.append((kind,mug[1],R/f'artifacts/controls/{kind}.mp4',mug[3]))
 c=read(R/'artifacts/construction/manifest.json')['cases'][0]
 g=read(R/'artifacts/construction/generation.json');v=R/g['video'].replace('evidence/','artifacts/')
 items.append(('generated_book',c,v,R/'artifacts/construction/initial.png'))
 return cases,items

def run(name,examples=None,routing_only=False):
 base=A/name;rows=[];cases,items=tasks();items=[] if routing_only else [x for x in items if not examples or x[0] in examples];save(base/'configuration.json',{'model':Judge(name).model,'settings':Judge(name).settings,'muse_revision':'a4e59da52a7bc87ae7251dd5545c0dd437c44b68','protocol':'Independent Analyze–Verify plus fixed expected-specification Verify; identical video and frame sampling; released prompts and formulas; six semantic examples, not a population study.'})
 for label,c,v,image in items:
  dest=base/(label+'.json')
  if dest.exists() and read(dest).get('status')=='complete':rows.append(read(dest));continue
  mod=MODULES[c['taxonomy']['probe_family']];judge=Judge(name,mod.BACKEND_OUTPUT_SCHEMA);t=time.time()
  print(name,label,'started',flush=True)
  try:
   result=mod.evaluate(v,c,image,judge,cache_root=R/'.private/judge-cache'/name/label)
   analyze=read(result['analyze_agent_cache_path']);verify=read(result['verify_agent_cache_path'])
   shared_path=A/'shared-specifications'/(label+'.json')
   if shared_path.exists():shared=read(shared_path)
   else:
    # Freeze an existing Qwen expected specification BEFORE comparing the new judges.
    source=R/'artifacts/fresh/cache' if label not in ['generated_book','frozen','reversed'] else R/'artifacts'
    candidates=[p for p in source.glob('**/analyze_agent/**/*.json') if p.name==c['case_id']+'.json']
    if not candidates:raise RuntimeError('No existing shared Analyze specification found')
    p=sorted(candidates)[0];old=read(p);shared={'expected_spec':old['expected_spec'],'source':str(p.relative_to(R)),'source_judge':'existing Qwen baseline','case_id':c['case_id']};save(shared_path,shared)
   frames,sampling=mod._sample_video(v);messages=mod.video_judge_messages(mod.canonical_spec(c),shared['expected_spec'],image,frames,*([sampling] if mod is offscreen else []))
   out=judge.infer(messages);fixed=mod.result_from_judgment(out['parsed'],mod.canonical_spec(c),shared['expected_spec'])
   row={'status':'complete','example':label,'case_id':c['case_id'],'model':judge.model,'video_sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'independent':{'result':result['result'],'analyze':compact(analyze),'verify':compact(verify)},'fixed_specification':{'result':fixed,'expected_spec':shared['expected_spec'],'conversation':compact(messages),'request_digest':value_digest(messages),'output':out,'sampling':sampling},'elapsed_seconds':time.time()-t}
   save(dest,row);rows.append(row);print(name,label,'scores',result['result']['score'],fixed['score'],flush=True)
  except Exception as e:
   error=str(e);key=judge.api_key
   if key:error=error.replace(key,'[redacted]')
   save(dest,{'status':'failed','example':label,'error':error});print(name,label,'FAILED',error[:250],flush=True)
  save((R/'.private')/('judge-summary-'+str(os.getpid())+'.json') if examples or routing_only else base/'summary.json',{'model':Judge(name).model,'completed':len(rows),'expected':len(items),'results':[{'example':r['example'],'independent_score':r['independent']['result']['score'],'fixed_score':r['fixed_specification']['result']['score']} for r in rows]})
 save((R/'.private')/('judge-summary-'+str(os.getpid())+'.json') if examples or routing_only else base/'summary.json',{'model':Judge(name).model,'completed':len(rows),'expected':len(items),'results':[{'example':r['example'],'independent_score':r['independent']['result']['score'],'fixed_score':r['fixed_specification']['result']['score']} for r in rows]})
 if examples:return
 # Routing remains separate from score comparison so changed plans do not confound judge effects.
 for c in cases:
  dest=base/'routing'/(c['case_id']+'.json')
  if dest.exists() and read(dest).get('status')=='complete':continue
  msgs=planner_messages(c);image=initial_observation_path(c,U);url='data:image/png;base64,'+base64.b64encode(image.read_bytes()).decode()
  messages=[{'role':m['role'],'content':[{'type':'text','text':m['content']}]+([{'type':'image_url','image_url':url}] if m['role']=='user' else [])} for m in msgs]
  try:
   out=Judge(name).infer(messages);plan=build_plan(out['parsed'],c,value_digest(messages));save(dest,{'status':'complete','plan':plan,'conversation':compact(messages),'output':out});print(name,'routing',c['taxonomy']['probe_family'],'complete',flush=True)
  except Exception as e:save(dest,{'status':'failed','error':str(e)});print(name,'routing failed',type(e).__name__,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('judge',choices=['gpt','muse']);p.add_argument('--examples',nargs='+');p.add_argument('--routing-only',action='store_true');args=p.parse_args();run(args.judge,args.examples,args.routing_only)
