from pathlib import Path
import psutil,time,subprocess,os
R=Path(__file__).resolve().parents[1]
while True:
 busy=[]
 for p in psutil.process_iter(['cmdline']):
  c=p.info['cmdline'] or []
  if len(c)>3 and c[1:3]==['-m','harnesseval.cli'] and 'physical_plausibility_inspector' in c:busy.append(p)
 if not busy:break
 time.sleep(2)
env=dict(os.environ,CUDA_VISIBLE_DEVICES='0',OMP_NUM_THREADS='4')
with (R/'artifacts/logs/trajectory-retry.log').open('w') as f:
 r=subprocess.run([str(R/'.venv/bin/python'),str(R/'scripts/run_skill.py'),'viewpoint_trajectory_verifier'],env=env,stdout=f,stderr=subprocess.STDOUT)
print('trajectory exit',r.returncode)
