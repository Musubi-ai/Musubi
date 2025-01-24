import subprocess
from dotenv import load_dotenv
import os


load_dotenv()


def logging_hf_cli(
    hf_token: str = None
):
    if hf_token is None:
        hf_token = os.getenv("HF_TOKEN")
        if hf_token is None:
            raise Exception("Cannot find huggingface access token in the device.")
    subprocess.run(["huggingface-cli", "login", "--token", hf_token])