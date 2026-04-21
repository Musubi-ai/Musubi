# Installation

## Requirements

- Python >= 3.9

## Install from PyPI

```bash
pip install musubi-scrape
```

## Install from source

To use the latest features before an official release:

```bash
pip install git+https://github.com/Musubi-ai/Musubi.git
```

Or clone and install locally:

```bash
git clone https://github.com/Musubi-ai/Musubi.git
cd Musubi
pip install -e .
```

## Verify installation

```python
from musubi import Pipeline, Crawl
```

---

## Environment variables

Musubi reads API keys and credentials from a `.env` file in your working directory. Copy `example.env` to `.env` and fill in the keys you need:

```bash
cp example.env .env
```

```bash
# Required only for AI agent features
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=
XAI_API_KEY=
DEEPSEEK_API_KEY=

# Required only for agent's Google Search tool
GOOGLE_SEARCH_API=
GOOGLE_ENGINE_ID=

# Required only for scheduler Gmail notifications
GOOGLE_APP_PASSWORD=

# Required only for uploading datasets to HuggingFace
HF_TOKEN=
```

You can also set keys via the CLI instead of editing `.env` manually:

```bash
musubi env --openai YOUR_KEY
musubi env --anthropic YOUR_KEY
```

---

## Optional dependencies

To run the test suite:

```bash
pip install musubi-scrape[test]
pytest
```

---

## Selenium setup

The `scroll` and `click` crawling methods use Selenium with a Chrome WebDriver. Make sure [Google Chrome](https://www.google.com/chrome/) is installed — `selenium` will manage the ChromeDriver automatically.
