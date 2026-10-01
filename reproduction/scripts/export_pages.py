"""Export a server-independent GitHub Pages edition with recorded evidence."""
from pathlib import Path
import shutil,json,re
R=Path(__file__).resolve().parents[1];P=R/'publish';P.mkdir(exist_ok=True)
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for name in ['index.html','style.css','app.js']:copy(R/'site'/name,P/name)
for name in ['media','data']:shutil.copytree(R/'site'/name,P/name,dirs_exist_ok=True)
# Curated evidence only: no runtime environments, model weights, credentials or server logs.
for src in (R/'artifacts').rglob('*'):
 rel=src.relative_to(R/'artifacts')
 if src.is_file() and 'logs' not in rel.parts and src.suffix in ['.json','.mp4','.png','.jpg','.npz','.patch','.py','.txt'] and src.name not in ['desktop.png','mobile.png','hero.png','generated-case.png']:
  if '-raw.mp4' not in src.name and not src.name.startswith('academic-') and not src.name.endswith(('desktop.png','mobile.png')):copy(src,P/'evidence'/rel)
for src in (R/'public-set/data').rglob('*'):
 if src.is_file() and src.suffix in ['.json','.png','.jpg','.jpeg']:copy(src,P/'public/data'/src.relative_to(R/'public-set/data'))
D=json.loads((P/'data/demo.json').read_text())
for c in D['cases']:
 for key in ['video','image']:
  src=R/c[key];copy(src,P/c[key])
# Replace the local API dependency with a numerically checked browser port.
p=P/'app.js';s=p.read_text();a=s.index('let scoreRequest=');b=s.index('function renderConstruction()',a)
s=s[:a]+'''function pyRound6(x){if(x===0)return 0;const view=new DataView(new ArrayBuffer(8));view.setFloat64(0,x);const bits=view.getBigUint64(0),exp=Number((bits>>52n)&2047n);const mantissa=(bits&((1n<<52n)-1n))+(exp?1n<<52n:0n);const power=(exp||1)-1023-52;let n=mantissa*1000000n,d=1n;if(power<0)d<<=BigInt(-power);else n<<=BigInt(power);let q=n/d;const rem=n%d;if(2n*rem>d||(2n*rem===d&&(q&1n)))q++;return Number(q)/1e6}
function hostedScore(q){const round=pyRound6;const change=round(.4*q[1]+.6*q[2]),preservation=round(.6*q[5]+.4*q[6]);const core=round(.30*change+.25*q[4]+.20*q[3]+.25*preservation);return round(q[0]*q[7]*core)}
function recompute(){const q=$$('#sliders input').map(x=>Number(x.value));$$('#sliders output').forEach((o,i)=>o.textContent=q[i].toFixed(2));$('#whatif-score').textContent=num(hostedScore(q))}
'''+s[b:]
a=s.index("$('#case-form').onsubmit=");b=s.index('\n',a)
s=s[:a]+s[b:]
s=s.replace('href="upstream/src/', 'href="https://github.com/MirroS-Lab/HarnessEval-W/blob/${D.commit}/src/')
s+='''
const hostedConstruction=renderConstruction;renderConstruction=function(){hostedConstruction();const c=D.construction;const options=[{name:'Accepted · open the book',action:c.action,validation:c.validation},{name:'Rejected · reveal a recipe',action:c.previous_attempt.plan.action_text,validation:c.previous_attempt.validation}];$('#case-form').innerHTML='<div><span class="tiny-label">Case feasibility and judgeability</span><h3>Case-Validation Outcomes</h3><p>The validator checks whether the proposed action is grounded in the initial image and whether its outcome can be judged from a future rollout. Select an action to inspect its recorded assessment.</p></div><label for="recorded-case">Action specification</label><select id="recorded-case">'+options.map((x,i)=>'<option value="'+i+'">'+esc(x.name)+'</option>').join('')+'</select><div id="validation-output" role="status"></div>';const show=()=>{const x=options[Number($('#recorded-case').value)];$('#validation-output').innerHTML='<p><b>Proposed action:</b> '+esc(x.action)+'</p>'+tag(x.validation.valid?'Accepted':'Rejected',x.validation.valid?'teal':'amber')+'<p>'+esc(x.validation.reason)+'</p><div class="chips">'+Object.entries(x.validation.checks||{}).map(([k,v])=>'<span>'+esc(nice(k))+': '+(v?'yes':'no')+'</span>').join('')+'</div><a href="evidence/construction/result.json" target="_blank">Inspect the validation prompt and response ↗</a>'};$('#recorded-case').onchange=show;show()};
'''
p.write_text(s)
p=P/'index.html';s=p.read_text().replace('INTERACTIVE · RELEASED FORMULA','INTERACTIVE · VERIFIED BROWSER FORMULA').replace('The server runs the paper repository’s aggregation code.','The browser runs a port of the released formula, checked against the Python implementation.').replace('INTERACTIVE REPRODUCTION LAB','HOSTED REPRODUCTION LAB')
s=s.replace('<p><a href="evidence/formula-checks.json">','<p><a href="evidence/hosted-formula-check.json">Browser formula equivalence</a> · <a href="evidence/formula-checks.json">')
s=s.replace('python scripts/download_models.py\npython scripts/fetch_dependencies.py\n.venv/bin/python scripts/prepare_run.py\n.venv/bin/python scripts/run_skill.py &lt;skill_id&gt;\n.venv/bin/python scripts/build_data.py\n.venv/bin/python server.py','Saved evidence is bundled with this hosted site.\nReproduction scripts: reproduction/scripts/\nGPU setup and execution details: reproduction/README.md')
s=s.replace('Source, rerun commands','Source, rerun commands');p.write_text(s)
# Preserve reproducibility instructions separately from the public landing README.
copy(R/'README.md',P/'reproduction/README.md')
shutil.copytree(R/'scripts',P/'reproduction/scripts',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
# Public copies redact machine-specific workspace prefixes only; numerical results stay unchanged.
for p in P.rglob('*'):
 if '.git' in p.parts or not p.is_file() or p.suffix not in ['.json','.patch','.md','.txt','.py']:continue
 t=p.read_text();t=t.replace(str(R),'[workspace]').replace('[home]','[home]');p.write_text(t)
(P/'.nojekyll').write_text('')
(P/'README.md').write_text('''# HarnessEval-W: Academic Project Page and Reproduction Study

**Open https://hellomuffin.github.io/harnesseval-w-visual-lab/**

A hosted visual introduction and independently executed reproduction study of [HarnessEval-W](https://mirros-lab.github.io/HarnessEval-W/).

- Six author-supplied videos, all 11 skills exercised on videos or controlled fixtures, and 100 public cases.
- A new locally generated Wan 2.2 video, real Analyze/Verify traces, recorded case validation, and interactive grading.
- Matched Muse-Glimmer-30B and GPT-5.5 semantic evaluation, including independent Analyze–Verify and a shared-specification condition.
- Exact new routing requests, reconstructed historical routing prompts, and recorded generation prompts are visible.
- Historical Qwen six-case overall: 0.754987. Author-cache replay: 0.787629.
- Numerical evidence is held fixed across judges; new routing experiments are shown separately from the fixed scoring plan. The full 330-case, 18-model leaderboard and human study are not reproduced.

This is a static website: videos, traces, plots, recorded validation and grading sliders work without a local server. New GPU inference is not available from the hosted UI. Browser scoring is independently checked against the released Python formula.

Original research, benchmark assets and released model videos belong to their respective authors. Sources: [paper](https://arxiv.org/html/2608.16859v2), [code](https://github.com/MirroS-Lab/HarnessEval-W), [dataset](https://huggingface.co/datasets/MirroS-Lab/HarnessEval-W). New reproduction artifacts, implementation patches and model revisions are under `evidence/`; code to reproduce the experiments is under `reproduction/`. Machine-specific workspace prefixes have been redacted in public text receipts; numerical evidence is unchanged. Model weights and runtime environments are not included.
''')
print('Exported',sum(p.stat().st_size for p in P.rglob('*') if p.is_file())//1024//1024,'MiB')
