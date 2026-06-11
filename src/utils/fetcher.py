import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from openai import OpenAI
from PIL import Image, ImageStat

class MovieDetailFetcher:
    """
    负责将用户输入的单一片名，转化为长文本的电影分场及视觉细节Context
    """
    def __init__(self):
        pass

    def fetch_by_title(self, title: str) -> str:
        print(f"[Fetcher] 🔍 正在检索电影《{title}》的全量叙事脉络与细节...")
        simulated_context = f"电影《{title}》核心分镜信息：\n" \
                            f"【第一幕】大雪纷飞的厂区，一群落魄的下岗工人在风雪中为老厂长举行极其严肃的送葬仪式。男主神情迷茫。由于乐队吹错曲子，引发纠纷。\n" \
                            f"【第二幕】男主在风雪中因为和妻子离婚，净身出户，妻子已经跟了一个卖假药的富商。男主为了抢抚养费发生冲突，警察突击检查，现场陷入尴尬死寂。\n" \
                            f"【第三幕】大熔炉最终被无情爆破，工人们无能为力，只能看着浓烟。男主最终在雪地中看着废墟，决定为女儿手造一台钢的琴。"
        return simulated_context

class MediaAnalyzer:
    def __init__(self, ffmpeg_bin: str = "ffmpeg", ffprobe_bin: str = "ffprobe"):
        self.ffmpeg_bin = ffmpeg_bin
        self.ffprobe_bin = ffprobe_bin

    def _run_shell(self, command: str) -> subprocess.CompletedProcess:
        return subprocess.run(command, shell=True, capture_output=True, text=True)

    def probe_media(self, source_path: str) -> dict:
        source = shlex.quote(str(source_path))
        cmd = f"{self.ffprobe_bin} -v error -show_format -show_streams {source} -print_format json"
        proc = self._run_shell(cmd)
        if proc.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {proc.stderr.strip()}")
        return json.loads(proc.stdout)

    def _openai_client(self) -> OpenAI:
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
        if not api_key:
            raise RuntimeError("LLM_API_KEY 未设置，无法执行音频转录。")
        return OpenAI(api_key=api_key, base_url=base_url)

    def transcribe_audio(self, source_path: str, language: str = "zh") -> str:
        source = shlex.quote(str(source_path))
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name

        command = (
            f"{self.ffmpeg_bin} -y -i {source} -vn -ac 1 -ar 16000 -acodec pcm_s16le {shlex.quote(wav_path)}"
        )
        proc = self._run_shell(command)
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg audio extraction failed: {proc.stderr.strip()}")

        client = self._openai_client()
        try:
            with open(wav_path, "rb") as f:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language=language,
                )
            return result.text if hasattr(result, "text") else result["text"]
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

    def _extract_frame(self, source_path: str, timestamp: float, output_path: str) -> bool:
        source = shlex.quote(str(source_path))
        output = shlex.quote(str(output_path))
        command = (
            f"{self.ffmpeg_bin} -y -ss {timestamp} -i {source} -frames:v 1 -q:v 2 {output}"
        )
        proc = self._run_shell(command)
        return proc.returncode == 0

    def _compute_frame_metrics(self, frame_path: str) -> dict:
        with Image.open(frame_path) as img:
            img = img.convert("RGB")
            stat = ImageStat.Stat(img)
            brightness = sum(stat.mean) / len(stat.mean)
            contrast = sum(stat.stddev) / len(stat.stddev) if any(stat.stddev) else 0.0
            colors = img.getcolors(maxcolors=1000000) or []
            dominant_color = colors[0][1] if colors else (0, 0, 0)
            return {
                "brightness": round(brightness, 2),
                "contrast": round(contrast, 2),
                "dominant_color_rgb": dominant_color,
                "width": img.width,
                "height": img.height,
            }

    def analyze_shots(self, source_path: str, scene_times: list, transcript: str | None = None,
                      max_shots: int = 10) -> dict:
        metadata = self.probe_media(source_path)
        duration = float(metadata.get("format", {}).get("duration", 0.0))
        if not scene_times:
            scene_times = [0.0]

        shots = []
        temp_dir = Path(tempfile.mkdtemp(prefix="shot_analysis_"))
        try:
            for index, start in enumerate(scene_times[:max_shots]):
                end = scene_times[index + 1] if index + 1 < len(scene_times) else duration
                if end <= start:
                    end = min(start + 1.0, duration)
                frame_time = start + min(1.0, max(0.0, end - start) / 2.0)
                frame_path = temp_dir / f"shot_{index + 1}.jpg"
                self._extract_frame(source_path, frame_time, str(frame_path))
                metrics = self._compute_frame_metrics(str(frame_path)) if frame_path.exists() else {}
                shots.append({
                    "shot_index": index + 1,
                    "start_time": round(start, 3),
                    "end_time": round(end, 3),
                    "duration": round(end - start, 3),
                    "frame_sample_time": round(frame_time, 3),
                    "frame_metrics": metrics,
                })

            return {
                "duration": duration,
                "scene_count": len(scene_times),
                "analyzed_shots": shots,
                "audio_transcript_preview": transcript[:1000] if transcript else None,
                "summary": (
                    f"共检测到 {len(scene_times)} 个镜头点，分析前 {len(shots)} 个关键镜头。"
                    f"平均镜头时长 {round(duration / max(1, len(scene_times)), 2)} 秒。"
                    f"{ '已包含音频转录摘要。' if transcript else '未提供音频转录。'}"
                )
            }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def detect_scenes(self, source_path: str, threshold: float = 0.35, max_scenes: int = 40) -> list:
        source = shlex.quote(str(source_path))
        command = (
            f"{self.ffprobe_bin} -v error -f lavfi -i \"movie={source},select=gt(scene\\,{threshold})\" "
            "-show_entries frame=pkt_pts_time -of csv=p=0"
        )
        proc = self._run_shell(command)
        if proc.returncode != 0:
            return []
        times = []
        for line in proc.stdout.splitlines():
            if not line.strip():
                continue
            try:
                times.append(float(line.strip()))
            except ValueError:
                continue
            if len(times) >= max_scenes:
                break
        return times

    def detect_silence(self, source_path: str, silence_thresh: str = "-40dB", duration: float = 0.5) -> list:
        source = shlex.quote(str(source_path))
        command = (
            f"{self.ffmpeg_bin} -hide_banner -nostats -i {source} -af silencedetect=noise={silence_thresh}:d={duration} -f null -"
        )
        proc = self._run_shell(command)
        silence_starts = []
        silence_ranges = []
        for line in proc.stderr.splitlines():
            if "silence_start:" in line:
                start = float(line.split("silence_start:")[-1].strip())
                silence_starts.append(start)
            elif "silence_end:" in line:
                parts = line.split("silence_end:")[-1].strip().split("|")
                end = float(parts[0].strip())
                silence_ranges.append(end)
        ranges = []
        for idx, start in enumerate(silence_starts):
            end = silence_ranges[idx] if idx < len(silence_ranges) else None
            ranges.append({"start": start, "end": end})
        return ranges

    def build_context(self, source_path: str, metadata: dict, scene_changes: list, silence_ranges: list) -> str:
        source = Path(source_path)
        format_info = metadata.get("format", {})
        streams = metadata.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio = next((s for s in streams if s.get("codec_type") == "audio"), {})

        duration = float(format_info.get("duration", 0.0))
        width = video.get("width")
        height = video.get("height")
        fps = self._parse_frame_rate(video.get("r_frame_rate"))
        channels = audio.get("channels")
        sample_rate = audio.get("sample_rate")

        context = [
            f"媒体文件: {source.name}",
            f"路径: {source.resolve()}",
            f"时长: {self._format_duration(duration)}", 
            f"视频分辨率: {width}x{height}",
            f"视频帧率: {fps:.2f} fps", 
            f"音频通道: {channels}",
            f"采样率: {sample_rate} Hz",
            f"检测到场景切换点: {len(scene_changes)} 个（前 10 个: {[self._format_duration(s) for s in scene_changes[:10]]}）",
            f"检测到静音区: {len(silence_ranges)} 个（前 5 个: {[self._format_silence(r) for r in silence_ranges[:5]]}）",
        ]
        return "\n".join(context)

    def _parse_frame_rate(self, value: str) -> float:
        if not value or value == "0/0":
            return 24.0
        parts = value.split("/")
        if len(parts) == 2 and float(parts[1]) != 0:
            return float(parts[0]) / float(parts[1])
        return float(value)

    def _format_duration(self, seconds: float) -> str:
        if seconds is None:
            return "00:00:00"
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _format_silence(self, silence: dict) -> str:
        start = self._format_duration(silence.get("start", 0.0))
        end = self._format_duration(silence.get("end", 0.0)) if silence.get("end") is not None else "?"
        return f"{start} - {end}"
