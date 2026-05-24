import logging, sys
from pathlib import Path

def setup_logging(log_path: Path) -> None:
    print(f"Logging to {log_path}")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        # level=logging.WARNING,
        format="%(message)s",   
        handlers=[
            # logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

def attach_pid_log_handler(base_dir: Path, pid: int, phase: str = "phase1") -> logging.Handler:
    pid_dir = base_dir / "logs" / f"pid_{pid}" 
    pid_dir.mkdir(parents=True, exist_ok=True)
    log_path = pid_dir / f"{pid}_{phase}.log"

    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter(
        "%(message)s"
    )
    handler.setFormatter(formatter)

    class _PidFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if not hasattr(record, "pid"):
                record.pid = pid
            return True

    handler.addFilter(_PidFilter())

    root = logging.getLogger()
    root.addHandler(handler)
    return handler


def detach_handler(handler: logging.Handler) -> None:
    root = logging.getLogger()
    root.removeHandler(handler)
    handler.close()
