#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
export CUDA_HOME="$PROJECT_DIR/.cuda"
export PATH="$CUDA_HOME/bin:$PATH"
export OMP_NUM_THREADS=4
export VLLM_USE_FLASHINFER_SAMPLER=0
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0,1}
exec "$PROJECT_DIR/.venv-muse/bin/vllm" serve "$PROJECT_DIR/weights/muse-glimmer" --served-model-name meta-models/Muse-Glimmer-30B --host 127.0.0.1 --port 8001 --tensor-parallel-size 2 --max-model-len 24576 --max-num-seqs 4 --gpu-memory-utilization 0.90 --limit-mm-per-prompt '{"image":14}' --reasoning-parser muse_glimmer --enforce-eager
