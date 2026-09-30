"""Sequential GPU schedule; never mixes a large PAVRM run with another model."""
from pathlib import Path
import os,sys,subprocess,json,time,psutil
R=Path(__file__).resolve().parents[1];A=R/'artifacts';log=A/'logs';results=[]
wait_pid=int(sys.argv[1]) if len(sys.argv)>1 else None
if wait_pid:
 while psutil.pid_exists(wait_pid):time.sleep(2)
def run(name,skill,envname='.venv',extra=(),gpus='0'):
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpus,OMP_NUM_THREADS='4',HARNESSEVAL_DEPENDENCIES_ROOT=str(R/'dependencies'))
 cmd=[str(R/envname/'bin/python'),str(R/'scripts/run_skill.py'),skill,*extra]
 with (log/(name+'.log')).open('w') as f:
  t=time.time();r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 results.append({'name':name,'command':cmd,'exit':r.returncode,'seconds':round(time.time()-t,2)});(A/'metric-schedule.json').write_text(json.dumps(results,indent=2));print(name,r.returncode,flush=True)
run('drift-physical','drift_degradation_analyzer',extra=['--drift-stage','physical'],gpus='0,1')
run('render-final','render_quality_inspector',envname='.hpsenv')
run('drift-render','drift_degradation_analyzer',envname='.hpsenv',extra=['--drift-stage','render'])
run('trajectory','viewpoint_trajectory_verifier')
run('drift-motion','drift_degradation_analyzer',extra=['--drift-stage','motion'])
run('drift-clip','drift_degradation_analyzer',extra=['--drift-stage','clip'])
run('drift-final','drift_degradation_analyzer')
