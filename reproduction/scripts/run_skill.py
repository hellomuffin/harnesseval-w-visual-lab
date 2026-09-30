"""Execute released skill backends on bundled rollouts into a fresh cache."""
import os,sys,subprocess,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];U=R/'upstream';A=R/'artifacts'
os.environ['HARNESSEVAL_DEPENDENCIES_ROOT']=str(R/'dependencies')
os.environ['HARNESSEVAL_WEIGHTS_ROOT']=str(R/'weights')
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('HARNESSEVAL_LINEAR_PATCH_EMBED','1')
os.environ.setdefault('HARNESSEVAL_VISION_CHUNK_T','4')
os.environ.setdefault('HARNESSEVAL_SPARSE_EXPERTS','1')
args=sys.argv[1:];skill=args.pop(0)
cmd=[sys.executable,'-m','harnesseval.cli','eval','run-skills','--manifest',str(U/'runs/example/results_example/manifest.json'),'--inventory-root',str(A/'fresh/inventory'),'--plan-root',str(U/'benchmark/plans'),'--cache-root',str(A/'fresh/cache'),'--backend-config',str(A/'backend.json'),'--skill',skill,'--workers','1','--analyze-workers','1','--execute',*args]
t=time.time();result=subprocess.run(cmd)
print(json.dumps({'skill':skill,'seconds':time.time()-t,'exit':result.returncode}),flush=True)
sys.exit(result.returncode)
