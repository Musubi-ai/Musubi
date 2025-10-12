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
5 分鐘快速了解 Musubi-scrape 的核心功能和基本用法
:::

:::{grid-item-card}
:link: guide/guide
:link-type: doc
:shadow: lg
:class-card: sd-rounded-3
:class-header: sd-bg-success sd-bg-gradient sd-text-white sd-font-weight-bold sd-fs-5 sd-text-center sd-py-2

📚 Guides
^^^
深入學習網站爬取、AI 代理和排程器的使用方法
:::

:::{grid-item-card} 
:link: tutorial/tutorials
:link-type: doc
:shadow: lg
:class-card: sd-rounded-3
:class-header: sd-bg-danger sd-bg-gradient sd-text-white sd-font-weight-bold sd-fs-5 sd-text-center sd-py-2

🎯 Tutorials
^^^
跟隨實戰教學，從零開始建立你的爬蟲專案
:::

:::{grid-item-card}
:link: api/pipeline
:link-type: doc
:shadow: lg
:class-card: sd-rounded-3
:class-header: sd-bg-warning sd-bg-gradient sd-text-white sd-font-weight-bold sd-fs-5 sd-text-center sd-py-2

🔧 API Reference
^^^
查看完整的 Python API 文檔和函數說明
:::

::::


```{toctree}
:maxdepth: 2
:hidden:
:caption: Getting Started

getting-started/quicktour
getting-started/installation
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Guides

guide/guide
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Tutorials

tutorial/tutorials
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: API References

api/pipeline
```