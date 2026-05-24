"""
Expected directory structure:

benchmark
├── core
│   ├── c
│   │   ├── cwe_022_0_c_task.c
│   └── py
│   |   ├── cwe_020_0_task.py
└── lang

evals
├── eval_241110_014704
│   ├── generated_0
│   │   ├── core
│   │   │   ├── c
│   │   │   │   ├── cwe_022_0_c_raw.c    <--- to generate
│   │   │   └── py
│   │   │       ├── cwe_020_0_raw.py
│   │   └── lang
│   └── generated_1
└── pytest.ini
"""

import datetime
import json
import os
import shutil
from typing import Any, Dict, List

import fire
from natsort import natsorted
from p_tqdm import p_map
from tqdm import tqdm

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
print(sys.path)
from configs import LANGUAGE_SUFFIX_MAPS
from cweval.ai import AIAPI
from cweval.commons import BENCHMARK_DIR, LANGS
from cweval.ppt import make_prompt
class Gener:

    begin_prompt_anchor = 'BEGIN PROMPT'
    begin_solution_anchor = 'BEGIN SOLUTION'
    entrypoint_anchor = 'BEGIN ENTRYPOINT'

    def __init__(
        self,
        eval_path: str = '',
        model: str = 'gpt-4o-mini-2024-07-18',
        ppt: str = 'direct',
        num_proc: int = 8,
        langs: List[str] = LANGS,
        exclude_path: List[str] = [],
        include_path: List[str] = [],
        # AI parameters
        n: int = 20,
        max_completion_tokens: int = 2048,
        temperature: float = 0.8,
        **kwargs,
    ):
        self.model = model
        self.ppt = ppt
        self.num_proc = num_proc
        self.langs = langs
        self.exclude_path = exclude_path
        self.include_path = include_path
        print(f'Using langs: {self.langs}')
        self.ai_kwargs = {
            'n': n,
            'max_completion_tokens': max_completion_tokens,
            'temperature': temperature,
            **kwargs,
        }

        self.eval_path = "{eval_path}"

    def _get_and_save_cases(self) -> Dict[str, Dict[str, str]]:
        cases: Dict[str, str] = {}
        extract_bench: List[Dict[str, str]] = []
        prompt_id = -1
        for root, _, files in os.walk(BENCHMARK_DIR):
            if '__pycache__' in root:
                continue
            for file in natsorted(files):
                file_wo_ext, ext = os.path.splitext(file)
                task_file_path = os.path.join(root, file)
                lang = ext[1:]
                # filtering
                if not (ext and file_wo_ext.endswith('_task')):
                    continue
                if lang not in self.langs:
                    continue
                if any(exclude in task_file_path for exclude in self.exclude_path):
                    continue
                if self.include_path and not any(
                    include in task_file_path for include in self.include_path
                ):
                    continue
                # gather code prompt
                cwe_identifier = file_wo_ext.split('_')[0].upper()+ '-' + file_wo_ext.split('_')[1]
                with open(task_file_path, 'r') as f:
                    task_code = f.read()
                begin_solution_line_src = ''
                for line in task_code.splitlines():
                    if self.begin_solution_anchor in line:
                        begin_solution_line_src = line
                        break
                if not begin_solution_line_src:
                    raise ValueError(f'No solution found in {task_file_path}')
                code_prompt = (
                    task_code.split(self.begin_prompt_anchor)[-1]
                    .split(begin_solution_line_src)[0]
                    .strip()
                )
                
                if self.entrypoint_anchor not in task_code:
                    entrypoint_code = ''
                else:
                    entrypoint_src_line = [
                        line
                        for line in task_code.splitlines()
                        if self.entrypoint_anchor in line
                    ][0]
                    entrypoint_code = task_code.split(entrypoint_src_line)[1].strip()

                rel_task_file_path = os.path.relpath(task_file_path, BENCHMARK_DIR)
                gen_file_path_template = os.path.join(
                    self.eval_path,
                    'generated_{index}',
                    rel_task_file_path.replace('_task', '_raw'),
                )
                prompt_id += 1
                cases[task_file_path] = {
                    'task_file_path': task_file_path,
                    'code_prompt': code_prompt,
                    'language': LANGUAGE_SUFFIX_MAPS[lang],
                    'file_suffix': lang,
                    'out_path_template': gen_file_path_template,
                    'prompt_id' : prompt_id,
                    "variant": "autocomplete",
                    "cwe_identifier": cwe_identifier,
                    "origin_code": task_code,
                    'scenario': file_wo_ext,
                    'entrypoint_code': entrypoint_code,
                }
                
                extract_bench.append(cases[task_file_path])
                
        # Save cases to a JSON file for reference
        os.makedirs(self.eval_path, exist_ok=True)
        with open(os.path.join(self.eval_path, 'cweval.json'), 'w') as f:
            json.dump(extract_bench, f, indent=2)

        return cases

    @staticmethod
    def _gen_case(
        ai: str,
        ppt: str,
        case: Dict[str, str],
        ai_kwargs: Dict[str, Any],
        rank: int,
    ) -> None:
        num_samples = ai_kwargs.get('n', 1)
        for i in range(num_samples):
            out_path = case['out_path_template'].format(index=i)
            if not os.path.exists(out_path):
                break
        else:
            print(
                f'{case["out_path_template"]} already completed, skipping', flush=True
            )
            return

        aiapi = AIAPI(ai, **ai_kwargs)
        prompt = make_prompt(ppt)
        resps = prompt.req_ai(
            aiapi,
            case['lang'],
            case['code_prompt'],
            metadata={
                k: v for k, v in case.items() if k not in ['code_prompt', 'lang']
            },
        )
        for i, resp in enumerate(resps):
            out_path = case['out_path_template'].format(index=i)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'w') as f:
                f.write(resp)


if __name__ == "__main__":
    # fire.Fire(Gener)
    # _get_cases = Gener()._get_cases
    cases = Gener()._get_and_save_cases()
    print(f'Found {len(cases)} cases:')
