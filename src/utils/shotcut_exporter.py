from pathlib import Path
from xml.sax.saxutils import escape


class ShotcutExporter:
    def __init__(self, source_video: str, bgm_path: str | None = None):
        self.source_video = Path(source_video)
        self.bgm_path = Path(bgm_path) if bgm_path else None

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def export(self, destination: str, timeline: list[dict], metadata: dict) -> None:
        project_path = Path(destination)
        video_id = "video_src"
        bgm_id = "bgm_src"
        playlist_id = "playlist0"
        tractor_id = "tractor0"

        src_path = escape(str(self.source_video.resolve()))
        bgm_path = escape(str(self.bgm_path.resolve())) if self.bgm_path else None

        width = metadata.get("width", 1920)
        height = metadata.get("height", 1080)
        frame_rate_num = int(metadata.get("frame_rate_num", 24000))
        frame_rate_den = int(metadata.get("frame_rate_den", 1001))
        sample_aspect_num = 1
        sample_aspect_den = 1
        display_aspect_num = width
        display_aspect_den = height

        producers = [
            f"  <producer id=\"{video_id}\">\n"
            f"    <property name=\"resource\">{src_path}</property>\n"
            f"  </producer>\n"
        ]

        entries = []
        for idx, item in enumerate(timeline, start=1):
            clip_id = f"clip_{idx}"
            in_time = self._format_time(item.get("source_start", item.get("segment_start", 0.0)))
            out_time = self._format_time(item.get("source_end", item.get("segment_end", 0.0)))
            producers.append(
                f"  <producer id=\"{clip_id}\">\n"
                f"    <property name=\"resource\">{src_path}</property>\n"
                f"    <property name=\"in\">{in_time}</property>\n"
                f"    <property name=\"out\">{out_time}</property>\n"
                f"  </producer>\n"
            )
            entries.append(f"    <entry producer=\"{clip_id}\"/>\n")

        if bgm_path:
            producers.append(
                f"  <producer id=\"{bgm_id}\">\n"
                f"    <property name=\"resource\">{bgm_path}</property>\n"
                f"  </producer>\n"
            )

        playlist_body = "".join(entries)
        tractor_body = "".join([f"    <track producer=\"{playlist_id}\"/>\n"])

        audio_track = ""
        if bgm_path:
            audio_track = (
                f"  <playlist id=\"playlist_bgm\">\n"
                f"    <entry producer=\"{bgm_id}\"/>\n"
                f"  </playlist>\n"
                f"  <tractor id=\"tractor_bgm\">\n"
                f"    <track producer=\"playlist_bgm\"/>\n"
                f"  </tractor>\n"
            )

        xml = [
            "<mlt version=\"7.0.0\">\n",
            f"  <profile width=\"{width}\" height=\"{height}\" progressive=\"1\" sample_aspect_num=\"{sample_aspect_num}\" sample_aspect_den=\"{sample_aspect_den}\" display_aspect_num=\"{display_aspect_num}\" display_aspect_den=\"{display_aspect_den}\" frame_rate_num=\"{frame_rate_num}\" frame_rate_den=\"{frame_rate_den}\" colorspace=\"709\"/>\n",
            "  <producer id=\"main\">\n",
            f"    <property name=\"resource\">{src_path}</property>\n",
            "  </producer>\n",
            f"  <playlist id=\"{playlist_id}\">\n",
            playlist_body,
            "  </playlist>\n",
            f"  <tractor id=\"{tractor_id}\">\n",
            tractor_body,
            "  </tractor>\n",
            audio_track,
            "</mlt>\n"
        ]

        project_path.parent.mkdir(parents=True, exist_ok=True)
        project_path.write_text("".join(xml), encoding="utf-8")
