from pathlib import Path
import json,random,re,sys
from playwright.sync_api import sync_playwright
from harnesseval.skills.skill_intentional_change_vlm import aggregate_q_scores,normalize_q_scores
R=Path(__file__).resolve().parents[1];url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8082/'
rng=random.Random(17);vectors=[[rng.choice([0,.25,.5,.75,1]) for _ in range(8)] for _ in range(5000)]+[[0]*8,[1]*8]
expected=[aggregate_q_scores(normalize_q_scores({'q_scores':{'Q'+str(i+1):v for i,v in enumerate(q)}}))['final_score'] for q in vectors]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000});errors=[];api=[];bad=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:api.append(r.url) if '/api/' in r.url else None)
 page.on('response',lambda r:bad.append((r.status,r.url)) if r.status>=400 else None)
 page.goto(url,wait_until='networkidle');page.wait_for_selector('#case-tabs button')
 actual=page.evaluate('(qs)=>qs.map(hostedScore)',vectors);assert all(abs(a-e)<1e-6 for a,e in zip(actual,expected))
 for t in page.locator('#case-tabs button').all():
  t.click()
  for stage in page.locator('.stage-tabs button').all():stage.click()
 assert page.locator('#skill-grid .skill-tile').count()==11
 page.locator('#q0').fill('0');page.locator('#q0').dispatch_event('input');assert page.locator('#whatif-score').inner_text()=='0.000'
 page.locator('#recorded-case').select_option('1');assert 'Rejected' in page.locator('#validation-output').inner_text()
 page.locator('#recorded-case').select_option('0');assert 'Accepted' in page.locator('#validation-output').inner_text()
 page.locator('.generated-filmstrip button').last.click();page.wait_for_timeout(300);assert abs(page.locator('#generated-video').evaluate('(v)=>v.currentTime')-4)<.1
 page.locator('#public-filter').select_option('intentional_transition');assert page.locator('.public-card').count()==10
 page.screenshot(path=str(R/'artifacts/pages-desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.goto(url,wait_until='networkidle');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(R/'artifacts/pages-mobile.png'),full_page=True)
 assert not errors,errors;assert not api,api;assert not bad,bad
 b.close()
receipt={'status':'passed','formula_vectors':len(vectors),'max_absolute_error':max(abs(a-e) for a,e in zip(actual,expected)),'browser_errors':errors,'api_requests':api,'failed_asset_requests':bad,'case_tabs':6,'skills':11,'recorded_validation':'accepted and rejected executions verified','generated_video_seeking':'passed','mobile_overflow':False}
(R/'publish/evidence/hosted-formula-check.json').write_text(json.dumps(receipt,indent=2));(R/'artifacts/pages-check.json').write_text(json.dumps(receipt,indent=2));print(receipt)
# Fail publication if an actual credential pattern slipped into the curated export.
for path in (R/'publish').rglob('*'):
 if path.is_file() and path.suffix in ['.json','.js','.html','.md','.txt','.py','.patch']:
  assert not re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{32,}',path.read_text()),'Credential-like string in '+str(path)
print('Export credential-pattern check passed')
