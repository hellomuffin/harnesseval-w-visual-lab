from pathlib import Path
import os,sys,subprocess,re,shutil
R=Path(__file__).resolve().parents[1];base=R/'dependencies/mega-sam/base'
# Restore the exact retired xFormers component expected by embedded UniDepth.
layers=R/'dependencies/mega-sam/UniDepth/unidepth/layers'
shutil.copyfile(R/'research/xformers_nystrom.py',layers/'legacy_nystrom.py')
p=layers/'nystrom_attention.py';s=p.read_text()
if 'from .legacy_nystrom import NystromAttention' not in s:
 s=s.replace('from xformers.components.attention import NystromAttention', 'try:\n    from xformers.components.attention import NystromAttention\nexcept ImportError:\n    from .legacy_nystrom import NystromAttention')
 p.write_text(s)
hub=R/'dependencies/mega-sam/torchhub';hub.mkdir(exist_ok=True)
link=hub/'facebookresearch_dinov2_main'
if not link.exists():link.symlink_to(R/'dependencies/dinov2',target_is_directory=True)
for d in [base/'src',base/'thirdparty/lietorch/lietorch/src']:
 for p in d.glob('*'):
  if p.suffix not in ['.cu','.cpp']:continue
  s=p.read_text();s='\n'.join(line.replace('.type()', '.scalar_type()') if 'DISPATCH' in line else line for line in s.split('\n'));p.write_text(s)
p=base/'setup.py';s=p.read_text();s=re.sub(r"\s*'-gencode=arch=compute_(70|75|80),code=sm_\1',",'',s);s=s.replace("'-gencode=arch=compute_86,code=sm_86'","'-gencode=arch=compute_89,code=sm_89'");p.write_text(s)
# Use headers already installed with the host's matching CUDA 12.8 PyTorch wheels.
env=dict(os.environ,CUDA_HOME=str(R/'.cuda'),TORCH_CUDA_ARCH_LIST='8.9',MAX_JOBS='4')
headers=list(Path('/opt/conda/lib/python3.12/site-packages/nvidia').glob('*/include'))
env['CPATH']=':'.join(map(str,headers))+':'+str(R/'.cuda/targets/x86_64-linux/include')
res=subprocess.run([sys.executable,'setup.py','build_ext','--inplace'],cwd=base,env=env)
if res.returncode==0:
 site=next((R/'.venv/lib').glob('python*/site-packages'))
 (site/'megasam_local.pth').write_text(str(base)+'\n'+str(base/'thirdparty/lietorch')+'\n')
sys.exit(res.returncode)
