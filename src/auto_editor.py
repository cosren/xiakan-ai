import json
from pathlib import Path
from src.utils.fetcher import MediaAnalyzer
from src.utils.shotcut_exporter import ShotcutExporter


class AutoEditor:
    def __init__(self, llm_client, ffmpeg_bin: str = "ffmpeg", ffprobe_bin: str = "ffprobe"):
        self.llm = llm_client
        self.media_analyzer = MediaAnalyzer(ffmpeg_bin=ffmpeg_bin, ffprobe_bin=ffprobe_bin)

    def create_edit_script(self, source_video: str, title: str, bgm_name: str | None = None) -> dict:
        metadata = self.media_analyzer.probe_media(source_video)
        scene_changes = self.media_analyzer.detect_scenes(source_video)
        silence_ranges = self.media_analyzer.detect_silence(source_video)
        transcript = self.media_analyzer.transcribe_audio(source_video)
        shot_analysis = self.media_analyzer.analyze_shots(source_video, scene_changes, transcript=transcript, max_shots=8)

        context = self.media_analyzer.build_context(source_video, metadata, scene_changes, silence_ranges)
        prompt = (
            f"你是视频自动剪辑策划师。给定以下视频元数据、场景检测结果、音频转录内容和镜头分析结果，生成一个剪辑脚本。\n"
            f"视频标题: {title}\n"
            f"{context}\n"
            f"音频转录:\n{transcript}\n"
            f"镜头分析:\n{json.dumps(shot_analysis, ensure_ascii=False, indent=2)}\n"
            f"请在输出中给出：\n"
            f"1. 剪辑段落数组，每段包含 source_start、source_end、action、voiceover、bgm_selection。\n"
            f"2. 说明每段应该保留什么画面类型。\n"
            f"3. 最后给出 Shotcut 工程文件导出说明。\n"
        )
        director_prompt = self._load_director_prompt()
        raw_response = self.llm.ask(system=director_prompt, prompt=prompt)

        timeline = self._parse_timeline(raw_response)
        return {
            "source_video": source_video,
            "title": title,
            "timeline": timeline,
            "bgm": bgm_name or "默认BGM",
            "metadata": self._build_media_metadata(metadata),
        }

    def export_shotcut_project(self, source_video: str, timeline: list[dict], metadata: dict, project_path: str, bgm_path: str | None = None) -> str:
        exporter = ShotcutExporter(source_video=source_video, bgm_path=bgm_path)
        exporter.export(project_path, timeline, metadata)
        return project_path

    def _load_director_prompt(self) -> str:
        prompt_file = Path("skills/xiakan/director.json")
        if not prompt_file.exists():
            raise FileNotFoundError("skills/xiakan/director.json not found")
        return json.loads(prompt_file.read_text(encoding="utf-8"))["system_prompt"]

    def _parse_timeline(self, raw: str) -> list[dict]:
        try:
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return [{"source_start": 0.0, "source_end": 10.0, "action": "highlight", "voiceover": raw, "bgm_selection": "默认BGM"}]

    def _build_media_metadata(self, probe: dict) -> dict:
        format_info = probe.get("format", {})
        streams = probe.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        return {
            "duration": float(format_info.get("duration", 0.0)),
            "width": int(video.get("width", 1920)),
            "height": int(video.get("height", 1080)),
            "frame_rate_num": int(video.get("r_frame_rate", "24000/1001").split("/")[0]),
            "frame_rate_den": int(video.get("r_frame_rate", "24000/1001").split("/")[1]),
        }
