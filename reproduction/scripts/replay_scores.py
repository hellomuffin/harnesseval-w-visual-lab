from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parents[1];U=R/'upstream';A=R/'artifacts'
base=U/'runs/example/results_example'
cmd=[sys.executable,'-m','harnesseval.cli','eval','score','--generation-root',str(base/'generation'),'--plan-root',str(U/'benchmark/plans'),'--cache-root',str(base/'run/harnesseval/metric_cache'),'--eval-root',str(A/'replay'),'--execute']
r=subprocess.run(cmd,capture_output=True,text=True,cwd=U);(A/'logs/score-replay.log').write_text(r.stdout+r.stderr);print(r.stdout[-3500:]);print('exit',r.returncode)
