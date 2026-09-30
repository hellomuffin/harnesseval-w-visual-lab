#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-1}
exec /opt/conda/bin/python -m vllm.entrypoints.openai.api_server --model "$PROJECT_DIR/weights/judge" --served-model-name local-judge --host 127.0.0.1 --port 8000 --max-model-len 16384 --gpu-memory-utilization 0.85 --limit-mm-per-prompt '{"image":14}' --enforce-eager
