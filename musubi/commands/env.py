import argparse
from dotenv import set_key
from loguru import logger
from ..utils.env import create_env_file


def env_command_parser(subparsers=None):
    if subparsers is not None:
        parser = subparsers.add_parser("env")
    else:
        parser = argparse.ArgumentParser("Musubi env command")

    parser.add_argument(
        "--google_search_api", type=str, default=None, help="Google search api for searching."
    )
    parser.add_argument(
        "--google_engine_id", type=str, default=None, help="Google engine id for searching."
    )
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
    env_path = create_env_file()
    if args.google_search_api is not None:
        set_key(env_path, key_to_set="GOOGLE_SEARCH_API", value_to_set=args.google_search_api)
    if args.google_engine_id is not None:
        set_key(env_path, key_to_set="GOOGLE_ENGINE_ID", value_to_set=args.google_engine_id)
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