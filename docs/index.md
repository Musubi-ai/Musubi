# Musubi

Welcome to Musubi-scrape's Documentation! Musubi-scrape is a Python library designed for efficiently crawling and extracting website text, enabling users to construct scalable, domain-specific datasets from the ground up for training LLMs.

With Musubi-scrape, you can:

🕸️ Extract text data from most websites with common structures and transform them into markdown format.

🤖 Deploy AI agents to help you find optimal parameters for website crawling and implement crawling automatically.

📆 Set schedulers to schedule your crawling tasks.

🗂️ Manage crawling configurations for each website conveniently.

We've also developed a CLI tool that lets you crawl and deploy agents without the need to write any code!

---

::::{grid} 2
:gutter: 3
:class-container: sd-text-center

:::{grid-item-card}
:link: getting-started/quicktour
:link-type: doc
:shadow: lg
:class-card: sd-rounded-3
:class-header: sd-bg-primary sd-bg-gradient sd-text-white sd-font-weight-bold sd-fs-5 sd-text-center sd-py-2

🚀 Getting Started
^^^
Start here to explore Musubi-scrape’s main features and learn how to efficiently crawl website articles!
:::

:::{grid-item-card} 
:link: tutorial/tutorials
:link-type: doc
:shadow: lg
:class-card: sd-rounded-3
:class-header: sd-bg-success sd-bg-gradient sd-text-white sd-font-weight-bold sd-fs-5 sd-text-center sd-py-2

🎯 Tutorials
^^^
We provide several practical examples showing how to use Musubi-scrape to crawl articles in various scenarios.
:::

:::{grid-item-card}
:link: guide/guide
:link-type: doc
:shadow: lg
:class-card: sd-rounded-3
:class-header: sd-bg-danger sd-bg-gradient sd-text-white sd-font-weight-bold sd-fs-5 sd-text-center sd-py-2

📚 Guides
^^^
Dive deep into the detailed usages of the pipeline function, configuration settings, crawling agents, schedulers, and CLI tools.
:::

:::{grid-item-card}
:link: api/Pipeline
:link-type: doc
:shadow: lg
:class-card: sd-rounded-3
:class-header: sd-bg-warning sd-bg-gradient sd-text-white sd-font-weight-bold sd-fs-5 sd-text-center sd-py-2

🔧 API Reference
^^^
Explore the complete API documentation and learn about each function in detail.
:::

::::


```{toctree}
:maxdepth: 2
:hidden:
:caption: GETTING STARTED

getting-started/quicktour
getting-started/installation
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: TUTORIALS

tutorial/tutorials
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: GUIDES

guide/guide
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: API REFERENCES

api/Pipeline
api/Crawl link
api/Crawl content
api/Utils
api/Agent
```