import pandas as pd
from pathlib import Path
from typing import Any, List
from collections import OrderedDict
import re, json, os
def _extract_related_ids(cell: Any) -> List[int]:
    if pd.isna(cell):
        return []
    return [int(x) for x in re.findall(r"CWE ID:(\d+)", str(cell))]

def load_cwe_table(csv_path: Path ) -> pd.DataFrame:
    cols = [
        "CWE-ID",
        "Name",
        "Related Weaknesses",
        "Detection Methods",
        "Potential Mitigations",
        "Description",
        "Extended Description",
    ]
    df = pd.read_csv(csv_path, header=0)
    df = df[cols].copy()
    df["Related Weaknesses"] = df["Related Weaknesses"].apply(_extract_related_ids)
    return df

def load_cwe_tree(path: Path ) -> List[OrderedDict]:
    with path.open("r", encoding="utf-8") as f:
        return [OrderedDict(json.loads(line)) for line in f]



def get_exp_path(args, strategy, output_root_path='experiments', pj_name=''):
    strategy_id = strategy.value  + args.suffix 
    if args.output_path is None:
        if args.ours :
            if args.eval_type == 'none':
                output_dir = '{}/{}_{}_{}'.format(output_root_path, pj_name, args.task, args.model)
            else:
                output_dir = '{}/{}_{}_{}_{}'.format(output_root_path, pj_name, args.task, args.eval_type, args.model)
        elif args.eval_type == 'none':
            if pj_name != '':
                output_dir = '{}/{}_{}_{}'.format(output_root_path, pj_name, args.task, args.model)
                # output_dir = '{}/{}'.format(output_root_path, pj_name) #, args.task, args.model)
            else:
                output_dir = '{}/{}_{}'.format(output_root_path, args.task, args.model)
        else:
            if pj_name != '':
                output_dir = '{}/{}_{}_{}_{}'.format(output_root_path, pj_name, args.task, args.eval_type, args.model)
            else:
                output_dir = '{}/{}_{}_{}'.format(output_root_path, args.task, args.eval_type, args.model)
        output_path = os.path.join(output_dir, strategy_id)
        if args.init:
            json_file_path = os.path.join(output_path, 'response_init.json')
        else:
            json_file_path = os.path.join(output_path, 'response.json')
    else:
        json_file_path =  args.output_path
        output_path = '/'.join(args.output_path.split('/')[:-1])
        output_dir = os.path.dirname(output_path)
    
    return output_dir, output_path, strategy_id, json_file_path


def previously_processed(output_res_file, args):
    previous = []
    if args.compile_only or not os.path.exists(output_res_file):
        return previous, [], ""
    with open(output_res_file, 'r') as f:
        previous = [OrderedDict(json.loads(line)) for line in f if 'prompt_id' in json.loads(line) ]
    return previous, [p['prompt_id'] for p in previous], ''.join(open(output_res_file).readlines())
