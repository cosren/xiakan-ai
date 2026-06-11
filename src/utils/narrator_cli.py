import json
import subprocess
from typing import List


class NarratorAICLI:
    def __init__(self, cli_bin: str = "narrator-ai-cli"):
        self.cli_bin = cli_bin

    def is_installed(self) -> bool:
        try:
            subprocess.run([self.cli_bin, "--version"], capture_output=True, text=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def run(self, args: List[str]) -> str:
        command = [self.cli_bin] + args
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"narrator-ai-cli command failed ({' '.join(command)}): {result.stderr.strip() or result.stdout.strip()}"
            )
        return result.stdout.strip()

    def run_json(self, args: List[str]) -> dict:
        output = self.run(args + ["--json"])
        return json.loads(output)
