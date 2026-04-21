# Quick Tour

Musubi-scrape is a Python library for crawling websites and extracting text content to build domain-specific datasets for LLM training. It handles the two hardest parts of web crawling at scale: navigating diverse site architectures to collect article links, and accurately extracting clean text from those pages.

This tour covers the three main ways to use the library: the `Pipeline` high-level API, the low-level crawl classes, and the AI agent layer.

---

## Installation

```bash
pip install musubi-scrape
```

---

## Pipeline (recommended starting point)

`Pipeline` orchestrates the full crawl in two stages — link discovery then content extraction — and manages a website config registry so you can re-crawl or update sites later.

### Crawling a new website

Use `pipeline()` to register a site and crawl it in one call. You need to inspect the target site first to find the right HTML block and URL pattern.

```python
from musubi import Pipeline

pipeline = Pipeline(website_config_path="config/websites.json")

pipeline.pipeline(
    dir_="Literary_Hub",           # folder name for output files
    name="Craft and Criticism",    # subfolder / category name
    class_="English",              # data class label
    prefix="https://lithub.com/category/craftandcriticism/page/",
    pages=5,                       # number of pages to crawl
    block1=["div", "post-list-item"],  # [html_tag, css_class] for article links
    implementation="scan",         # pagination strategy
    async_=True,                   # use async crawler
)
```

**`implementation` options:**

| Value | When to use |
|-------|-------------|
| `"scan"` | Standard paginated site (`?page=1`, `/page/2`, etc.) |
| `"scroll"` | Infinite-scroll (JavaScript loads more content on scroll) |
| `"click"` | "Load More" button or JS pagination buttons |
| `"onepage"` | All links are on a single static page |

**URL pagination pattern** — set `prefix` to the URL up to the page number. If the page number appears in the middle (e.g., `/page/2?category=news`), pass the trailing part as `suffix`:

```python
prefix="https://example.com/news/page/",
suffix="?lang=en",
# → crawls: https://example.com/news/page/1?lang=en, /page/2?lang=en, ...
```

If links on the page are relative paths (e.g., `/articles/foo`), pass the domain as `root_path`:

```python
root_path="https://example.com",
```

### Re-crawling by index

Once a site is registered in `websites.json`, crawl it by its index:

```python
pipeline = Pipeline(website_config_path="config/websites.json")
pipeline.start_by_idx(idx=0, update_pages=10)
```

### Crawling all registered sites

```python
pipeline.start_all(start_idx=0, update_pages=20)
```

---

## Low-level crawl classes

Use these directly when you want more control over each stage.

### Stage 1 — Link crawling

```python
from musubi import Scan

scanner = Scan(
    prefix="https://lithub.com/category/craftandcriticism/page/",
    pages=5,
    block1=["div", "post-list-item"],
    url_path="crawler/lithub/craft_links.json",
)

# Preview the first result before committing to a full crawl
scanner.check_link_result()

# Run the full crawl
scanner.crawl_link()
```

For infinite-scroll sites, use `Scroll`; for "Load More" buttons, use `Click` and pass the button selector as `block2`:

```python
from musubi import Click

clicker = Click(
    prefix="https://example.com/articles",
    pages=10,                                # number of button clicks
    block1=["article", "post"],              # article link container
    block2=["button", "load-more-btn"],      # "Load More" button
    url_path="crawler/example/links.json",
)
clicker.crawl_link()
```

### Stage 2 — Content crawling

```python
from musubi import Crawl

crawler = Crawl(url_path="crawler/lithub/craft_links.json")

# Preview one article
crawler.check_content_result()

# Crawl and save all articles as JSONL
crawler.crawl_contents(save_path="data/English/lithub/craft.json")
```

---

## AI Agent (auto-discover crawl parameters)

If you don't want to inspect the HTML yourself, `PipelineAgent` uses an LLM to browse the target site and determine the right selectors and URL pattern automatically.

```python
from musubi.agent import PipelineAgent
from musubi.agent.actions import (
    search_url,
    analyze_website,
    get_container,
    get_page_info,
    final_answer,
)

agent = PipelineAgent(
    actions=[search_url, analyze_website, get_container, get_page_info, final_answer],
    model_source="anthropic",   # or "openai", "groq", "gemini"
)

agent.execute("Scrape all articles from the Craft and Criticism section of Literary Hub.")
```

Set your API key first:

```bash
musubi env --anthropic <your-key>
# or
export ANTHROPIC_API_KEY=<your-key>
```

---

## Output format

Both `Pipeline` and `Crawl` save content as JSONL, one article per line:

```json
{"url": "https://lithub.com/...", "text": "# Title\n\nArticle body in markdown..."}
```

Link files (`*_link.json`) are plain JSON lists of URLs:

```json
["https://lithub.com/article-one/", "https://lithub.com/article-two/", ...]
```

---

## CLI

All functionality is also available from the command line after installation:

```bash
# Register and crawl a new site
musubi pipeline --dir_ Literary_Hub --name "Craft and Criticism" \
  --class_ English --prefix "https://lithub.com/category/craftandcriticism/page/" \
  --pages 5 --block1 '["div","post-list-item"]' --implementation scan

# Crawl by index
musubi start-by-idx --idx 0

# Crawl all registered sites
musubi start-all --website_config_path config/websites.json --update-pages 20

# Run an agent
musubi agent --prompt "Scrape Literary Hub Craft and Criticism" \
  --model_source anthropic --model_type claude-sonnet-4-6
```
