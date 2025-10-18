import openai
import groq
import anthropic
from huggingface_hub import InferenceClient
from typing import Optional
from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv, set_key
from ..utils.env import create_env_file


load_dotenv()


class BaseModel(ABC):
    """Abstract base class wrapper for language model APIs.

    This class provides a common interface for interacting with various language model
    APIs. It manages conversation history, handles message formatting, and provides
    a consistent call interface for generating responses.
    """
    def __init__(
        self,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
        """Initializes the BaseModel with optional system prompt and model type.

        Args:
            system_prompt (Optional[str], optional): System prompt to initialize the
                conversation context. If provided, it will be added as the first message
                with role 'system'. Defaults to None.
            model_type (Optional[str], optional): Identifier for the specific model
                type or version to use. Defaults to None.
        """
        self.system_prompt = system_prompt
        self.model_type = model_type
        self.messages = []
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})

    def __call__(
        self,
        message: str,
        **generate_kwargs
    ):
        """Generates a response to the given message and updates conversation history.

        This method provides a convenient callable interface for the model. It appends
        the user message to the conversation history, executes the model to generate
        a response, and appends the assistant's response to the history.

        Args:
            message (str): User message or prompt to send to the model.
            **generate_kwargs: Additional keyword arguments passed to the execute method
                for controlling generation behavior (e.g., temperature, max_tokens).

        Returns:
            The model's generated response. The exact return type depends on the
            implementation in subclasses.

        Raises:
            ValueError: If message is not a string.
        """
        if not isinstance(message, str):
            raise ValueError("The message should be string.")
        self.messages.append({"role": "user", "content": message})
        result = self.execute(**generate_kwargs)
        self.messages.append({"role": "assistant", "content": str(result)})
        return result
    
    @abstractmethod
    def execute(self):
        """Executes the API call to generate a response.

        Abstract method that must be implemented by subclasses to define the specific
        logic for interacting with the underlying language model API.

        Returns:
            Implementation-dependent return value containing the model's response.

        Note:
            Subclasses should implement this method to:
            - Make the actual API call to the language model
            - Process the response appropriately
            - Return the generated content
        """
        pass


class OpenAIModel(BaseModel):
    """Concrete implementation of BaseModel for OpenAI's language models.

    This class provides a wrapper for OpenAI's chat completion API, handling API key
    management, message history, and model configuration. It automatically manages
    environment variables for API key storage and provides a simple interface for
    generating responses.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
        """Initializes the OpenAIModel with API credentials and configuration.

        Sets up the OpenAI client with the provided or environment-stored API key.
        If an API key is provided and differs from the current environment variable,
        it will be saved to the .env file. Initializes the conversation history with
        an optional system prompt.

        Args:
            api_key (Optional[str], optional): OpenAI API key for authentication. If not
                provided, attempts to use the OPENAI_API_KEY environment variable.
                Defaults to None.
            system_prompt (Optional[str], optional): System prompt to initialize the
                conversation context. If provided, it will be added as the first message
                with role 'system'. Defaults to None.
            model_type (Optional[str], optional): Identifier for the specific OpenAI model
                to use (e.g., "gpt-4", "gpt-3.5-turbo"). Defaults to "gpt-5" if not
                specified.

        Raises:
            ValueError: If no API key is provided and OPENAI_API_KEY environment
                variable is not set.

        Note:
            The API key will be automatically saved to a .env file if it differs from
            the current environment variable value.
        """
        super().__init__()
        if api_key is not None:
            if os.getenv("OPENAI_API_KEY") != api_key:
                env_path = create_env_file()
                set_key(env_path, key_to_set="OPENAI_API_KEY", value_to_set=api_key)
            self.api_key = api_key
        elif os.getenv("OPENAI_API_KEY"):
            self.api_key = os.getenv("OPENAI_API_KEY")
        else:
            raise ValueError("API Key is required for OpenAIModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model_type = model_type
        if self.model_type is None:
            self.model_type = "gpt-5"
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model_type,
        messages=self.messages,
        **generate_kwargs
        )
        """Executes an OpenAI chat completion API call and returns the response.

        Makes a chat completion request to the OpenAI API using the current conversation
        history and returns both the generated content and token usage information.

        Args:
            **generate_kwargs: Additional keyword arguments passed to the OpenAI API
                for controlling generation behavior. Common options include:
                - temperature (float): Sampling temperature (0.0 to 2.0)
                - max_tokens (int): Maximum number of tokens to generate
                - top_p (float): Nucleus sampling parameter
                - frequency_penalty (float): Penalty for token frequency
                - presence_penalty (float): Penalty for token presence

        Returns:
            tuple: A tuple containing:
                - str: The generated message content from the model
                - int: Total number of tokens used in the API call (prompt + completion)
        """
        return completion.choices[0].message.content, completion.usage.total_tokens


class GroqModel(BaseModel):
    """Concrete implementation of BaseModel for Groq's language models.

    This class provides a wrapper for Groq's chat completion API, handling API key
    management, message history, and model configuration. It automatically manages
    environment variables for API key storage and provides a simple interface for
    generating responses using Groq's high-performance inference platform.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
        """Initializes the GroqModel with API credentials and configuration.

        Sets up the Groq client with the provided or environment-stored API key.
        If an API key is provided and differs from the current environment variable,
        it will be saved to the .env file. Initializes the conversation history with
        an optional system prompt.

        Args:
            api_key (Optional[str], optional): Groq API key for authentication. If not
                provided, attempts to use the GROQ_API_KEY environment variable.
                Defaults to None.
            system_prompt (Optional[str], optional): System prompt to initialize the
                conversation context. If provided, it will be added as the first message
                with role 'system'. Defaults to None.
            model_type (Optional[str], optional): Identifier for the specific Groq model
                to use (e.g., "llama-3.1-70b-versatile", "mixtral-8x7b-32768"). 
                Defaults to "openai/gpt-oss-120b" if not specified.

        Raises:
            ValueError: If no API key is provided and GROQ_API_KEY environment
                variable is not set.

        Note:
            The API key will be automatically saved to a .env file if it differs from
            the current environment variable value.
        """
        super().__init__()
        if api_key is not None:
            if os.getenv("GROQ_API_KEY") != api_key:
                env_path = create_env_file()
                set_key(env_path, key_to_set="GROQ_API_KEY", value_to_set=api_key)
            self.api_key = api_key
        elif os.getenv("GROQ_API_KEY"):
            self.api_key = os.getenv("GROQ_API_KEY")
        else:
            raise ValueError("API Key is required for GroqModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model_type = model_type
        if self.model_type is None:
            self.model_type = "openai/gpt-oss-120b"
        self.client = groq.Groq(api_key=self.api_key)
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model_type,
        messages=self.messages,
        **generate_kwargs
        )
        """Executes a Groq chat completion API call and returns the response.

        Makes a chat completion request to the Groq API using the current conversation
        history and returns both the generated content and token usage information.

        Args:
            **generate_kwargs: Additional keyword arguments passed to the Groq API
                for controlling generation behavior. Common options include:
                - temperature (float): Sampling temperature (0.0 to 2.0)
                - max_tokens (int): Maximum number of tokens to generate
                - top_p (float): Nucleus sampling parameter
                - frequency_penalty (float): Penalty for token frequency
                - presence_penalty (float): Penalty for token presence
                - stop (Union[str, List[str]]): Stop sequences

        Returns:
            tuple: A tuple containing:
                - str: The generated message content from the model
                - int: Total number of tokens used in the API call (prompt + completion)
        """
        return completion.choices[0].message.content, completion.usage.total_tokens
    

class GrokModel(BaseModel):
    """Concrete implementation of BaseModel for xAI's Grok language models.

    This class provides a wrapper for xAI's Grok chat completion API, handling API key
    management, message history, and model configuration. It uses OpenAI's client library
    with a custom base URL to interact with xAI's API endpoint. The class automatically
    manages environment variables for API key storage.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
        """Initializes the GrokModel with API credentials and configuration.

        Sets up the xAI Grok client with the provided or environment-stored API key.
        If an API key is provided and differs from the current environment variable,
        it will be saved to the .env file. Initializes the conversation history with
        an optional system prompt. Uses OpenAI's client library with xAI's base URL.

        Args:
            api_key (Optional[str], optional): xAI API key for authentication. If not
                provided, attempts to use the XAI_API_KEY environment variable.
                Defaults to None.
            system_prompt (Optional[str], optional): System prompt to initialize the
                conversation context. If provided, it will be added as the first message
                with role 'system'. Defaults to None.
            model_type (Optional[str], optional): Identifier for the specific Grok model
                to use (e.g., "grok-2", "grok-beta"). Defaults to "grok-4" if not
                specified.

        Raises:
            ValueError: If no API key is provided and XAI_API_KEY environment
                variable is not set.

        Note:
            The API key will be automatically saved to a .env file if it differs from
            the current environment variable value. This implementation uses OpenAI's
            client library with the base URL set to "https://api.x.ai/v1".
        """
        super().__init__()
        if api_key is not None:
            if os.getenv("XAI_API_KEY") != api_key:
                env_path = create_env_file()
                set_key(env_path, key_to_set="XAI_API_KEY", value_to_set=api_key)
            self.api_key = api_key
        elif os.getenv("XAI_API_KEY"):
            self.api_key = os.getenv("XAI_API_KEY")
        else:
            raise ValueError("API Key is required for GrokModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model_type = model_type
        if self.model_type is None:
            self.model_type = "grok-4"
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
        )
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model_type,
        messages=self.messages,
        **generate_kwargs
        )
        """Executes a Grok chat completion API call and returns the response.

        Makes a chat completion request to the xAI Grok API using the current conversation
        history and returns both the generated content and token usage information.

        Args:
            **generate_kwargs: Additional keyword arguments passed to the Grok API
                for controlling generation behavior. Common options include:
                - temperature (float): Sampling temperature (0.0 to 2.0)
                - max_tokens (int): Maximum number of tokens to generate
                - top_p (float): Nucleus sampling parameter
                - frequency_penalty (float): Penalty for token frequency
                - presence_penalty (float): Penalty for token presence
                - stop (Union[str, List[str]]): Stop sequences

        Returns:
            tuple: A tuple containing:
                - str: The generated message content from the model
                - int: Total number of tokens used in the API call (prompt + completion)
        """
        return completion.choices[0].message.content, completion.usage.total_tokens
    

class DeepseekModel(BaseModel):
    """Concrete implementation of BaseModel for Deepseek's language models.

    This class provides a wrapper for Deepseek's chat completion API, handling API key
    management, message history, and model configuration. It uses OpenAI's client library
    with a custom base URL to interact with Deepseek's API endpoint. The class automatically
    manages environment variables for API key storage.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
        """Initializes the DeepseekModel with API credentials and configuration.

        Sets up the Deepseek client with the provided or environment-stored API key.
        If an API key is provided and differs from the current environment variable,
        it will be saved to the .env file. Initializes the conversation history with
        an optional system prompt. Uses OpenAI's client library with Deepseek's base URL.

        Args:
            api_key (Optional[str], optional): Deepseek API key for authentication. If not
                provided, attempts to use the DEEPSEEK_API_KEY environment variable.
                Defaults to None.
            system_prompt (Optional[str], optional): System prompt to initialize the
                conversation context. If provided, it will be added as the first message
                with role 'system'. Defaults to None.
            model_type (Optional[str], optional): Identifier for the specific Deepseek model
                to use (e.g., "deepseek-chat", "deepseek-coder"). Defaults to "deepseek-chat"
                if not specified.

        Raises:
            ValueError: If no API key is provided and DEEPSEEK_API_KEY environment
                variable is not set.

        Note:
            The API key will be automatically saved to a .env file if it differs from
            the current environment variable value. This implementation uses OpenAI's
            client library with the base URL set to "https://api.deepseek.com".
        """
        super().__init__()
        if api_key is not None:
            if os.getenv("DEEPSEEK_API_KEY") != api_key:
                env_path = create_env_file()
                set_key(env_path, key_to_set="DEEPSEEK_API_KEY", value_to_set=api_key)
            self.api_key = api_key
        elif os.getenv("DEEPSEEK_API_KEY"):
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
        else:
            raise ValueError("API Key is required for DeepseekModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model_type = model_type
        if self.model_type is None:
            self.model_type = "deepseek-chat"
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )
    
    def execute(self, **generate_kwargs):
        """Executes a Deepseek chat completion API call and returns the response.

        Makes a chat completion request to the Deepseek API using the current conversation
        history and returns both the generated content and token usage information.

        Args:
            **generate_kwargs: Additional keyword arguments passed to the Deepseek API
                for controlling generation behavior. Common options include:
                - temperature (float): Sampling temperature (0.0 to 2.0)
                - max_tokens (int): Maximum number of tokens to generate
                - top_p (float): Nucleus sampling parameter
                - frequency_penalty (float): Penalty for token frequency
                - presence_penalty (float): Penalty for token presence
                - stop (Union[str, List[str]]): Stop sequences

        Returns:
            tuple: A tuple containing:
                - str: The generated message content from the model
                - int: Total number of tokens used in the API call (prompt + completion)
        """
        completion = self.client.chat.completions.create(
        model=self.model_type,
        messages=self.messages,
        **generate_kwargs
        )
        return completion.choices[0].message.content, completion.usage.total_tokens
    

class ClaudeModel(BaseModel):
    """Concrete implementation of BaseModel for Anthropic's Claude language models.

    This class provides a wrapper for Anthropic's Claude API, handling API key
    management, message history, and model configuration. It uses Anthropic's native
    client library to interact with Claude models. The class automatically manages
    environment variables for API key storage.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
        """Initializes the ClaudeModel with API credentials and configuration.

        Sets up the Anthropic Claude client with the provided or environment-stored API key.
        If an API key is provided and differs from the current environment variable,
        it will be saved to the .env file. Initializes the conversation history with
        an optional system prompt.

        Args:
            api_key (Optional[str], optional): Anthropic API key for authentication. If not
                provided, attempts to use the ANTHROPIC_API_KEY environment variable.
                Defaults to None.
            system_prompt (Optional[str], optional): System prompt to initialize the
                conversation context. If provided, it will be added as the first message
                with role 'system'. Defaults to None.
            model_type (Optional[str], optional): Identifier for the specific Claude model
                to use (e.g., "claude-3-opus-20240229", "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"). Defaults to "claude-opus-4-1-20250805" if not
                specified.

        Raises:
            ValueError: If no API key is provided and ANTHROPIC_API_KEY environment
                variable is not set.

        Note:
            The API key will be automatically saved to a .env file if it differs from
            the current environment variable value. This implementation uses Anthropic's
            native client library.
        """
        super().__init__()
        if api_key is not None:
            if os.getenv("ANTHROPIC_API_KEY") != api_key:
                env_path = create_env_file()
                set_key(env_path, key_to_set="ANTHROPIC_API_KEY", value_to_set=api_key)
            self.api_key = api_key
        elif os.getenv("ANTHROPIC_API_KEY"):
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
        else:
            raise ValueError("API Key is required for ClaudeModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model_type = model_type
        if self.model_type is None:
            self.model_type = "claude-opus-4-1-20250805"
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
        )
    
    def execute(self, **generate_kwargs):
        completion = self.client.messages.create(
        model=self.model_type,
        messages=self.messages,
        **generate_kwargs
        )
        """Executes a Claude message creation API call and returns the response.

        Makes a message creation request to the Anthropic Claude API using the current
        conversation history and returns both the generated content and token usage
        information.

        Args:
            **generate_kwargs: Additional keyword arguments passed to the Claude API
                for controlling generation behavior. Common options include:
                - max_tokens (int): Maximum number of tokens to generate (required by API)
                - temperature (float): Sampling temperature (0.0 to 1.0)
                - top_p (float): Nucleus sampling parameter
                - top_k (int): Top-k sampling parameter
                - stop_sequences (List[str]): Sequences that will stop generation

        Returns:
            tuple: A tuple containing:
                - str: The generated message text content from the model
                - int: Total number of tokens used in the API call (prompt + completion)

        Note:
            Unlike OpenAI-compatible APIs, Claude's API requires max_tokens to be
            explicitly specified in generate_kwargs.
        """
        return completion.content[0].text, completion.usage.total_tokens


class GeminiModel(BaseModel):
    """Concrete implementation of BaseModel for Google's Gemini language models.

    This class provides a wrapper for Google's Gemini API, handling API key
    management, message history, and model configuration. It uses OpenAI's client
    library for compatibility with OpenAI-style API interfaces. The class automatically
    manages environment variables for API key storage.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
        """Initializes the GeminiModel with API credentials and configuration.

        Sets up the Gemini client with the provided or environment-stored API key.
        If an API key is provided and differs from the current environment variable,
        it will be saved to the .env file. Initializes the conversation history with
        an optional system prompt.

        Args:
            api_key (Optional[str], optional): Google Gemini API key for authentication.
                If not provided, attempts to use the GEMINI_API_KEY environment variable.
                Defaults to None.
            system_prompt (Optional[str], optional): System prompt to initialize the
                conversation context. If provided, it will be added as the first message
                with role 'system'. Defaults to None.
            model_type (Optional[str], optional): Identifier for the specific Gemini model
                to use (e.g., "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp").
                Defaults to "gemini-2.5-pro" if not specified.

        Raises:
            ValueError: If no API key is provided and GEMINI_API_KEY environment
                variable is not set.

        Note:
            The API key will be automatically saved to a .env file if it differs from
            the current environment variable value. This implementation uses OpenAI's
            client library for API compatibility.
        """
        super().__init__()
        if api_key is not None:
            if os.getenv("GEMINI_API_KEY") != api_key:
                env_path = create_env_file()
                set_key(env_path, key_to_set="GEMINI_API_KEY", value_to_set=api_key)
            self.api_key = api_key
        elif os.getenv("GEMINI_API_KEY"):
            self.api_key = os.getenv("GEMINI_API_KEY")
        else:
            raise ValueError("API Key is required for GeminiModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model_type = model_type
        if self.model_type is None:
            self.model_type = "gemini-2.5-pro"
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model_type,
        messages=self.messages,
        **generate_kwargs
        )
        """Executes a Gemini chat completion API call and returns the response.

        Makes a chat completion request to the Google Gemini API using the current
        conversation history and returns both the generated content and token usage
        information.

        Args:
            **generate_kwargs: Additional keyword arguments passed to the Gemini API
                for controlling generation behavior. Common options include:
                - temperature (float): Sampling temperature (0.0 to 2.0)
                - max_tokens (int): Maximum number of tokens to generate
                - top_p (float): Nucleus sampling parameter
                - top_k (int): Top-k sampling parameter
                - stop (Union[str, List[str]]): Stop sequences

        Returns:
            tuple: A tuple containing:
                - str: The generated message content from the model
                - int: Total number of tokens used in the API call (prompt + completion)
        """
        return completion.choices[0].message.content, completion.usage.total_tokens


class HFModel(BaseModel):
    """Concrete implementation of BaseModel for Hugging Face's hosted language models.

    This class provides a wrapper for Hugging Face's Inference API, handling API token
    management, message history, and model configuration. It uses Hugging Face's
    InferenceClient to interact with models hosted on the Hugging Face Hub. The class
    automatically manages environment variables for API token storage.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
        """Initializes the HFModel with API credentials and configuration.

        Sets up the Hugging Face InferenceClient with the provided or environment-stored
        API token. If a token is provided and differs from the current environment variable,
        it will be saved to the .env file. Initializes the conversation history with
        an optional system prompt.

        Args:
            api_key (Optional[str], optional): Hugging Face API token for authentication.
                If not provided, attempts to use the HF_TOKEN environment variable.
                Defaults to None.
            system_prompt (Optional[str], optional): System prompt to initialize the
                conversation context. If provided, it will be added as the first message
                with role 'system'. Defaults to None.
            model_type (Optional[str], optional): Identifier for the specific Hugging Face
                model to use (e.g., "meta-llama/Llama-3.1-70B-Instruct",
                "mistralai/Mixtral-8x7B-Instruct-v0.1"). Defaults to
                "Qwen/Qwen2.5-Coder-32B-Instruct" if not specified.

        Raises:
            ValueError: If no API token is provided and HF_TOKEN environment
                variable is not set.

        Note:
            The API token will be automatically saved to a .env file if it differs from
            the current environment variable value. This implementation uses Hugging Face's
            InferenceClient to access models hosted on the Hugging Face Hub.
        """
        super().__init__()
        if api_key is not None:
            if os.getenv("HF_TOKEN") != api_key:
                env_path = create_env_file()
                set_key(env_path, key_to_set="HF_TOKEN", value_to_set=api_key)
            self.api_key = api_key
        elif os.getenv("HF_TOKEN"):
            self.api_key = os.getenv("HF_TOKEN")
        else:
            raise ValueError("API Key is required for HFModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model_type = model_type
        if self.model_type is None:
            self.model_type = "Qwen/Qwen2.5-Coder-32B-Instruct"
        self.client = InferenceClient(
            model=self.model_type,
            api_key=self.api_key,
        )
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model_type,
        messages=self.messages,
        **generate_kwargs
        )
        """Executes a Hugging Face Inference API call and returns the response.

        Makes a chat completion request to the Hugging Face Inference API using the
        current conversation history and returns both the generated content and token
        usage information.

        Args:
            **generate_kwargs: Additional keyword arguments passed to the Hugging Face
                Inference API for controlling generation behavior. Common options include:
                - temperature (float): Sampling temperature (0.0 to 2.0)
                - max_tokens (int): Maximum number of tokens to generate
                - top_p (float): Nucleus sampling parameter
                - top_k (int): Top-k sampling parameter
                - repetition_penalty (float): Penalty for repeating tokens
                - stop (Union[str, List[str]]): Stop sequences

        Returns:
            tuple: A tuple containing:
                - str: The generated message content from the model
                - int: Total number of tokens used in the API call (prompt + completion)

        Note:
            The available parameters may vary depending on the specific model being used.
            Refer to the model's documentation on Hugging Face Hub for model-specific options.
        """
        return completion.choices[0].message.content, completion.usage.total_tokens


MODEL_NAMES={
    "openai": OpenAIModel,
    "groq": GroqModel,
    "xai": GrokModel,
    "deepseek": DeepseekModel,
    "anthropic": ClaudeModel,
    "google": GeminiModel,
    "huggingface": HFModel
}