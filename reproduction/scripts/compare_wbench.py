"""Official WBench rubric+aggregation; same local judge and Harness sampled frames.
This is a protocol ablation on three clips, not the original human study.
"""
from pathlib import Path
import sys,json,subprocess,datetime
from openai import OpenAI
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'baselines/WBench'));sys.path.insert(0,str(R/'upstream/src'))
from src.metrics.interaction.vlm_interaction import generate_event_edit_questions,_execute_binary_tasks
from harnesseval.skills.skill_intentional_change_vlm import _sample_video,_jpeg_data_url_from_rgb
out=R/'artifacts/baseline';out.mkdir(exist_ok=True)
api=OpenAI(base_url='http://127.0.0.1:8000/v1',api_key='local',timeout=600)
class Client:
 def __init__(self):self.calls=[]
 def ask(self,question,images,max_tokens,system_prompt):
  messages=[{'role':'system','content':system_prompt},{'role':'user','content':[{'type':'text','text':question}]+[{'type':'image_url','image_url':{'url':_jpeg_data_url_from_rgb(im)}} for im in images]}]
  response=api.chat.completions.create(model='local-judge',messages=messages,max_tokens=max_tokens,temperature=0)
  text=response.choices[0].message.content
  self.calls.append({'question':question,'system_prompt':system_prompt,'response':response.model_dump()});return text
manifest=json.loads((R/'upstream/runs/example/results_example/manifest.json').read_text())
case=next(c for c in manifest['cases'] if c['taxonomy']['probe_family']=='intentional_transition')
action=case['interaction']['action']['text'];rows=[]
for name in ['original','frozen','reversed']:
 frames,sampling=_sample_video(R/'artifacts/controls'/f'{name}.mp4');client=Client()
 tasks=[(1,q['sub_id'],q['question'],q['expected'],frames) for q in generate_event_edit_questions(action)]
 result=_execute_binary_tasks(client,tasks,[(1,action)],1,'event_edit_adherence')
 assert all(q['answer']!='error' for q in result['turn_details'][0]['questions']),result
 rows.append({'name':name,'sampling':sampling,'result':result,'raw_calls':client.calls});print(name,result['score'],flush=True)
 (out/'results.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'upstream_url':'https://github.com/meituan-longcat/WBench','commit':subprocess.check_output(['git','-C',str(R/'baselines/WBench'),'rev-parse','HEAD'],text=True).strip(),'judge':'Qwen3-VL-8B-Instruct','scope':'Official WBench five-question event-edit rubric and aggregation; frame sampling adapted to HarnessEval 12 frames at 512px. Same judge and clips, different rubric. Harness additionally uses an initial image in Analyze and reference specification; not a controlled architecture-only ablation or human accuracy test.','rows':rows},indent=2))
