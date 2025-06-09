<p align="center">
    <br>
    <img src="imgs\FullLogo.png" width="600"/>
    <br>
</p>

<h1 align="center">Weaving connection to the world.🪢</h1>

<p align="center">
    <a href="https://github.com/blaze7451/Musubi/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/badge/license-Apache_2.0-blue
    "></a>
    <a href="https://github.com/Musubi-ai"><img alt="Team" src="https://img.shields.io/badge/Built%20by-Musubi%20Team-blue"></a>
</p>

Musubi is a Python library designed for efficiently crawling and extracting website text, enabling users to construct scalable, domain-specific datasets from the ground up for training LLMs. 

# Features
With Musubi, you can:

🕸️ Extract text data from the most websites in common structures.

🤖 Deploy AI agents to help your find out moderate parameters to crawl website and implement crawling automatically.

📆 Set schedulers to schedule your crawling tasks.

🗂️ Manage crawling configurations for each websites conveniently.

We've also developed a CLI tool that lets you crawl and deploy agents without the need to write any code!

# Installation

## Python Package

For installing Musubi with `pip`:
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
    "prefix": prefix, # Main prefix of website. The url Musubi crawling will be formulaized as "prefix1" + str((page_init_val + pages) * multiplier) + "suffix".
    "suffix": suffix, 
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

## Agent

## Scheduler

## CLI Tools

# Context
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