"""Windows 便携版构建脚本。

用法:
  conda activate concrete
  python build_win.py

流程:
  1. npm run build (前端构建)
  2. PyInstaller --onefile (打包后端 + 前端 dist + exe 图标)
"""
import os
import subprocess
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
BUILD_DIR = ROOT / "build"
EXE_PATH = BUILD_DIR / "ConcreteCourseDesign.exe"
WORK_DIR = BUILD_DIR / "_work"
ENTRY = ROOT / "backend" / "run.py"
FRONTEND_DIST = ROOT / "frontend" / "dist"
ICON_PATH = ROOT / "assets" / "logo.ico"


def build_frontend():
    print("=" * 60)
    print("  1/2  构建前端 (npm run build)")
    print("=" * 60)
    subprocess.run(
        "npm run build",
        cwd=str(ROOT / "frontend"),
        check=True,
        shell=True,
    )
    if not FRONTEND_DIST.is_dir():
        print("[错误] 前端构建失败: frontend/dist/ 不存在")
        sys.exit(1)
    print(f"  前端构建完成: {FRONTEND_DIST}")


def build_exe():
    print("=" * 60)
    print("  2/2  PyInstaller 打包 (--onefile)")
    print("=" * 60)

    for p in [WORK_DIR, ROOT / "ConcreteCourseDesign.spec"]:
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

    if EXE_PATH.exists():
        EXE_PATH.unlink()

    args = [
        str(ENTRY),
        "--onefile",
        f"--name=ConcreteCourseDesign",
        f"--distpath={BUILD_DIR}",
        f"--workpath={WORK_DIR}",
        f"--paths={ROOT / 'backend'}",
        f"--add-data={FRONTEND_DIST}{os.pathsep}frontend/dist",
        "--hidden-import=app.main",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--collect-all=app",
        "--clean",
        "--noconfirm",
    ]

    if ICON_PATH.is_file():
        args.append(f"--icon={ICON_PATH}")

    from PyInstaller import __main__ as pyi
    pyi.run(args)

    spec_file = ROOT / "ConcreteCourseDesign.spec"
    if spec_file.exists():
        spec_file.unlink()
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR, ignore_errors=True)

    print(f"\n  打包完成: {EXE_PATH}")


if __name__ == "__main__":
    if not shutil.which("npm"):
        print("[错误] 未找到 npm，请确保 Node.js 已安装")
        sys.exit(1)

    build_frontend()
    build_exe()
    print("\n  所有步骤完成！")
