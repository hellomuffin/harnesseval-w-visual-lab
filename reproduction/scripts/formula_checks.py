"""Independent paper Appendix C formula checks against released Python."""
from pathlib import Path
import sys,json,random
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'upstream/src'))
from harnesseval.skills import skill_intentional_change_vlm as ic,skill_physical_response_vlm as pr,skill_offscreen_evolution as oe
mods={'intentional':ic,'physical':pr,'offscreen':oe}
def reference(name,q):
 a,b,c,d,e,f,g,h=q
 if name=='intentional':return a*h*(.3*(.4*b+.6*c)+.25*e+.2*d+.25*(.6*f+.4*g))
 if name=='physical':return (a+b)/2*h*(.55*(.45*c+.35*d+.2*e)+.25*(.55*f+.45*g)+.2*e)
 return (a+b+c)/3*(e+h)/2*(.35*d+.65*(.4*f+.6*g))
rng=random.Random(330);rows=[]
for name,module in mods.items():
 errors=[]
 for i in range(1000):
  q=[rng.choice([0,.25,.5,.75,1]) for _ in range(8)]
  normalized=module.normalize_q_scores({'q_scores':{'Q'+str(j+1):v for j,v in enumerate(q)}})
  actual=module.aggregate_q_scores(normalized)['final_score'];expected=reference(name,q)
  if actual is None or abs(actual-expected)>1e-6:errors.append({'q':q,'actual':actual,'expected':expected})
 rows.append({'skill':name,'vectors':1000,'mismatches':len(errors),'examples':errors[:5]})
print(rows)
(R/'artifacts/formula-checks.json').write_text(json.dumps({'seed':330,'checks':rows,'scope':'Complete 8-question inputs; does not validate the VLM judgments or missing-input behavior.'},indent=2))
assert all(x['mismatches']==0 for x in rows)
