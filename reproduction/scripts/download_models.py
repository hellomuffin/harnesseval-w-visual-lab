import os,json,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
os.environ['HF_HUB_DISABLE_XET']='1'
from huggingface_hub import snapshot_download,HfApi
root=Path(__file__).resolve().parents[1]
def run(repo,kind,dest,patterns):
    info=HfApi().repo_info(repo,repo_type=kind)
    print('START',repo,info.sha,flush=True)
    snapshot_download(repo,repo_type=kind,revision=info.sha,local_dir=root/dest,allow_patterns=patterns,max_workers=4)
    (root/'artifacts'/('download-'+dest.replace('/','-')+'.json')).write_text(json.dumps({'repo':repo,'revision':info.sha,'path':dest,'patterns':patterns},indent=2))
    print('DONE',repo,flush=True)
with ThreadPoolExecutor(3) as pool:
    jobs=[pool.submit(run,'MirroS-Lab/HarnessEval-W','dataset','public-set',['data/*','README.md']),pool.submit(run,'meituan-longcat/WBench-weights','model','weights',['clip/*','aesthetic/*','pyiqa/*','amt/*','raft/*','HPSv3/*','Qwen2-VL-7B-Instruct/*','qwen3vl-a3b-visual-plausibility/*','megasam/*']),pool.submit(run,'Qwen/Qwen3-VL-8B-Instruct','model','weights/judge',None)]
    for job in jobs: job.result()
