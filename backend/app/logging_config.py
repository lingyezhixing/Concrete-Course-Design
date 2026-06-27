"""应用日志配置：控制台 + 每启动一个时间戳文件（留 10 个），抑制 uvicorn 访问日志刷屏。

镜像 LLM-Manager 的 ``setup_logging``，但挂载点改为 FastAPI ``lifespan``——uvicorn 启动时
会用 ``dictConfig`` 覆盖 root logger 的 handlers（已实测），``lifespan`` 在其后执行，
这里的 handler 才能存活。"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

KEEP_LOGS = 10
LOG_PREFIX = "concrete-backend"
_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"

_logging_configured = False
logger = logging.getLogger(__name__)


def _cleanup_old_logs(log_dir: str, keep: int = KEEP_LOGS) -> None:
    """保留最近 keep 个 concrete-backend_*.log（按 mtime），删旧的。"""
    files = sorted(
        Path(log_dir).glob(f"{LOG_PREFIX}_*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for stale in files[keep:]:
        try:
            stale.unlink()
        except OSError:
            pass


def setup_logging(level: str = "INFO", log_dir: str = "logs") -> None:
    """配置 root logger（一次性）：控制台 + 每次启动一个时间戳文件（留 10 个）。

    必须在 FastAPI lifespan 中调用：uvicorn 启动会用 ``dictConfig`` 覆盖 root handlers，
    lifespan 在其后执行，这里的 handler 才不会被清掉。"""
    global _logging_configured
    if _logging_configured:
        return

    numeric = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(numeric)
    for handler in list(root.handlers):
        root.removeHandler(handler)

    formatter = logging.Formatter(_FORMAT, _DATEFMT)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(numeric)
    console.setFormatter(formatter)
    root.addHandler(console)

    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        log_file = Path(log_dir) / f"{LOG_PREFIX}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
        _cleanup_old_logs(log_dir, keep=KEEP_LOGS)
        logger.info("logging to %s", log_file)
    except OSError:
        pass

    # 降噪：uvicorn.access 每请求一行（健康检查刷屏），抬高到 WARNING
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    _logging_configured = True
