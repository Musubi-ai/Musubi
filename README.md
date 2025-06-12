<p align="center">
    <br>
    <img src="assets\logo\FullLogo.png" width="600"/>
    <br>
</p>

<h1 align="center">Weaving connection to the world.🪢</h1>

<p align="center">
    <a href="https://github.com/blaze7451/Musubi/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/badge/license-Apache_2.0-blue
    "></a>
    <a href="https://github.com/Musubi-ai"><img alt="Team" src="https://img.shields.io/badge/Built%20by-Musubi%20Team-blue"></a>
</p>

Musubi is a Python library designed for efficiently crawling and extracting website text, enabling users to construct scalable, domain-specific datasets from the ground up for training LLMs. 

# Table of Contents
- [Table of Contents](#table-of-contents)
- [Features](#features)
- [Installation](#installation)
  - [Python Package](#python-package)
  - [From source](#from-source)
- [Usage](#usage)
  - [Key usage](#key-usage)
  - [Scheduler](#scheduler)
  - [Agent](#agent)
  - [CLI Tools](#cli-tools)
- [Background](#background)
- [Citation](#citation)

# Features
With Musubi, you can:

🕸️ Extract text data from the most websites in common structures.

🤖 Deploy AI agents to help your find out moderate parameters to crawl website and implement crawling automatically.

📆 Set schedulers to schedule your crawling tasks.

🗂️ Manage crawling configurations for each websites conveniently.

We've also developed a CLI tool that lets you crawl and deploy agents without the need to write any code!

# Installation

## Python Package

For installing Musubi with `pip`: .
```bash
pip install musubi
``` 

## From source

You can also install musubi from source to instantly use the latest features before the official release.
```bash
pip install git+https://github.com/blaze7451/Musubi.git
``` 

# Usage
In musubi, the overall crawling process can be generally splitted into two stages: link-crawling stage and content-crawling stage. In the link-crawling stage, musubi extracts all links in the specfied block in the website. For link-crawling stage, musubi furnishes four main crawling methods based on the format of website to extract the links of news, documents, and blogs: scan, scroll, click, and onepage.  Next, the corresponding text content of each links are crawled and transformed into markdown style. 

## Key usage
To crawl website contents, you can easily use `pipeline` function:
```python
from musubi import Pipeline

pipeline_kwargs = {
    "dir": dir, # Name of directorys to store links and text contents
    "name": name, # Name of saved file 
    "class_": class_,  # The type of data in the website.
    "prefix": prefix, # Main prefix of website. 
    "suffix": suffix, # The url Musubi crawling will be formulaized as "prefix1" + str((page_init_val + pages) * multiplier) + "suffix".
    "root_path": root_path, # Root of the url if urls in tags are presented in relative fashion.
    "pages": max_pages, # Number of crawling pages if type is 'scan' or number of scrolling time if type is 'scroll'.
    "page_init_val": page_init_val, # Initial value of page.
    "multiplier": multiplier, # Multiplier of page.
    "block1": block1, # List of html tag and its class. 
    "block2": block2, # Second block if crawling nested structure
    "type": website_type, # Type of crawling method to crawl urls on the website
    "async_": async_ # crawling website in the asynchronous fashion or not
}

pipeline = Pipeline(website_config_path=website_config_path)
pipeline.pipeline(**pipeline_kwargs)
```
For real-world example, see [here](examples/scrape_website_articles.py).

## Scheduler

## Agent
Musubi provides agents for users to crawl websites, set crawling scheduler, and analyze crawling configs with the help of several top-tier proprietary LLMs from corporations such as OpenAI, Anthropic, Google, and open source LLMs from Hugging Face. Set the api keys in `.env` file to leverage these LLMs:
```bash
OPENAI_API_KEY=
GROQ_API_KEY=
XAI_API_KEY=
DEEPSEEK_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```
Alternatively, you can instantiate agents with api key directly. The api key will be stored into `.env` file once the agent is instantiated by default. For example, to utilize GPT-4o to build pipeline agent in Musubi:
```python
from musubi.agent import PipelineAgent

agent = PipelineAgent(
    actions=[some-actions],
    model_source="openai",
    api_key="your-openai-apikey",
    model_type="gpt-4o"
)
```
In addition to the LLM apis for agents, google search api and google engine id are required to take `google_search` action when using `PipelineAgent`. Check [doc](https://developers.google.com/custom-search/v1/overview?source=post_page-----36e5298086e4--------------------------------&hl=zh-tw) for applying google search api and [website](https://cse.google.com/cse/all) to build search engine and retrieve engine id, and set them in `.env` file:
```bash
GOOGLE_SEARCH_API=
GOOGLE_ENGINE_ID=
```

Here is a basic example to use pipeline agent in Musubi to crawl text contents in the 'Fiction and Poetry' category on Literary Hub:
```python
from musubi.agent import PipelineAgent
from musubi.agent.actions import (
    google_search,
    analyze_website,
    get_container,
    get_page_info,
    final_answer
)


actions = [google_search, analyze_website, get_container, get_page_info, final_answer]
pipeline_agent = PipelineAgent(
    actions=actions,
    model_source="openai"
)

prompt = "Help me scrape all pages of articles from the 'Fiction and Poetry' category on Literary Hub."
pipeline_agent.execute(prompt)
```

Beyond instantiating a single agent to perform specific tasks, agents can be coordinated into a hierarchical multi-agent system to execute tasks with greater efficiency, scalability, and adaptability. For building a hierarchical multi-agent system in musubi, you can simply use `MusubiAgent`:
```python
from musubi.agent import PipelineAgent, GeneralAgent, SchedulerAgent, MusubiAgent
from musubi.agent.actions import (
    google_search,
    analyze_website,
    get_container,
    get_page_info,
    final_answer,
    domain_analyze,
    type_analyze,
    update_all,
    update_by_idx,
    upload_data_folder,
    del_web_config_by_idx
)


actions = [google_search, analyze_website, get_container, get_page_info, final_answer]
pipeline_agent = PipelineAgent(
    actions=actions
)


general_actions = [domain_analyze, type_analyze, update_all, update_by_idx, upload_data_folder, del_web_config_by_idx]
general_agent = GeneralAgent(
    actions=general_actions
)

main_agent = MusubiAgent(candidates=[general_agent, pipeline_agent])
prompt = "Check how many websites I have scraped already."
main_agent.execute(prompt)
```
Check [agent examples](examples/agents) to further view the details about how to use agents in Musubi.

## CLI Tools
Musubi support users to execute the aforementioned functions by using command line interface (CLI).   
The fundamental structure of Musubi cli tool is formed as:
```bash
musubi [COMMAND] [FLAGS] [ARGUMENTS]
```
For instance, 
# Background
*Musubi* (結び) is a japanese word of meaning “to tie something like a string”. In Shinto (神道) and traditional Japanese philosophy, musubi also refers to life, birth, relationships, and the natural cycles of the world. 

# Citation
If you use Musubi in your research or project, please cite it with the following BibTeX entry:
```bibtex
@misc{musubi2025,
  title =        {Musubi: Weaving connection to the world.},
  author =       {Lung-Chuan Chen},
  howpublished = {\url{https://github.com/blaze7451/Musubi}},
  year =         {2025}
}
```