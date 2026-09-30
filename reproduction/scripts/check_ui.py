from playwright.sync_api import sync_playwright
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:8080',wait_until='networkidle');page.screenshot(path=str(R/'artifacts/desktop.png'),full_page=True)
 assert page.locator('#run-stats .stat strong').nth(1).inner_text()=='11 / 11'
 assert page.locator('#run-stats .stat strong').nth(2).inner_text()=='34'
 print('title',page.title(),'case-tabs',page.locator('#case-tabs button').count(),'skills',page.locator('.skill-tile').count())
 source_links=[]
 for tile in page.locator('.skill-tile').all():
  tile.click();url=page.locator('#skill-detail a').evaluate('(a)=>a.href');status=page.request.get(url).status;source_links.append({'url':url,'status':status});assert status==200
 if '--live' in sys.argv:
  page.locator('#new-action').fill('Open the red book on the counter.');page.locator('#case-form button').click();page.wait_for_function("document.querySelector('#validation-output a') !== null",timeout=180000);print('Live form:',page.locator('#validation-output').inner_text())
 for button in page.locator('#case-tabs button').all():
  button.click()
  for stage in page.locator('.stage-tabs button').all():stage.click()
  assert 'No complete case score' not in page.locator('#stage-content').inner_text()
  assert 'core mean' in page.locator('#stage-content').inner_text()
 if page.locator('#generated-video').count():
  assert page.locator('.generated-filmstrip button').count()==6
  page.locator('.generated-filmstrip button').last.click();page.wait_for_timeout(300)
  assert abs(page.locator('#generated-video').evaluate('(v)=>v.currentTime')-4)<.1
  hidden_header=page.add_style_tag(content='header{visibility:hidden!important}');page.locator('.generation-card').screenshot(path=str(R/'artifacts/generated-case.png'));hidden_header.evaluate('(e)=>e.remove()')
 assert page.locator('.protocol-comparison tbody tr').count()==3
 page.locator('#run-select').select_option('released');page.locator('[data-stage="verify"]').click()
 page.locator('#q0').fill('0');page.locator('#q0').dispatch_event('input');page.wait_for_timeout(400);assert page.locator('#whatif-score').inner_text()=='0.000'
 page.locator('#initial-toggle').click();assert page.locator('#image-dialog').is_visible();page.locator('#close-dialog').click()
 page.locator('#public-filter').select_option('intentional_transition');assert page.locator('.public-card').count()==10
 page.set_viewport_size({'width':390,'height':844});page.goto('http://127.0.0.1:8080',wait_until='networkidle');page.screenshot(path=str(R/'artifacts/mobile.png'),full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Mobile horizontal overflow'
 print('errors',errors);assert not errors
 (R/'artifacts/ui-check.json').write_text(json.dumps({'desktop':'1440x1000','mobile':'390x844','case_count':6,'skills':11,'tab_interactions':'passed','aggregation_gate':'passed','image_dialog':'passed','public_filter':'passed','horizontal_overflow':False,'browser_errors':errors,'skill_source_links':source_links,'live_validator_form':'passed' if '--live' in sys.argv else 'not tested in this run'},indent=2));browser.close()
