import argparse
from dotenv import set_key
from loguru import logger
from ..utils.env import create_env_file


def env_command_parser(subparsers=None):
    """Create and configure argument parser for env command.

    This function creates an argument parser for the Musubi env command,
    which is used to configure environment variables including API tokens
    for various AI services and notification systems.

    Args:
        subparsers: An argparse subparsers object to add this parser to.
            If None, creates a standalone ArgumentParser. Defaults to None.

    Returns:
        argparse.ArgumentParser: The configured argument parser with all
            environment configuration arguments and defaults set.
    """
    if subparsers is not None:
        parser = subparsers.add_parser("env")
    else:
        parser = argparse.ArgumentParser("Musubi env command")

    parser.add_argument(
        "--google_app_password", type=str, default=None, help="Google app password to let musubi send gmail notification."
    )
    parser.add_argument(
        "--hf_token", type=str, default=None, help="Huggingface token"
    )
    parser.add_argument(
        "--openai", type=str, default=None, help="OpenAI api token"
    )
    parser.add_argument(
        "--groq", type=str, default=None, help="Groq api token"
    )
    parser.add_argument(
        "--xai", type=str, default=None, help="XAI api token"
    )
    parser.add_argument(
        "--deepseek", type=str, default=None, help="Deepseek api token"
    )
    parser.add_argument(
        "--anthropic", type=str, default=None, help="Anthropic api token"
    )
    parser.add_argument(
        "--gemini", type=str, default=None, help="Gemini api token"
    )
    if subparsers is not None:
        parser.set_defaults(func=env_command)
    return parser


def env_command(args):
    """Execute the env command to configure environment variables.

    This function creates or updates a .env file with API tokens and
    credentials for various services. Only non-None arguments are written
    to the environment file, allowing selective updates.

    Args:
        args: An argparse.Namespace object containing the following attributes:
            google_app_password (str): Google app password for Gmail notifications. Optional.
            hf_token (str): Hugging Face API token. Optional.
            openai (str): OpenAI API key. Optional.
            groq (str): Groq API key. Optional.
            xai (str): XAI API key. Optional.
            deepseek (str): Deepseek API key. Optional.
            anthropic (str): Anthropic API key. Optional.
            gemini (str): Gemini API key. Optional.

    Returns:
        None: This function updates the .env file and returns nothing.

    Note:
        - Creates a new .env file if it doesn't exist
        - Only updates keys that are provided (non-None values)
        - Environment variable names are standardized:
            * GOOGLE_APP_PASSWORD for Gmail notifications
            * HF_TOKEN for Hugging Face
            * OPENAI_API_KEY, GROQ_API_KEY, XAI_API_KEY, etc. for AI services
        - Logs completion message after updating the file
    """
    env_path = create_env_file()
    if args.google_app_password is not None:
        set_key(env_path, key_to_set="GOOGLE_APP_PASSWORD", value_to_set=args.google_app_password)
    if args.hf_token is not None:
        set_key(env_path, key_to_set="HF_TOKEN", value_to_set=args.hf_token)
    if args.openai is not None:
        set_key(env_path, key_to_set="OPENAI_API_KEY", value_to_set=args.openai)
    if args.groq is not None:
        set_key(env_path, key_to_set="GROQ_API_KEY", value_to_set=args.groq)
    if args.xai is not None:
        set_key(env_path, key_to_set="XAI_API_KEY", value_to_set=args.xai)
    if args.deepseek is not None:
        set_key(env_path, key_to_set="DEEPSEEK_API_KEY", value_to_set=args.deepseek)
    if args.anthropic is not None:
        set_key(env_path, key_to_set="ANTHROPIC_API_KEY", value_to_set=args.anthropic)
    if args.gemini is not None:
        set_key(env_path, key_to_set="GEMINI_API_KEY", value_to_set=args.gemini)
    
    logger.info("Finished overwriting .env file.")