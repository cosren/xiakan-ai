# 🧠 Narrator AI CLI Skill + Xiakan Content Factory

[中文文档](README_CN.md)

> This repository combines an AI agent skill for `narrator-ai-cli` with a `xiakan-content-factory` command plugin. It supports both movie narration workflow orchestration and creative script/timeline generation.

## What is this?

A combined package with two main capabilities:

- **`narrator-ai-cli-skill`**: a skill description (`SKILL.md`) that teaches AI agents how to use `narrator-ai-cli` for automated movie narration video production.
- **`xiakan-content-factory`**: a CLI plugin module under `src/` that generates high-density storytelling scripts and structured timeline JSON for `瞎看什么` style content.

```
You say: "Create a narration video for Pegasus in a comedy style"

AI executes: Search movie → Select template → Choose BGM → Pick voice → Generate script → Compose video → Return download link
```

### How CLI and Skill work together

| | CLI (command-line tool) | Skill (capability description) |
|---|---|---|
| **What it is** | A set of executable commands | Instructions that teach AI how to use those commands |
| **Analogy** | Kitchen tools | A recipe book |
| **Works alone?** | Yes, in terminal manually | No, requires CLI |

In short: **CLI is the hands. Skill is the brain.** Together, the AI agent can produce videos end-to-end.

---

## Quick Start

### Step 1: Install the CLI tool

```bash
pip install "narrator-ai-cli @ git+https://github.com/NarratorAI-Studio/narrator-ai-cli.git"
```

> See [narrator-ai-cli](https://github.com/NarratorAI-Studio/narrator-ai-cli) for detailed installation options.

### Step 2: Configure API keys and environment

```bash
narrator-ai-cli config set app_key <your_app_key>
```

Set the content factory environment variables before using the Xiakan command:

```bash
export LLM_API_KEY=<your_llm_api_key>
export LLM_BASE_URL=https://api.deepseek.com/v1
export LLM_MODEL=deepseek-chat
export NARRATOR_APP_KEY=<your_app_key>
```

> 📧 Need an API key? Email **merlinyang@gridltd.com** or scan the QR code at the bottom of this page.

### Step 3: Install the Skill

The skill consists of `SKILL.md` **and** the `references/` directory — both are required. Clone the repo directly into your agent's skills folder:

**OpenClaw:**
```bash
mkdir -p ~/.openclaw/skills
git clone https://github.com/NarratorAI-Studio/narrator-ai-cli-skill.git \
  ~/.openclaw/skills/narrator-ai-cli
```

**Windsurf / Claude Code:**
```bash
mkdir -p /path/to/your/project/.skills
git clone https://github.com/NarratorAI-Studio/narrator-ai-cli-skill.git \
  /path/to/your/project/.skills/narrator-ai-cli
```

**Cursor:**
```bash
mkdir -p /path/to/your/project/.cursor/rules
git clone https://github.com/NarratorAI-Studio/narrator-ai-cli-skill.git \
  /path/to/your/project/.cursor/rules/narrator-ai-cli
```

**Any markdown-reading agent:**
```bash
mkdir -p /path/to/agent/skills
git clone https://github.com/NarratorAI-Studio/narrator-ai-cli-skill.git \
  /path/to/agent/skills/narrator-ai-cli
```

**CLI plugin usage:**
```bash
python3 -m src.cli setup
python3 -m src.cli verify --narrator
python3 -m src.cli generate-script --title "电影名称" --source ./movie.mp4 --out ./dist/script.txt
python3 -m src.cli transcribe-audio --source ./movie.mp4 --out ./dist/transcript.txt
python3 -m src.cli analyze-shots --source ./movie.mp4 --out ./dist/shot_analysis.json --max-shots 8
python3 -m src.cli auto-edit --source ./movie.mp4 --title "电影名称" --project ./dist/project.mlt
python3 -m src.cli list-materials --page 1 --size 50
python3 -m src.cli search-materials --query "都市 片段"
python3 -m src.cli download-material --url "https://example.com/media.mp4"
```

**WorkBuddy / QClaw (Tencent):**

Upload `SKILL.md` and the entire `references/` folder through the skill management UI, keeping the directory structure intact (`references/` must remain a subfolder alongside `SKILL.md` — do not flatten the files).

> 💡 **Tip**: To update the skill later, just run `git pull` inside the cloned directory.

### Step 4: Start talking!

Once installed, use natural language:

- "Create a narration video for The Shawshank Redemption"
- "Show me what movies are available"
- "Make 5 narration videos for different action movies"
- "Use a comedy template and generate a narration"

---

---

## Tested Platforms

| Platform | Setup | Status |
|----------|-------|--------|
| **OpenClaw** | `git clone` into skills directory | ✅ Verified |
| **Windsurf** | `git clone` into .skills directory | ✅ Verified |
| **WorkBuddy** (Tencent) | Upload SKILL.md + all files in references/ | ✅ Verified |
| **QClaw** (Tencent) | Upload SKILL.md + all files in references/ | ✅ Verified |
| **Youdao Lobster** | `git clone` into skills directory | ✅ Verified |
| **Yuanqi AI** | `git clone` into skills directory | ✅ Verified |
| **Claude Code** | `git clone` into project .skills directory | ✅ Verified |
| **Cursor** | `git clone` into .cursor/rules directory | ✅ Verified |
| Any markdown-skill agent | `git clone` repo, point agent to SKILL.md | ✅ Compatible |

---

## Capabilities

| Feature | Details |
|---------|---------|
| Two workflow paths | Adapted Narration and Original Narration |
| Three creation modes | Hot Drama / Original Mix / New Drama |
| Built-in resources | ~100 movies, 146 BGM tracks, 63 dubbing voices, 90+ narration templates |
| Full pipeline | Script → Clip data → Video composing → Visual template |
| Standalone tasks | Voice cloning, text-to-speech |
| Data flow mapping | Which output feeds into which input |
| Error handling | All 18 API error codes with recommended actions |
| Cost estimation | Budget verification before task creation |

### What's in SKILL.md

| Section | Description |
|---------|-------------|
| Frontmatter | Skill metadata (name, description, requirements) |
| Reference Index | Pointers to detailed lookup tables in `references/` (resources, workflows, magic-video, operations) |
| Pipeline at a Glance | ASCII diagram of Fast Path and Standard Path |
| Agent Rules | Mandatory rules: confirm before acting, language chain, polling pattern, etc. |
| Prerequisites | Assumes `narrator-ai-cli` is installed and `NARRATOR_APP_KEY` is set |
| Core Concepts | Key terms: file_id, task_id, task_order_num, etc. |
| Conversation Initiation | How to open a session and the decision sequence |
| Two Workflow Paths | Fast Path (Original Narration) vs Standard Path (Adapted Narration) |
| Resource Selection Protocol | BGM, dubbing, template selection order and rules |
| Fast Path | Steps 0–4 with parameter notes |
| Standard Path | Steps 0–5 with parameter notes |
| Standalone Tasks | Voice clone and TTS |
| Important Notes | 7 critical gotchas and best practices |
| Data & Privacy | API endpoint, file handling, credentials scope |

---

## Requirements

- **CLI**: narrator-ai-cli v1.0.0+
- **Python**: 3.10+
- **Dependencies**: typer, httpx[socks], httpx-sse, pyyaml, rich
- **API key**: Contact us to get one

## Links

- 📦 [narrator-ai-cli CLI repo](https://github.com/NarratorAI-Studio/narrator-ai-cli)
- 📖 [Resource preview (Feishu Docs)](https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc)
- 🦞 [OpenClaw agent framework](https://github.com/openclaw/openclaw)

## Contact

Need an API key or help?

- 📧 Email: merlinyang@gridltd.com
- 💬 WeChat: Scan the QR code below

![Contact us](imgs/contact.png)

## License

MIT
