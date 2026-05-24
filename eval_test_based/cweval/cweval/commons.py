import multiprocessing as mp
import os
import subprocess
import tempfile
from typing import Any, Callable, Dict, List, Tuple
import ast
import fire
import numpy as np
from natsort import natsorted

# LANGS_COMPILE = ['c', 'cpp', 'go']
LANGS_COMPILE = ['c', 'cpp', 'go', 'py', 'js']
# LANGS_RUN = ['py', 'js']
LANGS_RUN = []
LANGS = LANGS_COMPILE + LANGS_RUN

COMPILE_DIR = 'compiled'
BENCHMARK_DIR = 'benchmark'

C_HEADERS = '''#include <archive_entry.h>
#include <jwt.h>
#include <errno.h>
#include <sys/wait.h>
#include <libxml/xpath.h>
#include <sqlite3.h>
#include <archive.h>
#include <ctype.h>
#include <libxml/parser.h>
#include <openssl/evp.h>
#include <openssl/des.h>
#include <openssl/aes.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>
#include <stdlib.h>
#include <libgen.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>
#include <openssl/sha.h>
#include <regex.h>
#include <unistd.h>
#include <openssl/rand.h>
#include <archive.h>
#include <archive_entry.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <libgen.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/evp.h>
#include <openssl/md5.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <regex.h>
#include <sqlite3.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
'''


CPP_HEADERS = '''#include <iostream>
#include <string>
#include <cstring>
#include <cctype>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <filesystem>
#include <archive.h>
#include <archive_entry.h>
#include <memory>
#include <vector>
#include <sys/types.h>
#include <sys/wait.h>
#include <map>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cstdio>
#include <openssl/aes.h>
#include <openssl/des.h>
#include <openssl/rand.h>
#include <tuple>
#include <stdexcept>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <sys/stat.h>
#include <utility>
#include <regex>
#include <sqlite3.h>
'''
# include <jwt.h>

PY_HEADERS = '''import hashlib
import html
import tarfile
from urllib.parse import urlparse
from typing import Tuple, List, Dict
import yaml
from Crypto.Cipher import AES, DES
import datetime
from tempfile import NamedTemporaryFile, TemporaryFile, mktemp
from Crypto.Cipher import AES
import jwt
import requests
import os
import json
from Crypto.PublicKey import DSA
from Crypto.PublicKey import RSA
from yaml import Loader
import argon2
import re
import subprocess
import sqlite3
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from lxml import etree
from Crypto.Cipher import AES
from Crypto.Cipher import AES, DES
from Crypto.PublicKey import DSA
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from lxml import etree
from tempfile import NamedTemporaryFile, TemporaryFile, mktemp
from urllib.parse import urlparse
from yaml import Loader
import argon2
import datetime
import hashlib
import html
import json
import jwt
import os
import re
import requests
import sqlite3
import subprocess
import tarfile
import yaml
'''


def complete_code(code: str, lang: str) -> str:
    if lang == 'c':
        return C_HEADERS + code
    elif lang == 'cpp':
        return CPP_HEADERS + code
    elif lang == 'py':
        return PY_HEADERS + code
    elif lang == 'go':
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(code)
            f.flush()
            filename = f.name
        cmd = f'goimports -w {filename} {filename}'
        exec_cmd_shell(cmd, check=False)
        with open(filename, 'r') as f:
            fixed_code = f.read()
        os.remove(filename)
        return fixed_code
    else:
        return code


def get_code_from(
    msg: str,
    only_last: bool = False,
    only_first: bool = False,
    add_new_line: bool = False,
) -> str:
    assert not (
        only_last and only_first
    ), '`only_last` and `only_first` cannot be both True'
    tail = '\n' if add_new_line else ''
    if '```' not in msg:
        return msg + tail if add_new_line else msg
    code_blocks: List[str] = []
    msg_lines = msg.splitlines()
    i_line = 0
    while i_line < len(msg_lines):
        line = msg_lines[i_line]
        if line.startswith('```'):
            code_lines = []
            i_line += 1
            while i_line < len(msg_lines):
                line = msg_lines[i_line]
                if line.startswith('```'):
                    break
                code_lines.append(line)
                i_line += 1
            # end while for this code block
            code_blocks.append('\n'.join(code_lines) + tail)
            if only_first:
                return code_blocks[0]
        # end if for this code block
        i_line += 1
    # end while for all code blocks
    if only_last:
        return code_blocks[-1]
    return '\n'.join(code_blocks)


def run_in_subprocess(func: Callable[..., Any], *args, **kwargs) -> Any:
    """
    Run a function in a separate subprocess and return its result.

    Args:
        func: The function to run in the subprocess
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value from the function

    Example:
        def memory_intensive_function(x):
            # This will run in its own memory space
            large_list = [i for i in range(10**6)]
            return x * 2

        result = run_in_subprocess(memory_intensive_function, 5)
    """

    def wrapper(func, return_queue, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return_queue.put(result)
        except Exception as e:
            return_queue.put(e)

    # Create a queue to get the return value
    return_queue = mp.Queue()

    # Create and start the process
    process = mp.Process(
        target=wrapper, args=(func, return_queue) + args, kwargs=kwargs
    )
    process.start()

    # Wait for the process to complete
    process.join()

    # Get the result
    result = return_queue.get()

    # Check if the result is an exception
    if isinstance(result, Exception):
        raise result

    return result


def pass_at_k(n, c, k) -> float:
    """
    :param n: total number of samples
    :param c: number of correct samples
    :param k: k in pass@$k$
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))


def exec_cmd(
    cmd: List[str], check: bool = True, capture_output: bool = True
) -> Tuple[int, str, str]:
    assert isinstance(cmd, list)
    result = subprocess.run(cmd, capture_output=capture_output, text=True, check=check)
    return result.returncode, result.stdout, result.stderr


def exec_cmd_shell(
    cmd: str, check: bool = True, capture_output: bool = True
) -> Tuple[int, str, str]:
    assert isinstance(cmd, str)
    result = subprocess.run(
        cmd, capture_output=capture_output, text=True, check=check, shell=True
    )
    return result.returncode, result.stdout, result.stderr


def compile_c(
    src_path: str, compiled_path: str, check: bool = True
) -> Tuple[int, str, str]:
    lib_options = [
        '-lsqlite3',
        '-ljwt',
        '-lcurl',
        '-lxml2',
        '-lssl',
        '-lcrypto',
        '-larchive',
        '-ljansson',
        '-lcjson',
        '-ljson-c',
        '-lcrypt',
        '$(xml2-config --cflags --libs)',
    ]
    if 'lang/c' in src_path:
        exclude_patterns = [
            'lang/c/cwe_476_0_c_',
        ]
        if not any([pattern in src_path for pattern in exclude_patterns]):
            lib_options.append('-fsanitize=address')
    cmd = ['gcc', src_path, '-o', compiled_path] + lib_options
    cmd_str = ' '.join(cmd)
    returncode, stdout, stderr = exec_cmd_shell(cmd_str, check)
    if returncode != 0:
        print(f'Error compiling {src_path}:\n{stderr}', flush=True)
    return returncode, stdout, stderr, src_path

import shlex
import subprocess
from typing import Tuple, List

def _expand_xml2_flags() -> List[str]:
    for cmd in (["pkg-config", "--cflags", "--libs", "libxml-2.0"],
                ["xml2-config", "--cflags", "--libs"]):
        try:
            out = subprocess.check_output(cmd, text=True).strip()
            if out:
                return out.split()
        except Exception:
            pass
    return ["-lxml2"]

def compile_cpp(
    src_path: str, compiled_path: str, check: bool = True
) -> Tuple[int, str, str, str]:
    cxx = "g++"
    cxxstd = "-std=gnu++17"

    cflags: List[str] = [
        "-std=c++17",
        "-Ithird_party/jwt-cpp/include",
        "-I/usr/include/jsoncpp",
    ]
    if "lang/cpp" in src_path:
        cflags.append("-fsanitize=address")
    


    ldflags: List[str] = [
        "-lsqlite3",
        "-lcurl",
        "-lssl",
        "-lcrypto",
        '-lcrypt',
        "-lbcrypt",
        "-larchive",
        "-ljansson",
        "-lcjson",
        "-ljsoncpp",
        "-lz",
        "-ldl",
        "-lpthread",
    ]
    ldflags += _expand_xml2_flags()

    cmd = [cxx, cxxstd, src_path, "-o", compiled_path] + cflags + ldflags #+ 
    cmd_str = " ".join(shlex.quote(x) for x in cmd)
    returncode, stdout, stderr = exec_cmd_shell(cmd_str, check)

    need_fs = (
        "experimental::filesystem" in stderr
        or "std::filesystem" in stderr
        or "undefined reference to `std::experimental::filesystem" in stderr
        or "undefined reference to `std::filesystem" in stderr
    )
    if returncode != 0 and need_fs:
        cmd2 = cmd + ["-lstdc++fs"]
        cmd2_str = " ".join(shlex.quote(x) for x in cmd2)
        returncode2, stdout2, stderr2 = exec_cmd_shell(cmd2_str, check=False)

        if returncode2 == 0 or "cannot find -lstdc++fs" not in (stderr2 or ""):
            return returncode2, stdout2, stderr2, src_path

    if returncode != 0:
        print(f"Error compiling {src_path}:\n{stderr}", flush=True)
    return returncode, stdout, stderr, src_path



def compile_go(
    src_path: str, compiled_path: str, check: bool = True
) -> Tuple[int, str, str]:
    fmt_cmd = ['gofmt', '-l', '-s', src_path]
    fmt_cmd_str = ' '.join(fmt_cmd)
    fmt_returncode, fmt_stdout, fmt_stderr = exec_cmd_shell(fmt_cmd_str, check=False)

    if fmt_returncode != 0:
        print(f'gofmt detected formatting issues in {src_path}:\n{fmt_stderr}', flush=True)

    cmd = ['go', 'build', '-o', compiled_path, src_path]
    cmd_str = ' '.join(cmd)
    returncode, stdout, stderr = exec_cmd_shell(cmd_str, check)
    if returncode != 0:
        print(f'Error compiling {src_path}:\n{stderr}', flush=True)
    return returncode, stdout, stderr, src_path

import subprocess

def compile_js(
    src_path: str, compiled_path: str = "", check: bool = True
) -> Tuple[int, str, str, str]:
    with open(src_path, 'r') as f:
        code = f.read()

    fallback_cmd = (
        'NODE_PATH=$(npm root --quiet -g) npx babel '
        '--presets @babel/preset-env --no-babelrc --filename dummy.js'
    )
    cmds = [
        ('node -c -', 'node'),
        (fallback_cmd, 'babel')
    ]
    for cmd_str, name in cmds:
        try:
            proc = subprocess.run(
                cmd_str,
                shell=True,
                timeout=5,
                input=code.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if proc.returncode == 0:
                return proc.returncode, proc.stdout.decode(), proc.stderr.decode(), src_path
            print(f"[{name}] compile error in {src_path}:\n{proc.stderr.decode()}")
            if name == 'babel':
                return proc.returncode, proc.stdout.decode(), proc.stderr.decode(), src_path
        except subprocess.TimeoutExpired:
            return 1, "", f"{name} compile timed out", src_path

    return 1, "", "Unknown error", src_path

def compile_python(
    src_path: str, compiled_path: str, check: bool = True
):
    try:
        with open(src_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        return 0, "", "", src_path
    except SyntaxError as e:
        return 1, e.text.strip(), str(e.msg)+str(e.lineno)+str(e.offset), src_path


def compile_src(
    src_path: str, compiled_path: str, check: bool = True
) -> Tuple[int, str, str]:
    os.makedirs(os.path.dirname(compiled_path), exist_ok=True)
    lang = os.path.splitext(src_path)[1][1:]
    assert lang in LANGS_COMPILE, f'Unknown language for compile: {lang} for {src_path}'
    return {
        'c': compile_c,
        'cpp': compile_cpp,
        'go': compile_go,
        'py': compile_python,
        'js': compile_js,
    }[
        lang
    ](src_path, compiled_path, check)


def compile_list(
    src_path_list: List[str],
    compiled_path_list: List[str],
    check: bool = True,
    num_proc: int = 8,
) -> List[Tuple[int, str, str]]:
    # compiler sanity check
    cmd_checks = [
        'gcc --version',
        'g++ --version',
        'go version',
    ]
    for cmd_check in cmd_checks:
        returncode, stdout, stderr = exec_cmd_shell(cmd_check, check=True)

    assert len(src_path_list) == len(compiled_path_list)
    rets: List[Tuple[int, str, str]] = []
    rets_dict: Dict[str, Tuple[int, str, str]] = {}
    if num_proc == 1:
        for src_path, compiled_path in zip(src_path_list, compiled_path_list):
            ret = compile_src(src_path, compiled_path, check)
            rets.append(ret)
            rets_dict[src_path] = ret
    else:
        with mp.Pool(num_proc) as pool:
            rets = pool.starmap(
                compile_src,
                zip(src_path_list, compiled_path_list, [check] * len(src_path_list)),
            )
        for src_path, ret in zip(src_path_list, rets):
            rets_dict[src_path] = ret
    # return rets, rets_dict
    return rets_dict


def compile_all_in(
    path: str,
    check: bool = True,
    num_proc: int = 8,
) -> List[Tuple[int, str, str]]:
    src_path_list = []
    compiled_path_list = []
    if os.path.isfile(path):
        file_wo_ext, ext = os.path.splitext(path)
        if ext[1:] in LANGS_COMPILE:
            src_path_list.append(path)
            compiled_path = os.path.join(
                os.path.dirname(path), COMPILE_DIR, os.path.basename(file_wo_ext)
            )
            compiled_path_list.append(compiled_path)
    else:
        for root, _, files in os.walk(path):
            if '__pycache__' in root:
                continue
            for file in natsorted(files):
                file_wo_ext, ext = os.path.splitext(file)
                if ext[1:] in LANGS_COMPILE:
                    src_path = os.path.join(root, file)
                    compiled_path = os.path.join(root, COMPILE_DIR, file_wo_ext)
                    src_path_list.append(src_path)
                    compiled_path_list.append(compiled_path)

    return compile_list(src_path_list, compiled_path_list, check, num_proc)


if __name__ == '__main__':
    fire.Fire()
    # python cweval/commons.py compile_all_in --path benchmark
