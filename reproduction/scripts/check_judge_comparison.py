"""Verify matched inputs, official score recomputation, provenance, and hosted interactions."""
from pathlib import Path
import json,sys,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'upstream/src'))
from harnesseval.skills import skill_intentional_change_vlm as intentional,skill_physical_response_vlm as physical,skill_offscreen_evolution as offscreen
from harnesseval.score import score_components,resolve_selected_skills
from playwright.sync_api import sync_playwright
D=json.loads((R/'site/data/demo.json').read_text());J=json.loads((R/'site/data/judge-comparison.json').read_text())
assert J['complete'] and len(J['rows'])==6
counts=0
for row in J['rows']:
 mod={'physical_transition':physical,'offscreen_evolution':offscreen}.get(row['id'],intentional)
 a=row['judges']['muse'];b=row['judges']['gpt']
 assert a['fixed_specification']['request_digest']==b['fixed_specification']['request_digest']
 for judge in ['muse','gpt']:
  for mode in ['independent','fixed_specification']:
   x=row['judges'][judge][mode];judgment=x['verify']['judgment'] if mode=='independent' else x['output']['parsed'];q=mod.normalize_q_scores(judgment)
   assert len(q)==8 and all(isinstance(v,(int,float)) and v in {0,.25,.5,.75,1} for v in q.values()),(row['id'],judge,mode,q)
   score=mod.aggregate_q_scores(q)['final_score'];assert score==x['result']['score'];counts+=1
   responses=[x['analyze']['raw_response'],x['verify']['raw_response']] if mode=='independent' else [x['output']['raw_response']]
   assert all(r['choices'][0]['finish_reason']=='stop' for r in responses),(row['id'],judge,'truncated output')
for c in D['cases']:
 for judge in ['muse','gpt']:
  assert c['judge_plans'][judge]['validation']['status']=='ok'
  s=score_components(resolve_selected_skills(c['plan'],c['bundles'][judge]))
  assert s['final_score']==D['judge_reports'][judge]['leaderboard'][0]['family_scores'][c['taxonomy']['probe_family']]
  for old in c['bundles']['fresh']['skill_results']:
   if old['skill_id'] not in ['intentional_change_verifier_vlm','physical_response_verifier_vlm','offscreen_evolution_verifier']:
    assert next(x for x in c['bundles'][judge]['skill_results'] if x['skill_id']==old['skill_id'])==old
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8082/'
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1100});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url,wait_until='networkidle');page.wait_for_selector('#judge-rows tr')
 assert page.locator('#judge-rows tr').count()==6
 for case in page.locator('#case-tabs button').all():
  case.click()
  for judge in ['muse','gpt','fresh','released']:
   page.locator('#run-select').select_option(judge)
   for stage in ['route','analyze','verify','grade']:
    page.locator('[data-stage="'+stage+'"]').click()
    assert page.locator('#stage-content').inner_text().strip()
   page.locator('[data-stage="route"]').click();page.locator('.routing-prompt > summary').click();assert 'You are an evaluation skill planner.' in page.locator('.routing-prompt').inner_text()
 for mode in ['independent','fixed_specification']:
  page.locator('#judge-mode').select_option(mode)
  for i in range(6):
   page.locator('#judge-example').select_option(str(i));assert page.locator('#judge-detail tbody tr').count()==8
 page.set_viewport_size({'width':390,'height':844});page.reload(wait_until='networkidle');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert not errors,errors;b.close()
receipt={'status':'passed','paired_examples':6,'official_semantic_formula_recomputations':counts,'matched_fixed_specification_request_hashes':6,'validated_routing_plans':12,'workbench_case_judge_stage_combinations':96,'question_level_table_conditions':12,'numerical_backend_evidence':'unchanged','browser_errors':errors,'mobile_overflow':False}
(R/'artifacts/judge-comparison/verification.json').write_text(json.dumps(receipt,indent=2));print(receipt)
