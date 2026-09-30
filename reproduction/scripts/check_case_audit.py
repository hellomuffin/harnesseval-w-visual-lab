"""Exercise released lexical audit on concise vs full authored change descriptions."""
from pathlib import Path
import json,copy
from harnesseval.skills.skill_intentional_change_vlm import canonical_spec,case_audit,result_from_judgment
R=Path(__file__).resolve().parents[1];p=R/'artifacts/construction'
case=json.loads((p/'manifest.json').read_text())['cases'][0]
expected=json.loads((p/'evaluation/skills/intentional_change/analyze_agent/local_constructed_red_book.json').read_text())['expected_spec']
verbose=copy.deepcopy(expected);verbose['intended_change']=case['interaction']['action']['text']+' '+' '.join(case['non_model_facing']['expected_outcome'])
rows=[{'label':'Concise intended change: open (actual Analyze output)','expected_spec':expected,'audit':case_audit(canonical_spec(case),expected)},{'label':'Full authored intended-change instruction','expected_spec':verbose,'audit':case_audit(canonical_spec(case),verbose)}]
judgment=json.loads((p/'evaluation/skills/intentional_change/verify_agent/artifacts/harness_video/local_constructed_red_book.json').read_text())['judgment']
for row in rows:row['recomputed_result']=result_from_judgment(judgment,canonical_spec(case),row['expected_spec'])
assert rows[0]['recomputed_result']['score']==rows[1]['recomputed_result']['score']==1.0
(R/'artifacts/case-audit-check.json').write_text(json.dumps({'method':'Actual released case_audit function; only intended_change description changes; all anchors and eight video judgments stay fixed. No VLM calls or fabricated judgments.','finding':'This diagnostic is word-overlap based and sensitive to wording; its warning is not an independent visual failure judgment. It does not alter the numeric grade.','rows':rows},indent=2))
print([(x['label'],x['audit']) for x in rows])
