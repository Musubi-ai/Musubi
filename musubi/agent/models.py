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
    """Wrapper class for Model's API."""
    def __init__(
        self,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
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
        if not isinstance(message, str):
            raise ValueError("The message should be string.")
        self.messages.append({"role": "user", "content": message})
        result = self.execute(**generate_kwargs)
        self.messages.append({"role": "assistant", "content": str(result)})
        return result
    
    @abstractmethod
    def execute(self):
        """Abstract method for executing API calls."""
        pass


class OpenAIModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
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
        return completion.choices[0].message.content, completion.usage.total_tokens


class GroqModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
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
        return completion.choices[0].message.content, completion.usage.total_tokens
    

class GrokModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
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
        return completion.choices[0].message.content, completion.usage.total_tokens
    

class DeepseekModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
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
        completion = self.client.chat.completions.create(
        model=self.model_type,
        messages=self.messages,
        **generate_kwargs
        )
        return completion.choices[0].message.content, completion.usage.total_tokens
    

class ClaudeModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
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
        return completion.content[0].text, completion.usage.total_tokens


class GeminiModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
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
        return completion.choices[0].message.content, completion.usage.total_tokens


class HFModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model_type: Optional[str] = None
    ):
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