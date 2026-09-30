from pathlib import Path
import json,subprocess,datetime
R=Path(__file__).resolve().parents[1];A=R/'artifacts';U=R/'upstream'
def read(p):return json.loads(p.read_text()) if p.exists() else None
rows=[]
for p in (A/'fresh/cache/run_audits').glob('**/*.json'):
 d=read(p)
 for row in d.get('outcomes',[]):
  rows.append({k:row.get(k) for k in ['case_id','skill_id','skill_status','status','score','cache_hit','error']})
report={'scope':{'paper_cases':330,'public_cases_downloaded':100,'fresh_evaluation_videos':6,'evaluated_generator':'author-supplied Seedance 2.0 Standard rollouts','judge':'local Qwen3-VL-8B-Instruct; substitute for GPT-5.5','original_world_model_generation_reproduced':False,'human_alignment_reproduced':False},'hardware':read(A/'hardware.json'),'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'upstream_commit':subprocess.check_output(['git','-C',str(U),'rev-parse','HEAD'],text=True).strip(),'fresh_tasks':rows,'fresh_score_report':read(A/'fresh/evaluation/summary.json'),'completion_audit':read(A/'fresh/VERIFY.json'),'author_cache_replay':read(A/'replay/summary.json'),'baseline_protocol_comparison':read(A/'baseline/results.json'),'local_generation':read(A/'construction/generation.json'),'controls':read(A/'controls/results.json'),'repeatability':read(A/'repeats/results.json'),'construction':read(A/'construction/result.json'),'case_audit_wording_check':read(A/'case-audit-check.json'),'formula_checks':read(A/'formula-checks.json'),'weights_audit':read(A/'weights-audit.json'),'ui_checks':read(A/'ui-check.json'),'runtime_adaptation_check':read(A/'patch-equivalence.json'),'vision_chunk_check':read(A/'vision-equivalence.json'),'sparse_experts_check':read(A/'experts-equivalence.json'),'known_gaps':[
'Full 330-case x 18-model experiment and 5,000 human pairwise labels are not available in this checkout; population correlation, ranking, and WBench comparison claims are not reproduced.',
'The semantic implementation has one Analyze call and one eight-question Verify call, rather than independent per-question verifier sub-agents.',
'Physical observation code returns PAVRM raw/5 only; paper Appendix C describes a visual + causal mean.',
'Paper Appendix C gives mean/worst return-pair weights 0.5/0.5; released code uses 0.7/0.3 and an additional non-static gate.',
'Wind-flag case selects physical_law_validator but has no registered engine: not_applicable is not a numerical success.',
'Case construction is a reconstruction using a new imagegen initial image and local VLM planning/validation; the full authors\' construction pipeline is absent.',
'Future recursive skill acquisition and self-improvement are future work, not implemented contributions.'
]}
(A/'report.json').write_text(json.dumps(report,indent=2))
for name,path in [('upstream',U),('HPSv3',R/'dependencies/HPSv3'),('megasam',R/'dependencies/mega-sam'),('megasam-base',R/'dependencies/mega-sam/base'),('lietorch',R/'dependencies/mega-sam/base/thirdparty/lietorch')]:
 d=subprocess.check_output(['git','-C',str(path),'diff'],text=True);(A/(name+'.patch')).write_text(d)
for env in ['.venv','.hpsenv']:
 r=subprocess.run([str(R/env/'bin/pip'),'freeze'],capture_output=True,text=True);(A/(env.strip('.')+'-freeze.txt')).write_text(r.stdout)
print('Report written;',len(rows),'fresh task records')

import shutil
shutil.copyfile(R/'research/xformers_nystrom.py',A/'legacy_nystrom.py')
