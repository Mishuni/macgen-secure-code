#!/bin/bash
set -euo pipefail

eval "$(conda shell.bash hook)"
conda activate cweval
# export PYTHONPATH=$PYTHONPATH:$(pwd)
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$(pwd)"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
export NODE_PATH=$(npm root -g)
export C_INCLUDE_PATH="$CONDA_PREFIX/include"
export LIBRARY_PATH="$CONDA_PREFIX/lib"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib"
export PATH=$PATH:/usr/local/go/bin
export PATH=$PATH:~/go/bin

EVAL_ROOT="evals"

# 🔎 generated_0 
mapfile -t EVAL_DIRS < <(find "$EVAL_ROOT" -type d -name "generated_0" -exec dirname {} \; | sort -u)

if [ ${#EVAL_DIRS[@]} -eq 0 ]; then
  echo "No evaluation directories found under '$EVAL_ROOT' that contain 'generated_0'."
  exit 0
fi

for EVAL_PATH in "${EVAL_DIRS[@]}"; do
    LOG_PATH="$EVAL_PATH/log.txt"
    # pass_at_1.json : skip
    RESULT_PATH="$EVAL_PATH/pass_at_1.json"

    if [ -f "$RESULT_PATH" ]; then
        echo "⏭️  Skipping $EVAL_PATH (pass_at_1.json exists)"
        continue
    fi
    echo "🚀 Running evaluation for: $EVAL_PATH"
    python cweval/evaluate.py pipeline \
        --eval_path "$EVAL_PATH" \
        --num_proc 8 \
        --docker False > "$LOG_PATH" 2>&1

    # 🔧 cool down
    sleep 2
done
