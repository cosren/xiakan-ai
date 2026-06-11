import json
import os
from pathlib import Path

import requests


class MaterialLibrary:
    def __init__(self, local_root: str = "materials", search_api_url: str | None = None):
        self.local_root = Path(local_root)
        self.local_root.mkdir(parents=True, exist_ok=True)
        self.search_api_url = search_api_url or os.getenv("MATERIAL_SEARCH_API")

    def list_local(self, page: int = 1, size: int = 50) -> list[dict]:
        entries = []
        supported = {".mp4", ".mov", ".mkv", ".avi", ".mp3", ".wav", ".srt"}
        for path in sorted(self.local_root.glob("**/*")):
            if path.suffix.lower() in supported and path.is_file():
                entries.append({
                    "name": path.stem,
                    "path": str(path.resolve()),
                    "type": path.suffix.lower().lstrip('.'),
                })
        start = (page - 1) * size
        return entries[start:start + size]

    def search_network(self, query: str, api_url: str | None = None) -> list[dict]:
        url = api_url or self.search_api_url
        if not url:
            raise ValueError("网络素材搜索未配置，请设置环境变量 MATERIAL_SEARCH_API 或传入 api_url")

        response = requests.get(url, params={"q": query}, timeout=15)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        if isinstance(data, list):
            return data
        return []

    def download_material(self, url: str, dest: str | None = None) -> str:
        dest_path = Path(dest or self.local_root / Path(url).name)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return str(dest_path.resolve())
