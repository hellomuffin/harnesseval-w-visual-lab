from pathlib import Path
import json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1];U=ROOT/'upstream';A=ROOT/'artifacts';W=ROOT/'weights'
c=json.loads((U/'examples/backend_config.json').read_text().replace('<HARNESSEVAL_WEIGHTS_ROOT>',str(W)))
for key in ['intentional_change_verifier_vlm','physical_response_verifier_vlm','offscreen_evolution_verifier']:
 c['skills'][key].update(base_url='http://127.0.0.1:8000/v1',model='local-judge',wire_api='chat_completions',timeout=600)
c['skills']['drift_degradation_analyzer']['mode']='staged_local'
(A/'backend.json').write_text(json.dumps(c,indent=2))
manifest=U/'runs/example/results_example/manifest.json';generation=U/'runs/example/results_example/generation'
cmd=[sys.executable,'-m','harnesseval.cli','eval','inventory','--manifest',str(manifest),'--generation-root',str(generation),'--assets-root',str(U),'--model','seedance-2.0-standard','--output-root',str(A/'fresh/inventory'),'--full-decode','--execute','--workers','4']
r=subprocess.run(cmd,capture_output=True,text=True);(A/'logs/inventory.log').write_text(r.stdout+r.stderr);print(r.stdout[-3500:]);print('exit',r.returncode)
(A/'commands.json').write_text(json.dumps([{'command':cmd,'exit':r.returncode}],indent=2))
