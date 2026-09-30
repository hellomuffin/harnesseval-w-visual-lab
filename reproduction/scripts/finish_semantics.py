from pathlib import Path
import subprocess,requests,time,json
R=Path(__file__).resolve().parents[1]
for i in range(120):
 try:
  if requests.get('http://127.0.0.1:8000/v1/models',timeout=2).ok:break
 except requests.RequestException:pass
 time.sleep(2)
else:raise RuntimeError('Local judge did not start')
with (R/'artifacts/logs/stress-tests-fresh.log').open('w') as f:
 r=subprocess.run([str(R/'.venv/bin/python'),str(R/'scripts/stress_tests.py'),'--fresh'],stdout=f,stderr=subprocess.STDOUT)
 print('fresh controls',r.returncode,flush=True)
r=requests.post('http://127.0.0.1:8080/api/validate-case',json={'action':'Open the visible red book, keeping the blue mug, herb plant, counter and viewpoint unchanged.'},timeout=220)
(R/'artifacts/live-validator-check.json').write_text(json.dumps({'status_code':r.status_code,'body':r.json()},indent=2));print('live validator',r.status_code,flush=True)
