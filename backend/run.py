"""PyInstaller 打包入口：Windows 便携版/安装版使用。

设置为 SERVE_STATIC=1，后端自动托管前端静态文件，
用户无需单独部署前端，双击即可使用。
"""
import os
import sys
import webbrowser

import uvicorn


# 确保 app 包可导入（源码模式需要）
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


def _detect_static_dir() -> str:
    """找到前端 dist 目录：
    - PyInstaller 打包后 → _internal/frontend/dist（通过 sys._MEIPASS）
    - 源码模式 → backend/ 同级 frontend/dist
    """
    frozen = getattr(sys, "frozen", False)
    if frozen:
        base = sys._MEIPASS  # _internal 目录
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, "frontend", "dist"),
        os.path.join(base, "dist"),
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    return candidates[0]


def _ensure_data_dirs():
    """确保数据库和日志目录存在（打包后 exe 同级）。"""
    frozen = getattr(sys, "frozen", False)
    if frozen:
        base = os.path.dirname(os.path.abspath(sys.executable))
        for sub in ("data", "logs"):
            os.makedirs(os.path.join(base, sub), exist_ok=True)


if __name__ == "__main__":
    os.environ.setdefault("SERVE_STATIC", "1")
    os.environ.setdefault("STATIC_DIR", _detect_static_dir())

    _ensure_data_dirs()

    port = int(os.environ.get("PORT", 8000))

    print("========== 混凝土课程设计计算平台 ==========")
    print(f"  地址: http://localhost:{port}")
    print(f"  静态文件: {os.environ['STATIC_DIR']}")
    print("============================================")

    webbrowser.open(f"http://localhost:{port}")

    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
