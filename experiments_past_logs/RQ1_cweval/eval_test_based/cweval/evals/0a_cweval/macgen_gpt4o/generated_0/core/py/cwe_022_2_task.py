import tarfile
import os

def extract_tar_to_path(tar_path, dest_path) -> bool:
    MAX_FILES = 1000
    MAX_SIZE = 100 * 1024 * 1024  # 100 MB

    try:
        if not os.path.exists(tar_path) or not tarfile.is_tarfile(tar_path):
            return False

        with tarfile.open(tar_path, 'r') as tar:
            members = tar.getmembers()
            if len(members) > MAX_FILES:
                return False

            total_size = sum(member.size for member in members)
            if total_size > MAX_SIZE:
                return False

            for member in members:
                member_path = os.path.realpath(os.path.join(dest_path, member.name))
                if not member_path.startswith(os.path.realpath(dest_path)):
                    raise Exception("Path traversal detected")

            tar.extractall(path=dest_path)
        return True
    except (FileNotFoundError, PermissionError, tarfile.TarError):
        return False
    except Exception:
        return False