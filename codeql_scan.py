

import sys
import json
import shutil
import pandas as pd
import os, time
from collections import OrderedDict
import pprint

from concurrent.futures import ProcessPoolExecutor, as_completed
import subprocess
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.macgen.utils.code_parse import codeql_create_db, eval_setting, make_suffix
from src.macgen.utils.parse_arguments import parser
from src.macgen.utils.util  import get_exp_path, previously_processed
from src.macgen.config import strategy_mapping, QL_LANGUAGES, LANGUAGE_MAPS, AgentStrategy, CODEQL_ROOT_DIR

# from configs import *
import time, re

SAFE_CODER_FILES_DIRECTORY = './safe_coder_eval'
# CODEQL_ROOT_DIR = './codeql/codeql-repo/'
QUERIES={}
QUERIES_STATISTICS = {}

args = parser.parse_args()

## TODO : depending on language, we can use different codeql queries
for lang in QL_LANGUAGES:
    root_dir = os.path.join(CODEQL_ROOT_DIR, lang, 'ql', 'integration-tests', 'query-suite') if not lang == 'java' \
        else os.path.join(CODEQL_ROOT_DIR, lang, 'ql', 'integration-tests', lang, 'query-suite')
    if not os.path.exists(root_dir):
        print(f"Directory {root_dir} does not exist.")
        continue
    root_dir = os.path.join(root_dir, f'{lang}-security-extended.qls.expected')
    if not os.path.exists(root_dir):
        print(f"File {root_dir} does not exist.")
        continue

    with open(root_dir, 'r') as file:
        content = file.read()
        lines = content.splitlines()
    lines = ['/'.join(line.split('/')[2:]) for line in lines if 'CWE' in line or 'cwe' in line]

    lang_root_dir = os.path.join(CODEQL_ROOT_DIR, lang)
    QUERIES[lang] = {}
    total_queries = 0
    for line in lines:
        elements = line.split('/')
        for e in elements:
            if e.startswith('CWE-') or e.startswith('cwe'):
                cwe = e.upper()
                break
        if cwe not in QUERIES[lang]:
            QUERIES[lang][cwe] = [os.path.join(lang_root_dir, line)]
        else:
            QUERIES[lang][cwe].append(os.path.join(lang_root_dir, line))
        total_queries += 1
        # break
    QUERIES_STATISTICS[lang] = { 'total_ql': total_queries, 'total_cwes': len(list(QUERIES[lang].keys()))} 

def pick_workers_and_threads(pending_tasks: int):
    cpu = os.cpu_count() or 1  

    if pending_tasks <= 0:
        return 0, 1, cpu  
    workers = min(pending_tasks, max(1, cpu // 2))
    
    codeql_threads = max(1, cpu // workers)
    total_threads = workers * codeql_threads
    hard_cap = max(cpu, 1) * 2
    if total_threads > hard_cap:
        codeql_threads = max(1, hard_cap // workers)
        total_threads = workers * codeql_threads

    return workers, codeql_threads, cpu


def _resolve_query_files(ql_suite_or_queries):
    if isinstance(ql_suite_or_queries, (list, tuple)):
        return list(ql_suite_or_queries)
    if isinstance(ql_suite_or_queries, str):
        try:
            proc = subprocess.run(
                f'./codeql/codeql resolve queries --format=json "{ql_suite_or_queries}"',
                shell=True, capture_output=True, text=True, check=True
            )
            data = json.loads(proc.stdout)
            files = []
            if isinstance(data, list):
                for item in data:
                    f = item.get('file') or item.get('query') or item.get('path')
                    if f: files.append(f)
            elif isinstance(data, dict):
                for item in data.get('queries', []):
                    f = item.get('file') or item.get('query') or item.get('path')
                    if f: files.append(f)
            return files
        except Exception:
            return []
    return []


def _parse_ql_metadata(ql_file):
    try:
        with open(ql_file, 'r', encoding='utf-8', errors='ignore') as f:
            head = f.read(8192)  
        id_m = re.search(r'@id\s+([^\s*]+)', head)
        name_m = re.search(r'@name\s+(.+)', head)
        tags_m = re.findall(r'@tags?\s+([^\n*]+)', head)

        rid = id_m.group(1).strip() if id_m else None
        name = name_m.group(1).strip() if name_m else None
        tag_str = tags_m[-1] if tags_m else ''
        tag_list = [t.strip() for t in re.split(r'[,\s]+', tag_str) if t.strip()]
        cwes = []
        for t in tag_list:
            if 'cwe' in t.lower():
                m = re.search(r'cwe[-_/ ]?(\d+)', t, flags=re.I)
                if m:
                    cwes.append(f'CWE-{m.group(1)}')
        cwes = list(dict.fromkeys(cwes)) 
        return rid, name, cwes
    except Exception:
        return None, None, []


def _augment_csv_with_query_info(csv_out, ql_suite_or_queries):
    if not os.path.isfile(csv_out):
        return

    ql_files = _resolve_query_files(ql_suite_or_queries)
    if not ql_files and isinstance(ql_suite_or_queries, (list, tuple)):
        ql_files = list(ql_suite_or_queries)
    meta_by_name = {}

    for q in ql_files:
        _, name, cwes = _parse_ql_metadata(q)
        if name:
            meta_by_name[name] = {'ql_file': q, 'name': name, 'cwes': cwes}
        
    try:
        df = pd.read_csv(csv_out, header=None)
    except pd.errors.EmptyDataError:
        try:
            os.remove(csv_out)
        except Exception:
            pass
        return
    except Exception:
        try:
            os.remove(csv_out)
        except Exception:
            pass
        return
    # Print all values from the first column of each row in df
    for val in df.iloc[:, 0]:
        if val in meta_by_name:
            ql_file = str(meta_by_name.get(val, {})['ql_file'])
            cwe_name = '_'.join(ql_file.split('/')[-2:]).replace('.ql', '')
            df.loc[df.iloc[:, 0] == val, 'ql_file'] = ql_file
            df.loc[df.iloc[:, 0] == val, 'cwe'] = cwe_name
    df.to_csv(csv_out, index=False)

def run_codeql_bundled(args, info, exp_dir, ql_suite_or_queries, codeql_threads):
    prompt_id = info.get('prompt_id')
    statistic = OrderedDict()
    cwe = info.get('cwe', info.get('cwe_identifier', None))
    statistic['prompt_id'] = prompt_id
    statistic['cwe'] = cwe
    statistic['scenario'] = info.get('scenario', info.get('id', ''))
    statistic['language'] = info['language']

    ql_lang = LANGUAGE_MAPS.get(info['language'].lower(), None)
    if not ql_lang or ql_lang not in QL_LANGUAGES:
        statistic['vul_cwes'] = ["not supported"]
        return statistic

    valid, _, valid_srcs, invalid_srcs, feedbacks, out_dir = eval_setting(args, info.get('response', info.get('final_prediction')), info, output_dir=exp_dir)
    chosen = valid_srcs if len(valid_srcs) > 0 else invalid_srcs 
    dir_path = os.path.dirname(chosen[0])
    if args.compile_only:
        statistic['valid'] = valid
        if statistic['valid'] == 0:
            statistic['err_msg'] = feedbacks
        return statistic
    
    bundle_root = os.path.dirname(dir_path)
    csv_out = os.path.join(bundle_root, "bundle_codeql.csv")
    db_dir = os.path.join(bundle_root, "codeql_db")
    if len(valid_srcs) > 0 :
        file_suffix = info['file_suffix'] if info else ''
        src_dir = os.path.dirname(valid_srcs[0])
        codeql_create_db(info, src_dir, db_dir)
        _analyze_bundled(db_dir, csv_out, ql_suite_or_queries, codeql_threads=codeql_threads)

    results = pd.read_csv(csv_out, header=0) if os.path.isfile(csv_out) else pd.DataFrame()
    chck = len(results)
    checked_cwes = set(results['cwe'].dropna().unique().tolist()) if not results.empty else set()
    
    statistic['valid'] = valid
    statistic['vul_len'] = chck
    statistic['vul_len_of_cwes'] = len(list(checked_cwes))
    statistic['vul_cwes'] = list(checked_cwes)
    if os.path.exists(db_dir):
        try:
            shutil.rmtree(db_dir)
        except Exception as e:
            pass
    return statistic


def _analyze_bundled(db_dir: str, csv_out: str, ql_suite_or_queries, codeql_threads: int = 0):
    # finalize
    subprocess.run(f'./codeql/codeql database finalize "{db_dir}"',
                   shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if isinstance(ql_suite_or_queries, str) and ql_suite_or_queries.endswith('.qls'):
        query_arg = f'"{ql_suite_or_queries}"'
    elif isinstance(ql_suite_or_queries, (list, tuple)):
        query_arg = " ".join([f'"{q}"' for q in ql_suite_or_queries])
    else:
        raise ValueError("ql_suite_or_queries must be .qls path or list of .ql files")

    threads = 0 if not codeql_threads else int(codeql_threads)
    cmd = (
        f'./codeql/codeql database analyze "{db_dir}" {query_arg} '
        f'--format=csv --output="{csv_out}" --threads=0 '
        f'--additional-packs="{os.path.expanduser("~/.codeql/packages/codeql/")}"'
    )
    subprocess.run(cmd, shell=True, check=False, stdout=subprocess.DEVNULL)
    _augment_csv_with_query_info(csv_out, ql_suite_or_queries)


def _process_one(info, args, EXP_DIR, lang_to_queries, info_exp_dir):
    info = make_suffix(args, info)
    ql_lang = LANGUAGE_MAPS.get(info.get('language', info.get('lang')).lower(), None)
    ql_suite_or_queries = lang_to_queries.get(ql_lang, [])
    os.makedirs(info_exp_dir, exist_ok=True)

    try:
        print(f"[PID {os.getpid()}] Processing prompt_id={info.get('prompt_id')} lang={info.get('language')}")
        return run_codeql_bundled(args, info, info_exp_dir, ql_suite_or_queries, codeql_threads)
    except Exception as e:
        return None


if __name__ == "__main__":
    
    start_time = time.time()
    pprint.pprint(QUERIES_STATISTICS)
    print("Evaluation completed successfully.")
    output_root_path="experiments"
    strategy: AgentStrategy = getattr(AgentStrategy, strategy_mapping[args.strategy])
    _, EXP_DIR, _, json_file_path = get_exp_path(args, strategy, output_root_path, pj_name=args.pj_name)

    with open(f'{json_file_path}', 'r') as file:
        response_data = json.load(file)
    if response_data[0].get('prompt_id', None) is None:
        for i, item in enumerate(response_data):
            item['prompt_id'] = i
    response_data.sort(key=lambda x: x['prompt_id'])

    temp_file_name = (
        'compile_all_res.jsonl' if args.compile_only and not args.init
        else 'compile_all_res_init.jsonl' if args.compile_only    
        else 'sec_codeql_all_res.jsonl' if not args.init
        else 'sec_codeql_all_res_init.jsonl' 
    )

    output_res_file = os.path.join(EXP_DIR, temp_file_name)
    output_root_dir = os.path.join(EXP_DIR, args.eval_type) if not args.init else os.path.join(EXP_DIR, f'{args.eval_type}_init')
    if os.path.exists(output_root_dir):
        shutil.rmtree(output_root_dir)
        print(f"Removed existing directory: {output_root_dir}")
    os.makedirs(output_root_dir, exist_ok=True)

    previous, already_done, original_content = previously_processed(output_res_file, args)
    print(f"Loaded {len(previous)} previous results from {output_res_file}")    
    total_results, total_stat = previous, OrderedDict(total=0, valid=0)
    if not args.compile_only:
        total_stat.update({'vul_len': 0, 'vul_len_of_cwes': 0, 'vul_file_len': 0, 'vul_prompts': []})
    else:
        total_stat['not_valid_prompts'] = []
    total_stat['not_supported'] = 0
    
    lang_to_queries = {}
    for lang in QL_LANGUAGES:
        ql_list = []
        for arr in QUERIES.get(lang, {}).values():
            ql_list.extend(arr)
        lang_to_queries[lang] = ql_list

    pending_infos = []
    for info in response_data:
        info = make_suffix(args, info)  
        if info.get('prompt_id') in already_done:
            print(f"Skipping already processed prompt_id: {info.get('prompt_id')}")
            continue
        pending_infos.append(info)
    
    tasks = len(pending_infos)
    workers, codeql_threads, cpu = pick_workers_and_threads(tasks)
    print(f"{os.cpu_count()} CPU cores detected")
    print(f"Using {workers} workers with {codeql_threads} CodeQL threads each for {len(pending_infos)} pending tasks.")
    
    from concurrent.futures import ProcessPoolExecutor, as_completed
    total_results, total_stat = previous, OrderedDict(total=0, valid=0)
    if not args.compile_only:
        total_stat.update({'vul_len': 0, 'vul_len_of_cwes': 0, 'vul_file_len': 0, 'vul_prompts': []})
    else:
        total_stat['not_valid_prompts'] = []
    total_stat['not_supported'] = 0
    if workers <= 0: print("No tasks to process."); 
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(_process_one, info, args, EXP_DIR, lang_to_queries, output_root_dir)
                    for info in pending_infos]
            for fut in as_completed(futures):
                res = fut.result()
                if res is not None:
                    total_results.append(res)

        total_results.sort(key=lambda x: x.get('prompt_id', float('inf')))
        total_stat['total'] = len(total_results)
        with open(output_res_file, 'w') as f:
            for res in total_results:
                total_stat['valid'] += res.get('valid', 0)
                if len(res.get('vul_cwes',[])) > 0 and res['vul_cwes'][0] == 'not supported':
                    total_stat['not_supported'] += 1
                if not args.compile_only:
                    total_stat['vul_len'] += res['vul_len']
                    total_stat['vul_len_of_cwes'] += res['vul_len_of_cwes']
                    total_stat['vul_file_len'] += 1 if res['vul_len'] > 0 else 0
                    if res['vul_len'] > 0:
                        total_stat['vul_prompts'].append(res['prompt_id'])
                elif res.get('valid', 0) == 0:
                    total_stat['not_valid_prompts'].append(res['prompt_id'])
                f.write(json.dumps(res) + '\n')
            f.write(json.dumps(total_stat) + '\n')

        keep_db = getattr(args, "keep_db", False)
        if not keep_db:
            if os.path.exists(output_root_dir):
                shutil.rmtree(output_root_dir)
        print(f"Total time taken: {(time.time() - start_time)/60:.2f} minutes")
