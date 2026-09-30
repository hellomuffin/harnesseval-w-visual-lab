from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parents[1];U=R/'upstream';A=R/'artifacts'
base=U/'runs/example/results_example'
cmd=[sys.executable,'-m','harnesseval.cli','eval','score','--generation-root',str(base/'generation'),'--plan-root',str(U/'benchmark/plans'),'--cache-root',str(A/'fresh/cache'),'--eval-root',str(A/'fresh/evaluation'),'--refresh-stale','--execute']
r=subprocess.run(cmd,capture_output=True,text=True,cwd=U);(A/'logs/fresh-scoring.log').write_text(r.stdout+r.stderr);print('score exit',r.returncode)
cmd=[sys.executable,'-m','harnesseval.cli','verify','run','--eval-root',str(A/'fresh/evaluation'),'--manifest',str(base/'manifest.json'),'--model','seedance-2.0-standard','--output',str(A/'fresh/VERIFY.json')]
r=subprocess.run(cmd,capture_output=True,text=True,cwd=U);(A/'logs/fresh-verification.log').write_text(r.stdout+r.stderr);print('verify exit',r.returncode)
