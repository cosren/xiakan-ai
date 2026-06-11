import os
import shutil
import subprocess
import sys
from pathlib import Path

from src.utils.narrator_cli import NarratorAICLI


class Installer:
    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent
        self.requirements = self.root / "requirements.txt"

    def _run(self, args: list[str], capture: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable] + args, capture_output=capture, text=True)

    def install_dependencies(self) -> bool:
        if not self.requirements.exists():
            print("requirements.txt 未找到，跳过依赖安装。")
            return False
        print("🔧 安装 Python 依赖...")
        proc = self._run(["-m", "pip", "install", "-r", str(self.requirements)])
        if proc.returncode != 0:
            print(f"❌ 依赖安装失败: {proc.stderr or proc.stdout}")
            return False
        print("✅ Python 依赖安装完成。")
        return True

    def verify_system(self) -> bool:
        print("🔎 验证系统依赖...")
        errors = []

        if not shutil.which("ffmpeg"):
            errors.append("ffmpeg 未安装或不在 PATH 中。请安装 ffmpeg。")
        if not shutil.which("ffprobe"):
            errors.append("ffprobe 未安装或不在 PATH 中。请安装 ffmpeg 包含 ffprobe。")

        narrator = NarratorAICLI()
        if not narrator.is_installed():
            errors.append("narrator-ai-cli 未安装或不在 PATH 中。请安装 narrator-ai-cli。")

        if errors:
            for err in errors:
                print(f"❌ {err}")
            return False

        print("✅ 系统依赖检查通过。")
        return True

    def setup(self) -> bool:
        ok = self.install_dependencies()
        if not ok:
            return False
        return self.verify_system()


if __name__ == '__main__':
    installer = Installer()
    step = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if step == "setup":
        success = installer.setup()
    else:
        success = installer.verify_system()
    sys.exit(0 if success else 1)
