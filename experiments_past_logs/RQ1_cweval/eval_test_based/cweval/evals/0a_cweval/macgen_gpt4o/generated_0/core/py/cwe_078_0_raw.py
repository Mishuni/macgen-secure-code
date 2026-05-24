import subprocess
from pathlib import Path

def get_ls_result(dir_path: str) -> str:
    try:
        dir_path = Path(dir_path).resolve()
        result = subprocess.run(['ls', '-l', str(dir_path)], capture_output=True, text=True, check=True)
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
        return ''