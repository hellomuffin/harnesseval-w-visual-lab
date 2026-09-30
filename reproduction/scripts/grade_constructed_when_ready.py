from pathlib import Path
import time,requests,subprocess,sys
R=Path(__file__).resolve().parents[1]
for _ in range(120):
 try:
  r=requests.get('http://127.0.0.1:8000/health',timeout=2)
  if r.ok:break
 except requests.RequestException:pass
 time.sleep(5)
else:raise RuntimeError('Local judge did not become ready')
subprocess.run([sys.executable,str(R/'scripts/generate_case_video.py')],check=True)
subprocess.run([sys.executable,str(R/'scripts/build_data.py')],check=True)
