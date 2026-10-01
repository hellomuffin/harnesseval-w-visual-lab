"""Build public judge-comparison data without exporting credentials or binary requests."""
from pathlib import Path
import json,copy,statistics,sys
R=Path(__file__).resolve().parents[1];A=R/'artifacts/judge-comparison'
sys.path.insert(0,str(R/'upstream/src'))
from harnesseval.score import score_components,resolve_selected_skills
from harnesseval.aggregate import mean_valid
def read(p):return json.loads(p.read_text())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False))
D=read(R/'site/data/demo.json');rows=[]
labels={'intentional_transition':'Intentional transition: mug','physical_transition':'Physical response: wind and flag','offscreen_evolution':'Offscreen evolution: torch','frozen':'Temporal control: frozen mug','reversed':'Temporal control: reversed mug','generated_book':'Generated rollout: red book'}
for key,title in labels.items():
 row={'id':key,'title':title,'judges':{}}
 if key=='generated_book':row.update(video=D['generation']['video'],action=D['construction']['action'])
 else:
  family='intentional_transition' if key in ['frozen','reversed'] else key
  source_case=next(c for c in D['cases'] if c['taxonomy']['probe_family']==family)
  row.update(video='evidence/controls/'+key+'.mp4' if key in ['frozen','reversed'] else source_case['video'],action=source_case['interaction']['action'])
 for judge in ['muse','gpt']:
  p=A/judge/(key+'.json')
  if p.exists() and read(p).get('status')=='complete':
   d=read(p);row['judges'][judge]={'independent':d['independent'],'fixed_specification':d['fixed_specification'],'evidence':'evidence/judge-comparison/'+judge+'/'+key+'.json','model':d['model']}
 if key in ['frozen','reversed']:
  row['baseline']=next(x['result']['score'] for x in D['controls']['semantic'] if x['name']==key)
 elif key=='generated_book':row['baseline']=D['generation']['evaluation']['result']['score']
 else:
  c=next(c for c in D['cases'] if c['taxonomy']['probe_family']==key)
  ids={'intentional_transition':'intentional_change_verifier_vlm','physical_transition':'physical_response_verifier_vlm','offscreen_evolution':'offscreen_evolution_verifier'}
  row['baseline']=next(x['score'] for x in c['bundles']['fresh']['skill_results'] if x['skill_id']==ids[key])
 rows.append(row)
reports={}
for judge in ['muse','gpt']:
 full=True;family={};core_scores={};obs_scores={}
 for c in D['cases']:
  f=c['taxonomy']['probe_family'];bundle=copy.deepcopy(c['bundles']['fresh']);p=A/judge/(f+'.json')
  if f in labels:
   if not p.exists() or read(p).get('status')!='complete':full=False;continue
   r=read(p);replacement=r['independent']['result'];bundle['skill_runs'][replacement['skill_id']]={'evidence':'evidence/judge-comparison/'+judge+'/'+f+'.json','judge':r['model'],'execution':'new semantic inference'};bundle['provenance']={'type':'derived matched-judge bundle','numerical_source':'original fresh numerical cache, unchanged','semantic_judge':r['model'],'scoring_plan':'fixed released plan'};bundle['skill_results']=[replacement if x['skill_id']==replacement['skill_id'] else x for x in bundle['skill_results']]
   c['traces'][judge]={'expected_spec':r['independent']['analyze']['expected_spec'],'judgment':r['independent']['verify']['judgment'],'sampling':r['independent']['verify'].get('sampling'),'judge':r['model']}
  else:c['traces'][judge]={}
  c['bundles'][judge]=bundle
  route=A/judge/'routing'/(c['case_id']+'.json')
  if route.exists() and read(route).get('status')=='complete':
   r=read(route);c.setdefault('judge_plans',{})[judge]=r['plan'];c.setdefault('judge_routing_prompts',{})[judge]=r['conversation']
  scored=score_components(resolve_selected_skills(c['plan'],bundle))
  core_scores[f]=scored['core_score'];obs_scores[f]=scored['other_score'];family[f]=scored['final_score']
 if full:reports[judge]={'leaderboard':[{'family_scores':family,'family_core_scores':core_scores,'family_observation_scores':obs_scores,'overall_score':mean_valid(family.values())}]}
D['judge_reports']=reports
comparison={'models':{'muse':'Muse-Glimmer-30B','gpt':'GPT-5.5','baseline':'Qwen3-VL-8B (historical baseline)'},'rows':rows,'reports':reports,'settings':{j:read(A/j/'configuration.json') for j in ['muse','gpt'] if (A/j/'configuration.json').exists()},'complete':all(len(r['judges'])==2 for r in rows)}
paired=[r for r in rows if len(r['judges'])==2]
for mode in ['independent','fixed_specification']:
 deltas=[r['judges']['muse'][mode]['result']['score']-r['judges']['gpt'][mode]['result']['score'] for r in paired]
 comparison[mode+'_summary']={'paired_examples':len(deltas),'mean_absolute_score_difference':sum(abs(d) for d in deltas)/len(deltas) if deltas else None,'different_scores':sum(abs(d)>1e-6 for d in deltas)}
 if mode=='fixed_specification':
  assert all(r['judges']['muse'][mode]['request_digest']==r['judges']['gpt'][mode]['request_digest'] for r in paired),'Shared-prompt comparison mismatch'
write(R/'site/data/demo.json',D);write(R/'site/data/judge-comparison.json',comparison)
write(A/'comparison-summary.json',{k:v for k,v in comparison.items() if k!='rows'})
print('Paired judge examples',len(paired),'of',len(rows))
