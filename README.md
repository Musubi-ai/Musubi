<p align="center">
    <br>
    <img src="assets\logo\FullLogo.png" width="600"/>
    <br>
</p>

<h1 align="center">Weaving connection to the world.🪢</h1>

<p align="center">
    <a href="https://github.com/Musubi-ai/Musubi/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/badge/license-Apache_2.0-blue
    "></a>
    <a href="https://github.com/Musubi-ai"><img alt="Team" src="https://img.shields.io/badge/Built%20by-Musubi%20Team-blue"></a>
</p>

Musubi is a Python library designed for efficiently crawling and extracting website text, enabling users to construct scalable, domain-specific datasets from the ground up for training LLMs.

With Musubi, you can:

🕸️ Extract text data from most websites with common structures and transform them into markdown format.

🤖 Deploy AI agents to help you find optimal parameters for website crawling and implement crawling automatically.

📆 Set schedulers to schedule your crawling tasks.

🗂️ Manage crawling configurations for each website conveniently.

We've also developed a CLI tool that lets you crawl and deploy agents without the need to write any code!

# Table of Contents
- [Table of Contents](#table-of-contents)
- [Installation](#installation)
  - [Python Package](#python-package)
  - [From source](#from-source)
- [Usage](#usage)
  - [Key usage](#key-usage)
    - [Demo](#demo)
  - [Scheduler](#scheduler)
    - [Notification](#notification)
  - [Agent](#agent)
    - [Multi-agent System](#multi-agent-system)
      - [Demo](#demo-1)
  - [CLI Tools](#cli-tools)
    - [Demo](#demo-2)
- [License](#license)
- [Background](#background)
- [Citation](#citation)
- [Acknowledgement](#acknowledgement)

# Installation

## Python Package

For installing Musubi with `pip`: .
```bash
pip install musubi
``` 

## From source

You can also install Musubi from source to instantly use the latest features before the official release.
```bash
pip install git+https://github.com/Musubi-ai/Musubi.git
``` 

# Usage
In Musubi, the overall crawling process can be generally split into two stages: the link-crawling stage and the content-crawling stage. In the link-crawling stage, Musubi extracts all links in the specified block on the website. For the link-crawling stage, Musubi provides four main crawling methods based on the website format to extract links of news, documents, and blogs: scan, scroll, click, and onepage. Next, the corresponding text content of each link is crawled and transformed into markdown format. 

## Key usage
To crawl website contents, you can easily use `pipeline` function:
```python
from musubi import Pipeline

pipeline_kwargs = {
    "dir": dir, # Name of directory to store links and text contents
    "name": name, # Name of saved file 
    "class_": class_,  # The type of data on the website.
    "prefix": prefix, # Main prefix of website. 
    "suffix": suffix, # The URL Musubi crawls will be formulated as "prefix" + str((page_init_val + pages) * multiplier) + "suffix".
    "root_path": root_path, # Root of the URL if URLs in tags are presented in relative format.
    "pages": max_pages, # Number of crawling pages if type is 'scan' or number of scrolling times if type is 'scroll'.
    "page_init_val": page_init_val, # Initial value of page.
    "multiplier": multiplier, # Multiplier of page.
    "block1": block1, # List of HTML tag and its class. 
    "block2": block2, # Second block if crawling nested structure
    "type": website_type, # Type of crawling method to crawl URLs on the website
    "async_": async_ # Whether to crawl website asynchronously or not
}

pipeline = Pipeline(website_config_path=website_config_path)
pipeline.pipeline(**pipeline_kwargs)
```

### Demo
Task: Crawl 3 pages of articles from the 'Fiction and Poetry' category on Literary Hub.
```python
from musubi.pipeline import Pipeline


pipe = Pipeline(website_config_path=r"config\test.json")

pipe.pipeline(
    dir = "Literary Hub",
    name = "Fiction and Poetry",  
    class_ = "English",
    prefix = "https://lithub.com/category/fictionandpoetry/page/",
    suffix = "/",
    root_path = "https://lithub.com",
    pages = 3,
    page_init_val = 1,
    multiplier = 1,
    block1 = ["div", "post_header"],
    block2 = None,
    type = "scan",
    )
```

https://github.com/user-attachments/assets/223a5d62-8364-4964-ade6-829306fec271


## Scheduler
Musubi allows users to set up a scheduler to run crawling tasks at specified times. To launch a scheduler:
```python
from musubi.scheduler import Controller

controller = Controller()
controller.launch_scheduler()
```
By default, the scheduler uses `tasks.json` in the config folder as a task management configuration and uses `websites.json` to implement crawling tasks. Users can customize these settings using arguments:
```python
from musubi.scheduler import Controller

controller = Controller(
        config_dir="folder-of-task.json"
        website_config_path="path-of-website.json" 
    )
```
After launching the scheduler, users can add tasks and set the scheduler to implement tasks regularly. Currently, we support users to set tasks with task type `update_all` or `by_idx`. The `update_all` task crawls all websites stored in the website configuration file and the `by_idx` task crawls the specific website as specified by its index. Note that in the Musubi scheduler, we follow the common cron format to define when to implement the task. For instance, to set a regular update task to crawl all websites stored in the `websites.json` file at 12:05:05 on the 5th day of May each year:
```python
from musubi.scheduler import Controller

controller = Controller()

def main():
    status_code, _ = controller.check_status()
    if status_code == 200:
        controller.add_task(
        task_type="update_all",
        task_name="test1",
        update_pages=15,
        cron_params={"hour": 12, "second": 5, "minute": 5, "month": 5}
    )

if __name__ == "__main__":
    main()
```
For valid cron_params arguments, check [reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html).

### Notification
Users can set the argument `send_notification=True` in the `add_task` function so that the program will send Gmail notifications when scheduled tasks start and finish. Go to [this website](https://myaccount.google.com/apppasswords) to apply for an app password and set the environment variable in the `.env` file:

```bash
GOOGLE_APP_PASSWORD="your-app-password"
```

Then the notification can be used like:
```python
controller.add_task(
    ...,
    send_notification=True,
    sender_email="youe-account@gmail.com"
)
```

## Agent
Musubi provides agents for users to crawl websites, set crawling schedulers, and analyze crawling configurations with the help of several top-tier proprietary LLMs from corporations such as OpenAI, Anthropic, Google, and open-source LLMs from Hugging Face. Set the API keys in the `.env` file to use these LLMs:

```bash
OPENAI_API_KEY=
GROQ_API_KEY=
XAI_API_KEY=
DEEPSEEK_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Alternatively, you can instantiate agents with an API key directly. The API key will be stored in the `.env` file once the agent is instantiated by default. For example, to utilize GPT-4o to build a pipeline agent in Musubi:

```python
from musubi.agent import PipelineAgent

agent = PipelineAgent(
    actions=[some-actions],
    model_source="openai",
    api_key="your-openai-apikey",
    model_type="gpt-4o"
)
```

In addition to the LLM APIs for agents, Google Search API and Google Engine ID are required to take the `google_search` action when using `PipelineAgent`. Check this [documentation](https://developers.google.com/custom-search/v1/overview?source=post_page-----36e5298086e4--------------------------------&hl=zh-tw) for applying for Google Search API and this [website](https://cse.google.com/cse/all) to build a search engine and retrieve the engine ID, then set them in the `.env` file:

```bash
GOOGLE_SEARCH_API=
GOOGLE_ENGINE_ID=
```

Here is a basic example of using a pipeline agent in Musubi to crawl text contents in the 'Fiction and Poetry' category on Literary Hub:

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

### Multi-agent System
Beyond instantiating a single agent to perform specific tasks, agents can be coordinated into a hierarchical multi-agent system to execute tasks with greater efficiency, scalability, and adaptability. To build a hierarchical multi-agent system in Musubi, you can simply use `MusubiAgent`:

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

#### Demo
Task: Crawl 5 pages of articles from the 'Fiction and Poetry' category on Literary Hub.


https://github.com/user-attachments/assets/f61f40fb-882b-4484-9a9d-0304a8967a9e


Check [agent examples](examples/agents) to further view the details about how to use agents in Musubi.

## CLI Tools
Musubi supports users to execute the aforementioned functions using the command line interface (CLI).
The fundamental structure of the Musubi CLI tool is formed as:

```bash
musubi [COMMAND] [FLAGS] [ARGUMENTS]
```

For instance, to add openai api key into `.env` file with Musubi cli, you can use:

```bash
musubi env --openai your-openai-api-key
``` 

Use `pipeline` to crawl a website (Suppose that we want to crawl articles present in the first 5 pages of the Chinese website called '測試' with URL https://www.test.com/category?&pages=n):

```bash
musubi pipeline \
  --dir 測試 \
  --name 測試文章 \
  --class_ 中文 \
  --prefix https://www.test.com/category?&pages= \
  --pages 5 \
  --block1 ["div", "entry-image"] 
  --type scan \
```

Use agent:

```bash
musubi agent \
  --prompt "Help me crawl all pages of articles from the 'Fiction and Poetry' category on Literary Hub." \
  --model_source anthropic \
  --model_type claude-opus-4-20250514
```

Re-crawl all previously crawled websites according to the specified page numbers:

```bash
musubi strat-all \
 --website_config_path config/websites.json \
 --update-pages 80
```
### Demo
Task: Crawl all websites whose configurations stored in `config\test_websites.json` again (update 5 pages). 

https://github.com/user-attachments/assets/f7c17fa6-f2ab-48c9-aea1-f795cea362a0

# License
This repository is licensed under the [Apache-2.0 License](LICENSE).

# Background
*Musubi* (結び) is a japanese word of meaning “to tie something like a string”. In Shinto (神道) and traditional Japanese philosophy, musubi also refers to life, birth, relationships, and the natural cycles of the world.

# Citation
If you use Musubi in your research or project, please cite it with the following BibTeX entry:
```bibtex
@misc{musubi2025,
  title =        {Musubi: Weaving connection to the world.},
  author =       {Lung-Chuan Chen},
  howpublished = {\url{https://github.com/Musubi-ai/Musubi}},
  year =         {2025}
}
```

# Acknowledgement
This repo benefits from [trafilatura](https://github.com/adbar/trafilatura) for extracting text contents from webpages and [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for parsing online PDF documents.