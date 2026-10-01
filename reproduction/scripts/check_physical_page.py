from playwright.sync_api import sync_playwright
import sys
url=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8094/physical-transition/'
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000});errors=[];failed=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:failed.append(r.url) if r.status>=400 else None)
 page.goto(url,wait_until='networkidle');assert page.locator('#questions tr').count()==8
 for mode in ['independent','fixed_specification']:
  page.select_option('#condition',mode)
  for i in range(8):
   page.locator('#questions button').nth(i).click();assert len(page.locator('#reasons').inner_text())>80
 for x,y,val in [(False,False,'0.345410'),(True,False,'0.483574'),(False,True,'0.460547'),(True,True,'0.644766')]:
  page.locator('#swap-q2').set_checked(x);page.locator('#swap-q8').set_checked(y);assert page.locator('#counterfactual').inner_text()==val,(x,y,page.locator('#counterfactual').inner_text())
 for n in range(9):
  page.locator('#frame').fill(str(n));page.locator('#frame').dispatch_event('input');page.wait_for_function('document.querySelector("#sequence-image").complete');assert page.locator('#sequence-image').evaluate('(e)=>e.naturalWidth')>0
 page.locator('#play-sequence').click();page.wait_for_timeout(650);assert page.locator('#frame').input_value()!='0';page.locator('#reset-sequence').click();assert page.locator('#frame').input_value()=='0'
 page.locator('#video').evaluate('(v)=>{v.currentTime=2}');page.wait_for_function('document.querySelector("#video").readyState>=2');assert page.locator('#video').evaluate('(v)=>v.videoWidth')>0
 page.select_option('#condition','independent');page.locator('#questions button').nth(1).click();page.locator('#swap-q2').uncheck();page.locator('#swap-q8').uncheck();page.evaluate('scrollTo(0,0)');page.screenshot(path='artifacts/academic-physical-desktop.png',full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.reload(wait_until='networkidle');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path='artifacts/academic-physical-mobile.png',full_page=True)
 assert not errors,errors;assert not failed,failed
 print('Passed: both judgment conditions; question explanations; score substitutions; frame scrubbing and playback; video loading; mobile layout; no browser or asset errors.')
 b.close()
