from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import os
from ...pipeline import Pipeline
from ...utils import (
    ConfigAnalyzer, 
    delete_website_config_by_idx, 
    upload_folder
)


def domain_analyze(website_config_path = Path("config") / "websites.json"):
    """Analyzes a JSON file containing website configurations and counts the number of main domains and subdomains.

    Args:
        website_config_path (Path or str, optional): The path to the `websites.json` file containing website data. 
            Defaults to "config/websites.json".

    Returns:
        dict: A dictionary containing:
            - `num_main_domain` (int): The number of unique main domains.
            - `num_sub_domain` (int): The total number of subdomains.
    """
    analyzer = ConfigAnalyzer(website_config_path)
    report = analyzer.domain_analyze()
    return report


def type_analyze(website_config_path = Path("config") / "websites.json"):
    """Analyzes a JSON file containing website configurations and counts the occurrences of different website types.

    Args:
        website_config_path (Path or str, optional): The path to the `websites.json` file containing website data. 
            Defaults to "config/websites.json".

    Returns:
        dict: A dictionary containing:
            - `all_num` (int): The total number of websites.
            - `scan` (int): The count of websites classified as "scan".
            - `scroll` (int): The count of websites classified as "scroll".
            - `onepage` (int): The count of websites classified as "onepage".
            - `click` (int): The count of websites classified as "click".
    """
    analyzer = ConfigAnalyzer(website_config_path)
    report = analyzer.type_analyze()
    return report


def upgrade_all(
    website_config_path = Path("config") / "websites.json",
    start_idx: Optional[int] = 0,
    upgrade_pages: Optional[int] = None,
    save_dir: Optional[str] = None
):
    """
    Crawls all websites listed in the website configuration JSON file.

    This function initializes a `Pipeline` instance and calls `start_all()` to upgrade 
    or fully crawl all websites in the configuration file, starting from `start_idx`.

    Args:
        website_config_path (Union[str, Path]): 
            Path to the website configuration file (`websites.json` or `imgtxt_webs.json`). 
            Defaults to `"config/websites.json"`.
        start_idx (Optional[int]): 
            The index from which to start upgrading or crawling websites. Defaults to `0`.
        upgrade_pages (Optional[int]): 
            The number of pages to crawl in upgrade mode. If None, the function switches to 
            add mode and crawls all available pages.
        save_dir (Optional[str]): 
            Directory where `link.json` and articles will be saved. If None, defaults to `"data"`.

    Example:
        >>> upgrade_all(start_idx=2, upgrade_pages=50)
    """
    pipeline = Pipeline(website_config_path=website_config_path)
    pipeline.start_all(start_idx=start_idx, upgrade_pages=upgrade_pages, save_dir=save_dir)


def upgrade_by_idx(
    idx: Optional[int],
    website_config_path: Optional[str] = None,
    upgrade_pages: Optional[int] = None,
    save_dir: Optional[str] = None,
):
    """
    Crawls articles from a website specified by `idx` in `websites.json` or `imgtxt_webs.json` 
    in upgrade mode.

    This function initializes a `Pipeline` instance and calls `start_by_idx()` to crawl a 
    specified number of pages in upgrade mode. If `upgrade_pages` is None, it will crawl all 
    pages of the website in add mode.

    Args:
        website_config_path (Optional[str]): 
            Path to the website configuration file (`websites.json` or `imgtxt_webs.json`). 
            If None, defaults to `"config/websites.json"`.
        idx (Optional[int]): 
            The index of the website to crawl in the configuration file. Must not be None.
        upgrade_pages (Optional[int]): 
            The number of pages to crawl in upgrade mode. If None, the function switches to 
            add mode and crawls all available pages.
        save_dir (Optional[str]): 
            Directory where `link.json` and articles will be saved. If None, defaults to `"data"`.

    Raises:
        ValueError: If `idx` is None, since an index must be specified to crawl a website.

    Example:
        >>> upgrade_by_idx(idx=3, upgrade_pages=5)
    """
    pipeline = Pipeline(website_config_path=website_config_path)
    pipeline.start_by_idx(idx=idx, upgrade_pages=upgrade_pages, save_dir=save_dir)


def upload_data_folder(
    repo_id: str = None,
    repo_type: str = "dataset",
    folder_path: str = None,
):
    """A wrapper function for uploading a folder to Hugging Face using environment variables.

    This function uses the HF_TOKEN from environment variables and calls upload_folder
    with the provided parameters.

    Args:
        repo_id (str, optional): The repository ID on Hugging Face where the folder will be uploaded.
            Defaults to None.
        repo_type (str, optional): The type of repository ('dataset' or 'model').
            Defaults to "dataset".
        folder_path (str, optional): The local path to the folder to be uploaded.
            Defaults to None.

    Raises:
        Exception: If no Hugging Face token is found in the environment variables.

    Examples:
        >>> upload_data_folder(
        ...     repo_id="username/repo-name",
        ...     folder_path="path/to/folder"
        ... )
    """
    load_dotenv()
    if os.getenv("HF_TOKEN") is None:
        raise Exception("Cannot find huggingface access token in the device.")
    upload_folder(
        repo_id=repo_id,
        repo_type=repo_type,
        folder_path=folder_path
    )
    

def del_web_config_by_idx(
    idx: int,
    website_config_path = Path("config") / "websites.json"
):
    """Wrapper function for deleting a website configuration from websites.json by index and reordering remaining configs.

    This function removes a website configuration entry by its index from the JSON file,
    then reindexes all remaining configurations to maintain consecutive ordering.
    If the file becomes empty after deletion, it will be cleared.

    Args:
        idx (int): The index of the website configuration to delete.
        website_config_path (optional): Path to the websites configuration file.
            Defaults to Path("config") / "websites.json".

    Note:
        - The function uses JSONL format (one JSON object per line)
        - After deletion, all configurations with indices >= idx will have their indices decremented by 1
        - If the file becomes empty, it will be cleared rather than containing empty lines

    Examples:
        >>> delete_website_config_by_idx(2)  # Deletes configuration at index 2
        >>> delete_website_config_by_idx(
        ...     idx=1,
        ...     website_config_path=Path("custom/config/websites.json")
        ... )
    """
    delete_website_config_by_idx(idx=idx, website_config_path=website_config_path)