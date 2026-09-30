from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json
R=Path(__file__).resolve().parents[1]
records=[]
for source,local in [('WBench-weights','weights'),('Qwen3-VL-8B-Instruct','weights/judge')]:
 for x in json.loads((R/f'research/{source}-files.json').read_text()):
  p=R/local/x['path']
  if x.get('type')=='file' and p.exists() and p.name != '_HPSv3_7B_resolved.yaml':records.append((source,x,p))
def check(t):
 source,x,p=t;expected=(x.get('lfs') or {}).get('oid');actual=None
 if expected:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(16*1024*1024),b''):h.update(b)
  actual=h.hexdigest()
 return {'repository':source,'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'expected_bytes':x['size'],'sha256':actual,'expected_sha256':expected,'valid':p.stat().st_size==x['size'] and (not expected or expected==actual)}
with ThreadPoolExecutor(4) as pool:out=list(pool.map(check,records))
(R/'artifacts/weights-audit.json').write_text(json.dumps({'status':'passed' if all(x['valid'] for x in out) else 'failed','files':out,'file_count':len(out),'excluded_runtime_config':'_HPSv3_7B_resolved.yaml is rewritten by upstream to resolve local paths; it is not a model checkpoint.'},indent=2));print(len(out),'files checked; all valid:',all(x['valid'] for x in out))
