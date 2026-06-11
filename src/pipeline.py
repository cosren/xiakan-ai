import json
import os
from src.utils.fetcher import MovieDetailFetcher

class XiakanPipelineEngine:
    def __init__(self, llm_client):
        """
        llm_client 应当对齐您当前 github 仓库中已有的大模型调用实例（例如 OpenAI/Gemini 封装）
        """
        self.llm = llm_client
        self.skills_dir = "skills/xiakan"

    def _get_prompt(self, filename: str) -> str:
        with open(os.path.join(self.skills_dir, filename), "r", encoding="utf-8") as f:
            return json.load(f)["system_prompt"]

    def generate_script(self, title: str, source_video: str | None = None, media_context: str | None = None) -> dict:
        context = MovieDetailFetcher().fetch_by_title(title)
        if source_video:
            context += f"\n源视频路径: {source_video}\n"
        if media_context:
            context += f"\n媒体分析上下文:\n{media_context}\n"

        print("[Script] ⚙️ 正在生成文字解说稿...")
        char_prompt = self._get_prompt("character.json")
        characters = self.llm.ask(system=char_prompt, prompt=context)

        narrative_prompt = self._get_prompt("narrative.json")
        subverted_plot = self.llm.ask(system=narrative_prompt, prompt=f"原图景: {context}\n重构角色: {characters}")

        deadpan_prompt = self._get_prompt("deadpan.json")
        final_script = self.llm.ask(system=deadpan_prompt, prompt=subverted_plot)

        return {
            "title": title,
            "source_video": source_video,
            "raw_script": final_script,
            "characters": characters,
            "subverted_plot": subverted_plot,
        }

    def process_factory(self, title: str) -> list:
        # 1. 深度抓取
        context = MovieDetailFetcher().fetch_by_title(title)

        # 2. 链式调用 LLM (Chain of Thought)
        print("[Factory] ⚙️ 正在执行阶段 1：注入 [Character_Profiler] 转换人物...")
        char_prompt = self._get_prompt("character.json")
        characters = self.llm.ask(system=char_prompt, prompt=context) # 假设 ask 是您仓库里的基础方法

        print("[Factory] ⚙️ 正在执行阶段 2：注入 [Narrative_Subversion] 置换时空...")
        narrative_prompt = self._get_prompt("narrative.json")
        subverted_plot = self.llm.ask(system=narrative_prompt, prompt=f"原图景: {context}\n重构角色: {characters}")

        print("[Factory] ⚙️ 正在执行阶段 3：注入 [Deadpan_Linguistic] 雕刻冷面滑稽文本（进行文本3倍扩写）...")
        deadpan_prompt = self._get_prompt("deadpan.json")
        final_script = self.llm.ask(system=deadpan_prompt, prompt=subverted_plot)

        print("[Factory] ⚙️ 正在执行阶段 4：注入 [Audio_Visual_Director] 编排卡点JSON...")
        director_prompt = self._get_prompt("director.json")
        
        schema_instruction = "请必须输出标准的JSON数组，不允许包含任何 Markdown 代码块包裹（如 ```json）。" \
                             "数组内每个元素必须包含字段: [timestamp, voiceover, bgm_selection, bgm_action, video_effect]。\n" \
                             f"待处理文本：\n{final_script}"
                             
        raw_json_timeline = self.llm.ask(system=director_prompt, prompt=schema_instruction)

        # 3. 严格的 JSON 稳定性清洗器 (Sanitizer)
        try:
            # 清理可能存在的代码块残留
            clean_json = raw_json_timeline.replace("```json", "").replace("```", "").strip()
            timeline_data = json.loads(clean_json)
            return timeline_data
        except json.JSONDecodeError:
            print("[Error] AI未按标准Schema输出，启动强制降级适配...")
            return [{"timestamp": "00:00", "voiceover": final_script, "bgm_selection": "爱的供养", "bgm_action": "Play", "video_effect": "None"}]

    def analyze_video_frames(self, frame_descriptions: str) -> dict:
        """Skill 1.5: Video Analyzer — 拉片分析师与视觉喜剧潜力挖掘机"""
        print("[Analyzer] 🎬 正在分析视频画面的喜剧潜力...")
        analyzer_prompt = self._get_prompt("video_analyzer.json")
        
        analysis_task = f"请根据以下画面描述，评估每个画面的喜剧潜力和可利用的细节：\n\n{frame_descriptions}"
        analysis_result = self.llm.ask(system=analyzer_prompt, prompt=analysis_task)
        
        try:
            clean_result = analysis_result.replace("```json", "").replace("```", "").strip()
            analysis_data = json.loads(clean_result)
            return {
                "analysis": analysis_data,
                "summary": f"共识别出 {len(analysis_data) if isinstance(analysis_data, list) else 1} 个喜剧潜力点"
            }
        except json.JSONDecodeError:
            return {"analysis": analysis_result, "summary": "分析结果已生成（非结构化）"}

    def generate_music_cues(self, script_text: str) -> dict:
        """Skill 4: Music Matcher — 曲库选梗与卡点音频总监"""
        print("[Music] 🎵 正在生成音乐卡点与反差配乐方案...")
        music_prompt = self._get_prompt("music_matcher.json")
        
        music_task = f"根据以下解说词，生成精确的音乐卡点与反差配乐方案：\n\n{script_text}"
        music_result = self.llm.ask(system=music_prompt, prompt=music_task)
        
        try:
            clean_result = music_result.replace("```json", "").replace("```", "").strip()
            music_data = json.loads(clean_result)
            return {
                "music_cues": music_data if isinstance(music_data, list) else [music_data],
                "summary": "音乐卡点方案已生成"
            }
        except json.JSONDecodeError:
            return {"music_cues": music_result, "summary": "音乐方案已生成（非结构化）"}

    def generate_pacing_plan(self, script_text: str, duration: float) -> dict:
        """Skill 5: Pacing Cutter — 节奏大师与反套路剪辑设计"""
        print("[Pacing] ⏱️ 正在生成节奏控制与卡点剪辑方案...")
        pacing_prompt = self._get_prompt("pacing_cutter.json")
        
        pacing_task = f"根据以下解说词（时长约 {duration} 秒），生成精确的节奏控制与卡点剪辑方案：\n\n{script_text}"
        pacing_result = self.llm.ask(system=pacing_prompt, prompt=pacing_task)
        
        try:
            clean_result = pacing_result.replace("```json", "").replace("```", "").strip()
            pacing_data = json.loads(clean_result)
            return {
                "pacing_plan": pacing_data if isinstance(pacing_data, list) else [pacing_data],
                "summary": "节奏卡点方案已生成"
            }
        except json.JSONDecodeError:
            return {"pacing_plan": pacing_result, "summary": "节奏方案已生成（非结构化）"}

    def generate_epilogue(self, script_core: str) -> dict:
        """Skill 6: Satirical Epilogue — 毒鸡汤编织与虚无主义升华"""
        print("[Epilogue] 🎭 正在生成毒鸡汤结尾与现实讽刺升华...")
        epilogue_prompt = self._get_prompt("satirical_epilogue.json")
        
        epilogue_task = f"根据以下视频核心内容，生成一段毒鸡汤结尾与现实讽刺升华：\n\n{script_core}"
        epilogue_result = self.llm.ask(system=epilogue_prompt, prompt=epilogue_task)
        
        try:
            clean_result = epilogue_result.replace("```json", "").replace("```", "").strip()
            epilogue_data = json.loads(clean_result)
            return {
                "epilogue": epilogue_data,
                "summary": "毒鸡汤结尾已生成"
            }
        except json.JSONDecodeError:
            return {"epilogue": {"raw_text": epilogue_result}, "summary": "结尾文案已生成（非结构化）"}
