# Quicktour

Musubi-scrape provides convenient methods for crawling web text data. As the demand for advanced large language models (LLMs) continues to grow, building high-quality, large-scale text corpora has become essential for their development. The World Wide Web (WWW), a global, borderless, and open platform, provides abundant multimodal data—including text, images, and videos—that can be leveraged for this purpose. To date, crawling websites at scale has become a common approach for collecting such data. However, when it comes to crawling textual data, the main challenge lies not only in implementing scalable crawling across diverse website architectures but also in accurately extracting high-quality text—such as blog posts, news articles, and other written content—from websites. Musubi-scrape is specifically designed to address these challenges.

This quick tour introduces the main features of Musubi-scrape and demonstrates how to easily crawl web text data using the library.

## Pipeline
Musubi-scrape provides `pipeline` function to efficiently crawl article text in the certain website. The overall crawling process can be generally split into two stages: the link-crawling stage and the content-crawling stage. In the link-crawling stage, Musubi extracts all links in the specified block on the website. For the link-crawling stage, Musubi provides four main crawling methods based on the website format to extract links of news, documents, and blogs: scan, scroll, click, and onepage. Next, the corresponding text content of each link is crawled and transformed into markdown format. 

Let's dig into the practical example. Suppose we want to crawl articles from the News and Culture category on Literary Hub, a website that provides up-to-date literary news. Now, to crawl with Musuibi-scrape, import `pipeline` function and specify the following arguments:

- `aaaa`: aaaaa