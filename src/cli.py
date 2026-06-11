import click
import json
import os
import sys
from pathlib import Path
from src.install import Installer
from src.utils.llm_client import XiakanLLMClient
from src.utils.material_library import MaterialLibrary
from src.utils.narrator_cli import NarratorAICLI
from src.utils.fetcher import MediaAnalyzer
from src.pipeline import XiakanPipelineEngine
from src.auto_editor import AutoEditor
from src.script_generator import ScriptGenerator

@click.group()
def cli():
    pass

@cli.command(name="verify")
@click.option('--narrator', is_flag=True, default=False, help='同时验证 narrator-ai-cli 可用性')
def verify_api(narrator):
    """
    提供给 OpenClaw 安装生命周期调用的 API 验证通道
    """
    click.echo("🔄 正在验证大模型 API 连接有效性...")
    client = XiakanLLMClient()
    llm_ok = client.validate_connection()

    narrator_ok = True
    if narrator:
        click.echo("🔄 正在验证 narrator-ai-cli 可执行命令...")
        narrator_ok = NarratorAICLI().is_installed()
        if narrator_ok:
            click.secho("✅ narrator-ai-cli 已安装且可用。", fg="green")
        else:
            click.secho("❌ narrator-ai-cli 未找到，请先安装 narrator-ai-cli 并确保它在 PATH 中。", fg="red")

    if llm_ok and narrator_ok:
        click.secho("✅ 验证通过，内容工厂准备就绪！", fg="green")
        sys.exit(0)
    else:
        click.secho("❌ 验证失败，请检查配置。", fg="red")
        sys.exit(1)

@cli.command(name="setup")
def setup():
    """安装并验证 Skill 运行所需依赖。"""
    installer = Installer()
    success = installer.setup()
    if not success:
        sys.exit(1)

@cli.command(name="xiakan")
@click.option('--title', required=True, type=str, help='电影/电视剧名称')
@click.option('--out', default='./dist/timeline.json', type=str, help='输出 JSON 路径')
def xiakan_factory(title, out):
    click.secho(f"🚀 《瞎看什么》内容制造工厂正在排产...", fg="cyan", bold=True)
    llm_client = XiakanLLMClient()
    engine = XiakanPipelineEngine(llm_client)
    structured_data = engine.process_factory(title)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    click.secho(f"🎉 脚本已成功导出至：{out}", fg="green", bold=True)

@cli.command(name="generate-script")
@click.option('--title', required=True, type=str, help='电影/项目标题')
@click.option('--source', default=None, type=str, help='可选源视频文件路径')
@click.option('--out', default='./dist/script.txt', type=str, help='输出解说稿路径')
def generate_script(title, source, out):
    click.secho(f"📄 正在生成文字解说稿...", fg="cyan", bold=True)
    llm_client = XiakanLLMClient()
    generator = ScriptGenerator(llm_client)
    script_data = generator.generate_text_script(title, source)
    script_text = script_data.get('raw_script', '')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(script_text)

    click.secho(f"✅ 解说稿已生成：{out}", fg="green", bold=True)
    click.echo(script_text)

@cli.command(name="transcribe-audio")
@click.option('--source', required=True, type=str, help='视频或音频文件路径')
@click.option('--out', default='./dist/transcript.txt', type=str, help='输出转录文本路径')
def transcribe_audio(source, out):
    click.secho(f"🎧 正在识别音频并转录文本...", fg="cyan", bold=True)
    analyzer = MediaAnalyzer()
    transcript = analyzer.transcribe_audio(source)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(transcript)

    click.secho(f"✅ 转录结果已保存：{out}", fg="green", bold=True)
    click.echo(transcript)

@cli.command(name="analyze-shots")
@click.option('--source', required=True, type=str, help='视频文件路径')
@click.option('--out', default='./dist/shot_analysis.json', type=str, help='输出镜头分析结果路径')
@click.option('--max-shots', default=8, type=int, help='分析关键镜头数量')
def analyze_shots(source, out, max_shots):
    click.secho(f"🎬 正在分析镜头结构与画面语言...", fg="cyan", bold=True)
    analyzer = MediaAnalyzer()
    scene_changes = analyzer.detect_scenes(source)
    transcript = analyzer.transcribe_audio(source)
    shot_analysis = analyzer.analyze_shots(source, scene_changes, transcript=transcript, max_shots=max_shots)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(shot_analysis, f, ensure_ascii=False, indent=2)

    click.secho(f"✅ 镜头分析已保存：{out}", fg="green", bold=True)
    click.echo(json.dumps(shot_analysis, ensure_ascii=False, indent=2))

@cli.command(name="generate-music")
@click.option('--script', required=True, type=str, help='解说稿文件路径或直接文本')
@click.option('--out', default='./dist/music_cues.json', type=str, help='输出音乐卡点方案路径')
def generate_music(script, out):
    click.secho(f"🎵 正在生成反差配乐与精确卡点方案...", fg="cyan", bold=True)
    llm_client = XiakanLLMClient()
    engine = XiakanPipelineEngine(llm_client)
    
    script_text = script if len(script) > 100 else Path(script).read_text(encoding='utf-8')
    music_plan = engine.generate_music_cues(script_text)
    
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(music_plan, f, ensure_ascii=False, indent=2)

    click.secho(f"✅ 音乐方案已保存：{out}", fg="green", bold=True)
    click.echo(json.dumps(music_plan, ensure_ascii=False, indent=2))

@cli.command(name="generate-pacing")
@click.option('--script', required=True, type=str, help='解说稿文件路径或直接文本')
@click.option('--duration', default=600.0, type=float, help='视频时长（秒）')
@click.option('--out', default='./dist/pacing_plan.json', type=str, help='输出节奏方案路径')
def generate_pacing(script, duration, out):
    click.secho(f"⏱️ 正在生成极限节奏与卡点剪辑方案...", fg="cyan", bold=True)
    llm_client = XiakanLLMClient()
    engine = XiakanPipelineEngine(llm_client)
    
    script_text = script if len(script) > 100 else Path(script).read_text(encoding='utf-8')
    pacing_plan = engine.generate_pacing_plan(script_text, duration)
    
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(pacing_plan, f, ensure_ascii=False, indent=2)

    click.secho(f"✅ 节奏方案已保存：{out}", fg="green", bold=True)
    click.echo(json.dumps(pacing_plan, ensure_ascii=False, indent=2))

@cli.command(name="generate-epilogue")
@click.option('--core', required=True, type=str, help='视频核心内容或脚本摘要')
@click.option('--out', default='./dist/epilogue.json', type=str, help='输出结尾方案路径')
def generate_epilogue(core, out):
    click.secho(f"🎭 正在生成毒鸡汤结尾与现实讽刺升华...", fg="cyan", bold=True)
    llm_client = XiakanLLMClient()
    engine = XiakanPipelineEngine(llm_client)
    
    epilogue = engine.generate_epilogue(core)
    
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(epilogue, f, ensure_ascii=False, indent=2)

    click.secho(f"✅ 结尾方案已保存：{out}", fg="green", bold=True)
    click.echo(json.dumps(epilogue, ensure_ascii=False, indent=2))

@cli.command(name="auto-edit")
@click.option('--source', required=True, type=str, help='原始电影视频文件路径')
@click.option('--title', required=True, type=str, help='影片名称或项目标题')
@click.option('--bgm', default=None, type=str, help='可选背景音乐文件路径')
@click.option('--project', default='./dist/shotcut_project.mlt', type=str, help='输出 Shotcut 工程文件路径')
def auto_edit(source, title, bgm, project):
    click.secho(f"🚀 正在生成自动剪辑脚本与 Shotcut 工程文件...", fg="cyan", bold=True)
    llm_client = XiakanLLMClient()
    editor = AutoEditor(llm_client)
    edit_plan = editor.create_edit_script(source, title, bgm_name=bgm)
    metadata = edit_plan.get('metadata', {})
    timeline = edit_plan.get('timeline', [])
    project_path = editor.export_shotcut_project(source, timeline, metadata, project, bgm_path=bgm)

    with open(project_path + '.json', 'w', encoding='utf-8') as f:
        json.dump(edit_plan, f, ensure_ascii=False, indent=2)

    click.secho(f"✅ 自动剪辑工程已生成：{project_path}", fg="green", bold=True)
    click.secho(f"ℹ️ 详细计划已保存：{project_path}.json", fg="green")

@cli.command(name="list-materials")
@click.option('--page', default=1, type=int, help='分页页码')
@click.option('--size', default=50, type=int, help='每页条目数')
def list_materials(page, size):
    library = MaterialLibrary()
    items = library.list_local(page=page, size=size)
    click.echo(json.dumps(items, ensure_ascii=False, indent=2))

@cli.command(name="search-materials")
@click.option('--query', required=True, type=str, help='网络素材搜索关键词')
@click.option('--api_url', default=None, type=str, help='可选网络素材搜索 API')
def search_materials(query, api_url):
    library = MaterialLibrary()
    try:
        results = library.search_network(query, api_url=api_url)
        click.echo(json.dumps(results, ensure_ascii=False, indent=2))
    except Exception as exc:
        click.secho(f"❌ 网络素材搜索失败：{exc}", fg="red")
        sys.exit(1)

@cli.command(name="download-material")
@click.option('--url', required=True, type=str, help='素材下载地址')
@click.option('--dest', default=None, type=str, help='下载保存路径')
def download_material(url, dest):
    library = MaterialLibrary()
    try:
        path = library.download_material(url, dest=dest)
        click.secho(f"✅ 素材已下载：{path}", fg="green")
    except Exception as exc:
        click.secho(f"❌ 下载失败：{exc}", fg="red")
        sys.exit(1)

@cli.command(name="narrator-materials")
@click.option('--page', default=1, type=int, help='分页页码')
@click.option('--size', default=50, type=int, help='每页条目数')
def narrator_materials(page, size):
    """使用 narrator-ai-cli 列出内置电影素材。"""
    narrator = NarratorAICLI()
    if not narrator.is_installed():
        click.secho("❌ narrator-ai-cli 未安装，请先安装 narrator-ai-cli。", fg="red")
        sys.exit(1)

    click.secho("🔎 正在读取 narrator-ai-cli 内置素材列表...", fg="cyan")
    try:
        result = narrator.run_json(["material", "list", "--page", str(page), "--size", str(size)])
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        click.secho(f"❌ 读取素材失败：{exc}", fg="red")
        sys.exit(1)

if __name__ == '__main__':
    cli()

if __name__ == '__main__':
    cli()