from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]/'dependencies';root.mkdir(exist_ok=True)
repos=[('RAFT','princeton-vl/RAFT','2888e15a51fa41140771d3f498ed8023cff098d1'),('AMT','MCG-NKU/AMT','70f988fbfc0d3d458beba1ee49caf876e57968fe'),('HPSv3','MizzenAI/HPSv3','bd0c5fcb5f587617b0169c07222ab78d01e2f3c2'),('mega-sam','mega-sam/mega-sam','a27b4e633c5cc0828a62ed943ef9f6505705fd3f'),('Depth-Anything','LiheYoung/Depth-Anything','1d03336771fe09c5398ffdd211441e33941a97dc'),('UniDepth','lpiccinelli-eth/UniDepth','8d8cfe4c7ee15297099983607febf0d4f32eb3d6'),('dinov2','facebookresearch/dinov2','7764ea0f912e53c92e82eb78a2a1631e92725fc8')]
def run(t):
 name,repo,rev=t;p=root/name
 if not p.exists():subprocess.run(['git','clone','--filter=blob:none','--no-checkout','https://github.com/'+repo+'.git',str(p)],check=True)
 subprocess.run(['git','fetch','--depth','1','origin',rev],cwd=p,check=True)
 subprocess.run(['git','checkout','--detach','FETCH_HEAD'],cwd=p,check=True)
 if name=='mega-sam':subprocess.run(['git','submodule','update','--init','--recursive','--depth','1'],cwd=p,check=True)
 print('DONE',name,flush=True)
with ThreadPoolExecutor(4) as pool:list(pool.map(run,repos))
