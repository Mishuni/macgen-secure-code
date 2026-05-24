import json
import os
import shutil
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.macgen.utils.parse_arguments import parser
from src.macgen.utils.util import get_exp_path
from src.macgen.utils.code_parse import extract_code
from src.macgen.config import strategy_mapping, AgentStrategy

args = parser.parse_args()
# python extract_res_for_cweval.py --pj_name test --model gpt4o-mini --output_path test.json
if __name__ == "__main__":
    BASE_DIR = "experiments"
    PJ_NAME = args.pj_name or f"{args.task}_{args.model}_macgen"
    MODEL_SLUG = args.model.replace("/", "-").replace(":", "-")

    if not args.ours:
        # ===== Standard experiment flow =====
        if args.output_path:
            ## codeGuarder
            json_file_path = args.output_path
            EXP_DIR = os.path.dirname(os.path.dirname(json_file_path))

        else:
            strategy: AgentStrategy = getattr(AgentStrategy, strategy_mapping[args.strategy])
            _, EXP_DIR, _, json_file_path = get_exp_path(args, strategy, BASE_DIR, pj_name=PJ_NAME)
        print(f"Experiment directory: {EXP_DIR}")

        # Keep evaluation dir simple (e.g., pj_name only)
        EVAL_DIR = PJ_NAME
        if args.init:
            EVAL_DIR += "_init"

    else:
        # ===== Ours / Custom experiment =====
        if 'icsme' in args.suffix:
            DIR_NAME = f"icsme_{MODEL_SLUG}_cweval"
        else:
            DIR_NAME = '' #f"cweval_{MODEL_SLUG}_macgen" #if args.init else f"ours_{MODEL_SLUG}_cweval"

        EXP_DIR = f"{PJ_NAME}"
        print(f"Experiment directory: {EXP_DIR}")
        CWE_LIMIT = args.cwe_limit if args.cwe_limit else 3

        # Construct file paths using consistent model_slug and pj_name
        if args.init:
            json_file_path = f"{BASE_DIR}/{EXP_DIR}/_{MODEL_SLUG}_cweval_{CWE_LIMIT}.json"
        else:
            json_file_path = f"{BASE_DIR}/{EXP_DIR}/_phase2_{MODEL_SLUG}_cweval_{CWE_LIMIT}.json"

        EVAL_DIR = PJ_NAME
        if args.init:
            EVAL_DIR += "_init"

    print(f"Evaluation directory: {EVAL_DIR}")
    print(f"Response JSON file path: {json_file_path}")

    # ===== Load Response JSON =====
    with open(json_file_path, 'r') as file:
        response_data = json.load(file)
    if response_data and response_data[0].get('prompt_id') is not None:
        response_data.sort(key=lambda x: x['prompt_id'])

    # ===== Eval Output Directory =====
    TEST_BENCH_ROOT_PATH = "./eval_test_based/cweval"
    eval_path = f"{TEST_BENCH_ROOT_PATH}/evals/{EVAL_DIR}"
    eval_in_doc = f"evals/{EVAL_DIR}"

    print(f"Eval path: {eval_path}")
    print(f"Number of responses: {len(response_data)}")

    # ===== Ensure Directory =====
    if not os.path.exists(eval_path):
        os.makedirs(eval_path)
    else:
        if not args.override:
            print(f"Eval path {eval_path} already exists. Skipping creation.")
            exit(1)
        else:
            shutil.rmtree(eval_path)
            os.makedirs(eval_path)

    # ===== Write each code snippet =====
    for i, info in enumerate(response_data):
        out_path_template = info.get('out_path_template')
        if not out_path_template:
            continue
        out_path = out_path_template.format(eval_path=eval_path, index=0)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        response = info.get('response', "")
        code = extract_code(
            response,
            lr=info.get('language', 'python'),
            task='cweval',
            file_context=None,
            func_context=None
        )
        # print(out_path)
        # print(code)
        # print()

        with open(out_path, 'w') as f:
            f.write(code)

    print(f'python cweval/evaluate.py pipeline --eval_path {eval_in_doc} --num_proc 20 --docker False')
