# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Musubi (`musubi-scrape`) is a Python library for crawling websites and extracting text content to build domain-specific datasets for LLM training. It supports sync/async crawling, Selenium-based JS rendering, PDF extraction, and an AI agent layer that auto-discovers crawl parameters.

## Commands

**Install dependencies:**
```bash
uv sync
# or
poetry install
```

**Run tests:**
```bash
pytest
# single test file:
pytest tests/test_pipeline.py
```

**Build the package:**
```bash
hatchling build
```

**Build documentation:**
```bash
cd docs && make html
```

**Set API keys via CLI:**
```bash
musubi env --openai <key> --anthropic <key>
```

**Upload datasets to HuggingFace:**
```bash
./scripts/upload_data.sh <hf-repo-name>
./scripts/upload_links.sh <hf-repo-name>
```

## Architecture

### Two-stage crawl pipeline

**Stage 1 — Link crawling** (`musubi/crawl_link.py`, `musubi/async_crawl_link.py`):
Discovers article URLs from a site. Four strategies: `Scan` (paginated requests), `AsyncScan` (concurrent aiohttp, up to 30), `Scroll` (Selenium infinite scroll), `Click` (Selenium pagination buttons). Output: `crawler/<site>/*_link.json`.

**Stage 2 — Content crawling** (`musubi/crawl_content.py`, `musubi/async_crawl_content.py`):
Fetches each URL and extracts text. Uses `trafilatura` for HTML→markdown, `PyMuPDF` for PDFs, BeautifulSoup for image-text pairs. Output: `data/<class>/<site>/*.json`.

**Orchestration** (`musubi/pipeline.py`):
`Pipeline` class reads `config/websites.json` (JSONL registry of hundreds of sites), selects the right crawlers per entry, and manages the full flow. `start_all()` / `start_by_idx()` are the main entry points.

### AI Agent layer (`musubi/agent/`)

`MusubiAgent` routes to one of three sub-agents:
- `PipelineAgent` — auto-discovers crawl parameters (URL patterns, CSS selectors, pagination) by browsing the target site using tools: `search_url`, `analyze_website`, `get_container`, `get_page_info`, `final_answer`
- `GeneralAgent` — batch-updates existing website configs: `domain_analyze`, `implementation_analyze`, `update_all/by_idx`, `upload`, `delete`
- `SchedulerAgent` — controls the scheduler server via HTTP: `launch/shutdown/check/add/pause/resume/remove`

All agents follow a **Thought → `<action>` tag → execute → Observation** loop. LLM backends are in `musubi/agent/models.py` (OpenAI, Anthropic, Groq, Gemini, HuggingFace, xAI — all implement `BaseModel` ABC).

### Scheduler layer (`musubi/scheduler/`)

A FastAPI + APScheduler server running on `127.0.0.1:5000`. `Controller` is the HTTP client. Tasks are cron-defined in `config/tasks.json`. Gmail notifications fire on task start/finish via `GOOGLE_APP_PASSWORD`.

### Key config files

| File | Purpose |
|------|---------|
| `config/websites.json` | Production site registry (JSONL, ~380KB, hundreds of sites) |
| `config/tasks.json` | Scheduler task definitions |
| `.env` | API keys — `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_APP_PASSWORD`, `HF_TOKEN` |
| `example.env` | Template for `.env` |

### Output directories (gitignored)

- `crawler/<site>/` — discovered URL lists (`*_link.json`)
- `data/<class>/<site>/` — extracted article content JSON
- `imgtxt_crawler/` — image-text pair results
- `logs/` — runtime logs

## Package entry points

The CLI (`musubi`) is registered in `pyproject.toml` under `[project.scripts]`. Key subcommands: `pipeline`, `agent`, `start-all`, `start-by-idx`, `crawl-link`, `crawl-content`, `analyze`, `get`, `env`.

Public API exported from `musubi/__init__.py`: `Crawl`, `Pipeline`, and all `crawl_link` classes.
