.. musubi-scrape documentation master file, created by
   sphinx-quickstart on Thu Oct  9 00:13:14 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============

Welcome to **musubi-scrape**, a Python framework for automated web data extraction, 
data processing pipelines, and task scheduling.

**musubi-scrape** provides:

- Multi-page web crawling
- Content scraping and cleaning
- Data processing pipelines
- Scheduler and agent-based automation
- CLI commands for easy task execution

Project Overview
----------------

The main components of musubi-scrape are:

- **musubi/**: Core modules of the framework
  - `crawl_link.py` and `crawl_content.py`: Web crawling and content extraction
  - `async_crawl_*`: Asynchronous crawling for higher performance
  - `pipeline.py`: Data processing and analysis pipelines
  - `scheduler/`: Task scheduling, notifications, and management
  - `agent/`: Agent system for automated decision making
  - `utils/`: Utility functions and helpers
  - `commands/`: CLI commands for interacting with the framework
- **examples/**: Scripts demonstrating agents, pipelines, and schedulers
- **config/**: Configuration files (e.g., `websites.json`) for target websites
- **data/**: Directory to store scraped data
- **crawler/**: Temporary storage for retrieved links or intermediate data
- **logs/**: Runtime log files

Installation
------------

Install via pip:

.. code-block:: bash

   pip install musubi-scrape

Or install the latest version from source:

.. code-block:: bash

   git clone https://github.com/your-username/musubi-scrape.git
   cd musubi-scrape
   pip install .

Quick Start
-----------

Here is a minimal example to start crawling a website:

.. code-block:: python

   from musubi.crawl_link import CrawlLink
   from musubi.crawl_content import CrawlContent

   # Initialize crawler
   crawler = CrawlLink()
   crawler.run()

   # Fetch content
   content_scraper = CrawlContent()
   content_scraper.run()

Explore the **examples/** directory for more advanced usage, including:
- Agents
- Scheduler tasks
- Pipelines

Additional Resources
--------------------

- `musubi-scrape on GitHub <https://github.com/your-username/musubi-scrape>`_
- API documentation available in the **API Reference** section


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   

