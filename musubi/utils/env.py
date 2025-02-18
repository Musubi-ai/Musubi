import subprocess
from typing import Optional
from dotenv import load_dotenv, set_key
from huggingface_hub import HfApi
from pathlib import Path
import os


def create_env_file():
    env_path = Path(".env")
    env_path.touch(mode=0o600, exist_ok=True)
    return env_path


def logging_hf_cli(
    hf_token: str = None
):
    load_dotenv()
    if hf_token is None:
        hf_token = os.getenv("HF_TOKEN")
        if hf_token is None:
            raise Exception("Cannot find huggingface access token in the device.")
    subprocess.run(["huggingface-cli", "login", "--token", hf_token])
    if hf_token != os.getenv("HF_TOKEN"):
        env_path = create_env_file()
        set_key(env_path, key_to_set="HF_TOKEN", value_to_set=hf_token)


def upload_folder(
    repo_id: str = None,
    repo_type: str = "dataset",
    folder_path: str = None,
    hf_token: Optional[str] = None,
):
    """Uploads a folder to Hugging Face using the provided credentials and parameters.

    Args:
        repo_id (str, optional): The repository ID on Hugging Face where the folder will be uploaded.
            Defaults to None.
        repo_type (str, optional): The type of repository ('dataset' or 'model').
            Defaults to "dataset".
        folder_path (str, optional): The local path to the folder to be uploaded.
            Defaults to None.
        hf_token (str, optional): Hugging Face API token for authentication.
            If not provided, tries to get from environment variable 'HF_TOKEN'.
            Defaults to None.

    Raises:
        Exception: If no Hugging Face token is found in the environment variables when
            hf_token is not provided.

    Examples:
        >>> upload_folder(
        ...     repo_id="username/repo-name",
        ...     folder_path="path/to/folder",
        ...     hf_token="your-token"
        ... )
    """
    load_dotenv()
    if hf_token is None:
        hf_token = os.getenv("HF_TOKEN")
        if hf_token is None:
            raise Exception("Cannot find huggingface access token in the device.")
    api = HfApi(token=hf_token)
    api.upload_large_folder(
        repo_id=repo_id,
        repo_type=repo_type,
        folder_path=folder_path,
    )

