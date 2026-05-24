import re
import os
import ast
import subprocess
import tempfile
import shutil
import pathlib
from macgen.config import SAFE_CODER_FILES_DIRECTORY, LANGUAGE_SUFFIX_MAPS

def extract_content_in_code_blocks(input: str, keyword=''):
    # Using regular expression to find content between code blocks ```
    if not input:
        return ""
    output = re.findall(r"```{}(.*?)```".format(keyword), input, re.DOTALL)
    if len(output)>0:
        return output[0]
        # return output[-1]
    return input 

def get_cp_args(info):
    info['class_path'] = info.get('class_path', '')
    if info['class_path'] == '':
        cp_args = ''
    else:
        paths = info['class_path'].split(':')
        paths = list(map(lambda p: os.path.realpath(p), paths))
        cp_args = '-cp {}'.format(':'.join(paths))
    return cp_args


def extract_code(input: str, lr='python', task='', file_context=None, func_context=''):
    code = extract_content_in_code_blocks(input).strip()
    if code.lower().startswith(lr.lower() + '\n'):
        code = code[len(lr):]
    elif (lr.lower()=='javascript' or lr.lower()=='js') and code.lower().startswith('jsx\n'):
        code = code[3:]
    elif (lr.lower()=='javascript' or lr.lower()=='js') and code.lower().startswith('javascript\n'):
        code = code[len('javascript\n'):].strip()
    elif (lr.lower()=='javascript' or lr.lower()=='js') and code.lower().startswith('js\n'):
        code = code[len('js\n'):].strip()
    elif code.lower().startswith('python\n'):
        code = code[6:]
    elif code.lower().startswith('cpp\n'):
        code = code[3:]
    if 'autocomplete' in task and file_context is not None:
        if not code.strip().startswith(file_context.strip().split('\n')[0][:6].strip()):
            code = file_context + func_context + code
    if 'cweval' in task and func_context is not None:
        if func_context.strip() in code:
            func_context = func_context.strip().split('\n')[0]
            code = code.replace(func_context.strip(), "")
    if 'cweval' in task and lr.lower() == 'go' and 'package solution' in code:
        code = code.replace('package solution', 'package main', 1)

    if lr.lower() == "json":
        code = code.replace(']"', ']')
        code = code.replace('"[', '[')
        code = code.replace("]'", ']')
        code = code.replace("'[", '[')
    return code 

def check_python_syntax(code: str) -> dict:
    """
    Parses Python code to check for syntax errors.
    """
    try:
        ast.parse(code)
        return { "valid": True }
    except SyntaxError as e:
        return {
            "valid": False,
            "error": {
                "msg": e.msg,
                "lineno": e.lineno,
                "offset": e.offset,
                "text": e.text.strip() if e.text else None
            }
        }

def make_parse_list(codes, info, get_feedback=False):
    output_srcs, non_parsed_srcs = [], []
    feedbacks = []
    for src in codes:
        if not get_feedback:
            # if info['file_suffix'] != 'go' and try_parse(src, info) != 0:
            if try_parse(src, info) != 0:
                non_parsed_srcs.append(src)
            else:
                output_srcs.append(src)
        else:
            compile_success, stdout, stderr = compile_code(src, info, info.get('language', info.get('lang', None)).lower())
            if compile_success:
                output_srcs.append(src)
            else:
                non_parsed_srcs.append(src)
                feedbacks.append({'stdout': stdout, 'stderr': stderr})
    if not get_feedback :
        return output_srcs, non_parsed_srcs
    else:
        return output_srcs, non_parsed_srcs, feedbacks


def compile_code(code, info, programming_language=None):
    stdout, stderr = '', ''
    if programming_language is None:
        programming_language = info.get('language', info.get('lang', None)).lower()
    if programming_language=='python':
        compile_result = check_python_syntax(code)
        compile_success = compile_result['valid']
        if not compile_success:
            stdout = ''
            temp_msg = compile_result['error']
            stderr = f"[SyntaxError] {temp_msg['msg']} (Line {temp_msg['lineno']}, Column {temp_msg['offset']}): {temp_msg['text'].strip() if temp_msg['text'] else ''}"
    else:
        for _ in range(5):
            compile_result = try_parse(code, info, get_feedback=True)
            if isinstance(compile_result, int):
                if compile_result == 1:
                    compile_success = False
                else:
                    compile_success = True
                stdout = ''
                stderr = ''
            else:
                stdout = compile_result.stdout
                stderr = compile_result.stderr
                if isinstance(stdout, bytes):
                    stdout = stdout.decode('utf-8', errors='replace')
                if isinstance(stderr, bytes):
                    stderr = stderr.decode('utf-8', errors='replace')
                print("Return Code:", compile_result.returncode)     
                compile_success = compile_result.returncode == 0
            if compile_success:
                break
    return compile_success, stdout, stderr


def try_parse(code, info, get_feedback=False):
    lang = info.get('file_suffix', None)
    language = info.get('language', info.get("lang", None)).lower()

    if lang == 'py':
        try:
            ast.parse(code)
            return 0
        except:
            return 1
    elif lang.lower() in ('c', 'js', 'rb', 'jsx', 'cpp', 'cc', 'hpp', 'h'):
        if lang.lower() == 'c' or (lang == 'h' and language == 'c'):
            cflags = subprocess.check_output(['xml2-config', '--cflags'], text=True).strip()
            ldflags = subprocess.check_output(['xml2-config', '--libs'], text=True).strip()
            if os.name == "nt":
                ldflags += " -lbcrypt"
            else:
                ldflags += " -lcrypt"
            cmd = f'gcc -c -x c {cflags} {ldflags} -'
        elif lang.lower() == 'cpp' or lang == 'cc' or lang == 'hpp' or lang == 'h':
            try:
                cflags = subprocess.check_output(
                    ['pkg-config', '--cflags', 'libxml-2.0'],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
            except (FileNotFoundError, subprocess.CalledProcessError):
                try:
                    cflags = subprocess.check_output(
                        ['xml2-config', '--cflags'],
                        text=True, stderr=subprocess.DEVNULL
                    ).strip()
                except (FileNotFoundError, subprocess.CalledProcessError):
                    cflags = '-I/usr/include/libxml2'  
            ldflags = "-lcrypt"  
            xlang = 'c++-header' if lang.lower() in ('hpp', 'h') else 'c++'
            cmd = f"g++ -fsyntax-only -std=gnu++17 -x {xlang} {cflags} {ldflags} -"
        elif lang == 'js':
            cmd = 'node -c -'
        elif lang == 'rb':
            cmd = 'ruby -c -'
        elif lang == 'jsx':
            cmd = 'NODE_PATH=$(npm root --quiet -g) npx babel --presets @babel/preset-react --no-babelrc'
        try:
            if not get_feedback:
                process = subprocess.run(cmd, shell=True, timeout=5, input=code.encode(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if process.returncode == 0:
                    return 0
                else:
                    if lang == 'js':
                        cmd = 'NODE_PATH=$(npm root --quiet -g) npx babel --presets @babel/preset-react --no-babelrc'
                        process = subprocess.run(cmd, shell=True, timeout=5, input=code.encode(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return process.returncode
                    return 1
            else:
                process = subprocess.run(cmd, shell=True, timeout=5, input=code.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE )
                if lang == 'js' and process.returncode != 0:
                    cmd = 'NODE_PATH=$(npm root --quiet -g) npx babel --presets @babel/preset-react --no-babelrc'
                    process = subprocess.run(cmd, shell=True, timeout=5, input=code.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return process  
                
        except subprocess.TimeoutExpired:
            return 1
    elif lang in ('java', 'go'):
        with tempfile.NamedTemporaryFile(mode='w+', prefix='code', suffix='.'+lang, delete=False) as temp_file:
            temp_file_name = temp_file.name
            if lang == 'java':
                temp_file.write(code.replace('MyTestClass', os.path.basename(temp_file_name)[:-5]))
                cmd = 'javac {} {}'.format(get_cp_args(info), temp_file_name)
            elif lang == 'go':
                tmpdir = tempfile.mkdtemp(prefix="go_build_")
                try:
                    src_path = os.path.join(tmpdir, "main.go")
                    with open(src_path, "w", encoding="utf-8") as f:
                        f.write(code)
                    fmt_cmd = f"gofmt -w {src_path}"

                    gomod_path = os.path.join(tmpdir, "go.mod")
                    with open(gomod_path, "w", encoding="utf-8") as f:
                        f.write("module tempmod\n\ngo 1.20\n")
                    out_bin = os.path.join(tmpdir, "a.out")
                    build_cmd = f"cd {tmpdir} && go build -o {out_bin} ./..."

                    if not get_feedback:
                        subprocess.run(fmt_cmd, shell=True, timeout=5,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        process = subprocess.run(build_cmd, shell=True, timeout=10,
                                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return 0 if process.returncode == 0 else 1
                    else:
                        subprocess.run(fmt_cmd, shell=True, timeout=5,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                        process = subprocess.run(build_cmd, shell=True, timeout=10,
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        return process

                except subprocess.TimeoutExpired:
                    return 1
                finally:
                    shutil.rmtree(tmpdir, ignore_errors=True)
        try:
            if not get_feedback:
                process = subprocess.run(cmd, shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if process.returncode == 0:
                    return 0
                else:
                    return 1
            else:
                process = subprocess.run(cmd, shell=True, timeout=5, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                return process  
        except subprocess.TimeoutExpired:
            return 1
        finally:
            os.remove(temp_file_name)
    else:
        print(f"Language {lang} is not supported for syntax checking.")
        raise NotImplementedError()
        


def codeql_create_db(info, src_dir, db_dir):
    
    if info['file_suffix'] == 'py':
        cmd = './codeql/codeql database create {} --quiet --language=python --overwrite --source-root {}'
    # elif info['file_suffix'] == 'c':
    elif info['file_suffix'] in ['c', 'h', 'cpp', 'cc', 'hpp']:
        cmd = './codeql/codeql database create {} --quiet --language=cpp --overwrite --command="make -B" --source-root {}'
    elif info['file_suffix'] in ('js', 'jsx'):
        cmd = './codeql/codeql database create {} --quiet --language=javascript --overwrite --source-root {}'
    elif info['file_suffix'] == 'rb':
        if 'use_gemspec' in info and info['use_gemspec']:
            cmd = './codeql/codeql database create {} --quiet --language=ruby --overwrite --command="gem build" --source-root {}'
            src_dir = os.path.dirname(src_dir)
        else:
            cmd = './codeql/codeql database create {} --quiet --language=ruby --overwrite --source-root {}'
    elif info['file_suffix'] == 'go':
        ## TODO: temporarily set the platform to linux64
        os.environ['CODEQL_PLATFORM'] = 'linux64'
        cmd = './codeql/codeql database create {} --quiet --language=go --overwrite --source-root {}'
        
    elif info['file_suffix'] == 'java':
        cmd = './codeql/codeql database create {} --quiet --language=java --overwrite --command="bash compile_java.sh" --source-root {}'
    else:
        raise NotImplementedError()

    cmd = cmd.format(db_dir, src_dir)
    result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)
    
    # Print stderr if there is an error
    if result.returncode != 0:
        print(cmd)
        print("Error occurred:")
        print(result.stderr)
        # exit(1)
    return result.returncode


def make_output_dir(args, info, output_dir):
    # vul_type = info['cwe'].lower()
    vul_type = info['cwe'].lower() if info.get('cwe', None) else None
    scnario_name = info['scenario'] if 'scenario' in info else info['file_path'].split('/')[-1].split('.')[0] if 'file_path' in info else info['id']
    prompt_id = info.get('prompt_id', None)
    if args.init:
        if not vul_type:
            output_dir = os.path.join(output_dir, args.eval_type+'_init', scnario_name+f'_{prompt_id}')
        else:
            output_dir = os.path.join(output_dir, args.eval_type+'_init', vul_type, scnario_name)
    else:
        if not vul_type:
            output_dir = os.path.join(output_dir, args.eval_type, scnario_name+f'_{prompt_id}')
        else:
            output_dir = os.path.join(output_dir, args.eval_type, vul_type, scnario_name)
    return output_dir

def eval_setting(args, code, info, output_dir=None):
    safe_coder_file = SAFE_CODER_FILES_DIRECTORY
    # info = make_suffix(args, info)
                            
    file_ctx = info.get('file_context', None)
    func_ctx = info.get('func_context', None)
    code = extract_code(code, lr=info['language'], task=args.task, file_context=file_ctx, func_context=func_ctx)
    feedbacks = []
    if args.compile_only :
        output_srcs, non_parsed_srcs, feedbacks = make_parse_list([code], info, get_feedback=args.compile_only)
    else:
        output_srcs, non_parsed_srcs = make_parse_list([code], info, get_feedback=args.compile_only)
    valid = len(output_srcs)
    total = valid + len(non_parsed_srcs)
    
    output_dir = make_output_dir(args, info, output_dir)
    valid_source_paths = []
    invalid_source_paths = []
    for srcs, name in [(output_srcs, 'output_srcs'), (non_parsed_srcs, 'non_parsed_srcs')]:
        src_dir = os.path.join(output_dir, name)
        os.makedirs(src_dir, exist_ok=True)
        
        for i, src in enumerate(srcs):
            findex = f'{str(i).zfill(2)}'
            if info['file_suffix'] == 'java':
                class_name = 'MyTestClass' + findex
                fname = class_name + '.' + info['file_suffix']
                src = src.replace('MyTestClass', class_name)
            else:
                fname = findex + '.' + info['file_suffix']
            with open(os.path.join(src_dir, fname), 'w') as f:
                f.write(src)
        if name == 'non_parsed_srcs':
            invalid_source_paths.append(os.path.join(src_dir, fname))
            continue
        if name == 'output_srcs' and valid > 0:
            valid_source_paths.append(os.path.join(src_dir, fname))
            if info['file_suffix'] == 'c' or (info['file_suffix'] == 'h' and info['language'].lower() == 'c'):
                shutil.copy2(f'{safe_coder_file}/Makefile.c', os.path.join(src_dir, 'Makefile'))
            elif info['file_suffix'] in ['cpp', 'cc', 'hpp', 'h'] or info['language'].lower() == 'cpp':
                shutil.copy2(f'{safe_coder_file}/Makefile.cpp', os.path.join(src_dir, 'Makefile'))
            elif info['file_suffix'] == 'java':
                with open(f'{safe_coder_file}/compile_java.sh') as f:
                    makefile = f.read()
                makefile = makefile.replace('CLASS_PATH', get_cp_args(info))
                with open(os.path.join(src_dir, 'compile_java.sh'), 'w') as f:
                    f.write(makefile)
            elif info['file_suffix'] == 'rb' and 'use_gemspec' in info and info['use_gemspec']:
                # shutil.copy2(f'{safe_coder_file}/test.gemspec', os.path.join(src_dir, 'test.gemspec'))
                shutil.copy2(f'{safe_coder_file}/test.gemspec', output_dir)
    
    return valid, total, valid_source_paths, invalid_source_paths, feedbacks, output_dir



def make_suffix(args, info):
    if args.task in ['instruct'] or 'instruct_test' in args.task or 'autocomplete_test' in args.task:
        info['cwe'] = info['cwe_identifier']
        info['scenario'] = info['file_path'].split('/')[-1].split('.')[0]
        if 'file_suffix' not in info:
            info['file_suffix'] = info['file_path'].split('/')[-1].split('.')[-1]
            if info['language'].lower() == 'cpp':
                info['file_suffix'] = 'cpp'
            if info['language'].lower() == 'c':
                info['file_suffix'] = 'c'
    elif args.task in ['cvs', 'cvs_test', 'cvs_test2'] or 'cvs_test' in args.task:
        info['scenario'] = str(info['prompt_id'])
        if 'file_suffix' not in info:
            if info['language'] == 'csharp': 
                info['file_suffix'] = 'cs'
            elif info['language'] == 'cpp':
                info['file_suffix'] = 'cpp'
            else:
                info['file_suffix'] = list(LANGUAGE_SUFFIX_MAPS.keys())[list(LANGUAGE_SUFFIX_MAPS.values()).index(info['language'].lower())]
    elif 'llmseceval' in args.task :
        info['cwe'] = info['cwe_identifier']
    elif 'codeguardplus' in args.task:
        if 'cwe' not in info and 'cwe_identifier' in info:
            info['cwe'] = info['cwe_identifier']
        if 'language' not in info:
            temp = info['scenario']
            if temp[-1] == 'c':
                info['language'] = 'c'
                info['file_suffix'] = 'c'
            elif temp[-2:]=='py':
                info['language'] = 'python'
                info['file_suffix'] = 'py'
    if 'llmseceval' in args.task and not '_'+str(info.get('prompt_id', '')) in info['scenario']:
        info['scenario'] = info['scenario'] + '_' + str(info.get('prompt_id', ''))
    return info


class Parser:
    def __init__(self):
        self.fp_pattern = re.compile(r"<FILEPATH>(.+?)</FILEPATH>", re.DOTALL)
        self.fp_ht_pattern = re.compile(r"^###\s*(.+?)$", re.DOTALL | re.MULTILINE)
        self.md_pattern = re.compile(r"```(?!bash)\w+\n(.*?)\n```", re.DOTALL)
        self.code_pattern = re.compile(r"<CODE>(.+?)</CODE>", re.DOTALL)

    def _invalid(self, response: str) -> dict[pathlib.Path, str]:
        return {pathlib.Path("failed"): "Format not found. Full response:\n" + response}

    def _clean(self, s: str) -> str:
        s = s.strip()
        if s.startswith("**"):
            s = s[2:]
        if s.endswith("**"):
            s = s[:-2]
        s = s.strip()
        return s

    def _parse_md(self, response: str) -> list[str]:
        return [self._clean(s) for s in self.md_pattern.findall(response)]

    def _parse_code(self, response: str) -> list[str]:
        return [self._clean(s) for s in self.code_pattern.findall(response)]

    def _parse_multi_file_response(self, response: str) -> dict[pathlib.Path, str]:
        normal_file_paths = [
            pathlib.Path(self._clean(s)) for s in self.fp_pattern.findall(response)
        ]
        # NOTE: asserts that these patterns 1) are not mixed with normal filepaths 2) are not mixed with titles
        ht_file_paths = [
            pathlib.Path(self._clean(s)) for s in self.fp_ht_pattern.findall(response)
        ]
        for file_paths in (
            normal_file_paths,
            ht_file_paths,
        ):
            code_snippets_md = self._parse_md(response)
            code_snippets_code = self._parse_code(response)
            if len(file_paths) == len(code_snippets_md) and len(file_paths) > 0:
                return {fp: c for fp, c in zip(file_paths, code_snippets_md)}
            elif len(file_paths) == len(code_snippets_code) and len(file_paths) > 0:
                # failsave code parsing in case some of them have md and some not
                codes = []
                for code in code_snippets_code:
                    md_parsed = self._parse_md(code)
                    if len(md_parsed) > 0:
                        codes.append(md_parsed[0])
                    else:
                        codes.append(code)
                assert len(codes) == len(code_snippets_code)
                return {fp: c for fp, c in zip(file_paths, codes)}
        return response

    def _parse_single_file_response(self, response: str) -> dict[pathlib.Path, str]:
        code_snippets_md = self._parse_md(response)
        code_snippets_code = self._parse_code(response)
        if len(code_snippets_md) > 0:
            return code_snippets_md[0]
        elif len(code_snippets_code) > 0:
            return  code_snippets_code[0]
        else:
            return response

    def parse_response(self, response: str, is_multi_file: bool) -> dict[pathlib.Path, str]:
        if is_multi_file:
            return self._parse_multi_file_response(response)
        else:
            return self._parse_single_file_response(response)

