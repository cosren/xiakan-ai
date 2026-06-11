import json
from pathlib import Path
from src.pipeline import XiakanPipelineEngine
from src.utils.fetcher import MediaAnalyzer


class ScriptGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.engine = XiakanPipelineEngine(llm_client)
        self.media_analyzer = MediaAnalyzer()

    def generate_text_script(self, title: str, source_video: str | None = None) -> dict:
        if source_video:
            source_path = Path(source_video)
            if not source_path.exists():
                raise FileNotFoundError(f"源视频文件不存在: {source_video}")
            scene_changes = self.media_analyzer.detect_scenes(source_video)
            silence_ranges = self.media_analyzer.detect_silence(source_video)
            transcript = self.media_analyzer.transcribe_audio(source_video)
            shot_analysis = self.media_analyzer.analyze_shots(
                source_video,
                scene_changes,
                transcript=transcript,
                max_shots=8,
            )
            context = self.media_analyzer.build_context(
                source_video,
                self.media_analyzer.probe_media(source_video),
                scene_changes,
                silence_ranges,
            )
            context += f"\n音频转录:\n{transcript}\n"
            context += f"\n镜头分析:\n{json.dumps(shot_analysis, ensure_ascii=False, indent=2)}\n"
            return self.engine.generate_script(
                title=title,
                source_video=source_video,
                media_context=context,
            )

        return self.engine.generate_script(title=title)

    def save_script(self, script_text: str, destination: str) -> str:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(script_text, encoding="utf-8")
        return str(path.resolve())
