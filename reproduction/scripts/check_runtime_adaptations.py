"""Small equivalence checks for the three disclosed PAVRM runtime adaptations."""
from pathlib import Path
import torch,json,types,os
from transformers.models.qwen3_vl_moe.configuration_qwen3_vl_moe import Qwen3VLMoeVisionConfig,Qwen3VLMoeTextConfig
from transformers.models.qwen3_vl_moe.modeling_qwen3_vl_moe import Qwen3VLMoeVisionPatchEmbed,Qwen3VLMoeVisionModel,Qwen3VLMoeTextExperts
from harnesseval.metrics.physical_plausibility import _linear_patch_embedding,_chunked_vision_forward
R=Path(__file__).resolve().parents[1];torch.set_num_threads(4);torch.manual_seed(42)
config=Qwen3VLMoeVisionConfig(depth=2,hidden_size=32,intermediate_size=64,num_heads=4,patch_size=2,temporal_patch_size=2,spatial_merge_size=2,out_hidden_size=32,num_position_embeddings=16,deepstack_visual_indexes=[0,1]);config._attn_implementation='eager'
with torch.no_grad():
 patch=[]
 for dtype in [torch.float32,torch.bfloat16]:
  model=Qwen3VLMoeVisionPatchEmbed(config).to(dtype);x=torch.randn(32,24,dtype=dtype)
  a=model(x);b=_linear_patch_embedding(model,x);delta=(a-b).abs().max().item();assert torch.allclose(a,b,atol=.01 if dtype==torch.bfloat16 else 1e-5,rtol=.01)
  patch.append({'dtype':str(dtype),'max_absolute_difference':delta,'allclose':True})
 (R/'artifacts/patch-equivalence.json').write_text(json.dumps({'tests':patch,'scope':'Single-patch Conv3d vs linear, toy random weights and inputs; not whole-checkpoint bitwise equivalence.'},indent=2))
 model=Qwen3VLMoeVisionModel(config).eval();x=torch.randn(64,24);grid=torch.tensor([[4,4,4]])
 a,sa=model(x,grid);model._harnesseval_original_forward=model.forward;os.environ['HARNESSEVAL_VISION_CHUNK_T']='2';b,sb=_chunked_vision_forward(model,x,grid)
 differences=[(u-v).abs().max().item() for u,v in zip([a,*sa],[b,*sb])];assert all(torch.allclose(u,v,atol=1e-5,rtol=1e-5) for u,v in zip([a,*sa],[b,*sb]))
 (R/'artifacts/vision-equivalence.json').write_text(json.dumps({'max_absolute_differences':differences,'allclose':True,'test':'FP32 two-layer Qwen3 vision model, same weights and input, 4 temporal groups vs 2+2, including deepstack outputs'},indent=2))
 tests=[]
 for dtype in [torch.float32,torch.bfloat16]:
  c=Qwen3VLMoeTextConfig(hidden_size=32,moe_intermediate_size=16,num_experts=8,num_experts_per_tok=2);m=Qwen3VLMoeTextExperts(c).to(dtype)
  for p in m.parameters():p.normal_(0,.03)
  x=torch.randn(17,32,dtype=dtype);weights=torch.softmax(torch.randn(17,8),-1);indices=weights.topk(2,-1).indices;mask=torch.zeros_like(weights).scatter_(1,indices,1);weights=(weights*mask);weights=(weights/weights.sum(-1,keepdim=True)).to(dtype)
  m.eval();a=m(x,weights,indices);m.train();b=m(x,weights,indices)
  delta=(a-b).abs().max().item();assert torch.allclose(a,b,atol=.001 if dtype==torch.bfloat16 else 1e-6,rtol=.01)
  tests.append({'dtype':str(dtype),'max_absolute_difference':delta,'allclose':True})
 (R/'artifacts/experts-equivalence.json').write_text(json.dumps({'tests':tests,'scope':'Same toy MoE parameters, inputs and routing. No-dropout expert container only; not whole-model equivalence.'},indent=2))
print('All runtime adaptation equivalence checks passed')
