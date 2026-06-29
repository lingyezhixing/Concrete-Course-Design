"""Windows 便携版构建脚本。

用法:
  conda activate concrete
  python build_win.py

流程:
  1. npm run build (前端构建，更新 frontend/dist)
  2. PyInstaller --onefile (打包后端 + 前端 dist + exe 图标)
  3. 将 exe 放入根目录 Portable/ 文件夹，便于直接分发与运行

产物:
  Portable/ConcreteCourseDesign.exe   （单文件，双击即运行）

说明:
  Portable/ 内的 exe 可直接双击运行，但可能不是最新版本；
  最新版建议从 GitHub Releases 下载。
"""
import os
import subprocess
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
BUILD_DIR = ROOT / "build"                 # PyInstaller 中间产物（scratch）
PORTABLE_DIR = ROOT / "Portable"           # 最终 exe 落地位置（分发用）
EXE_NAME = "ConcreteCourseDesign.exe"
EXE_PATH = PORTABLE_DIR / EXE_NAME
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
    print("  2/2  PyInstaller 打包 (--onefile) → Portable/")
    print("=" * 60)

    # 清理旧产物
    for p in [WORK_DIR, ROOT / "ConcreteCourseDesign.spec"]:
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

    PORTABLE_DIR.mkdir(parents=True, exist_ok=True)
    if EXE_PATH.exists():
        EXE_PATH.unlink()

    args = [
        str(ENTRY),
        "--onefile",
        f"--name=ConcreteCourseDesign",
        f"--distpath={PORTABLE_DIR}",
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
    # 清理空的 build 中间目录（若已空）
    if BUILD_DIR.exists() and not any(BUILD_DIR.iterdir()):
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    print(f"\n  打包完成: {EXE_PATH}")
    if EXE_PATH.exists():
        size_mb = EXE_PATH.stat().st_size / (1024 * 1024)
        print(f"  文件大小: {size_mb:.1f} MB")


if __name__ == "__main__":
    if not shutil.which("npm"):
        print("[错误] 未找到 npm，请确保 Node.js 已安装")
        sys.exit(1)

    build_frontend()
    build_exe()
    print("\n  所有步骤完成！")
    print(f"  便携版位置: {PORTABLE_DIR}")
    print("  注: Portable/ 内 exe 可能不是最新版本，最新版请从 GitHub Releases 下载。")
