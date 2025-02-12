import openai
import groq
import anthropic
from typing import Optional
from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv


load_dotenv()


class BaseModel(ABC):
    """Wrapper class for Model's API."""
    def __init__(
        self,
        system_prompt: Optional[str] = None, 
        model: Optional[str] = None
    ):
        self.system_prompt = system_prompt
        self.model = model
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
        self.messages.append({"role": "assistant", "content": result})
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
        model: Optional[str] = None
    ):
        super().__init__()
        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is required for OpenAIModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model = model
        if self.model is None:
            self.model = "gpt-4o"
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=self.messages,
        **generate_kwargs
        )
        return completion.choices[0].message.content


class GroqModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model: Optional[str] = None
    ):
        super().__init__()
        self.api_key = api_key if api_key else os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is required for GroqModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model = model
        if self.model is None:
            self.model = "llama-3.3-70b-versatile"
        self.client = groq.Groq(api_key=self.api_key)
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=self.messages,
        **generate_kwargs
        )
        return completion.choices[0].message.content
    

class GrokModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model: Optional[str] = None
    ):
        super().__init__()
        self.api_key = api_key if api_key else os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is required for GrokModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model = model
        if self.model is None:
            self.model = "grok-2-latest"
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
        )
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=self.messages,
        **generate_kwargs
        )
        return completion.choices[0].message.content
    

class DeepseekModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model: Optional[str] = None
    ):
        super().__init__(system_prompt, model)
        self.api_key = api_key if api_key else os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is required for DeepseekModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model = model
        if self.model is None:
            self.model = "deepseek-chat"
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )
    
    def execute(self, **generate_kwargs):
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=self.messages,
        **generate_kwargs
        )
        return completion.choices[0].message.content
    

class ClaudeModel(BaseModel):
    def __init__(
        self, 
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None, 
        model: Optional[str] = None
    ):
        super().__init__(system_prompt, model)
        self.api_key = api_key if api_key else os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is required for ClaudeModel.")
        self.messages = []
        self.system_prompt = system_prompt
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.model = model
        if self.model is None:
            self.model = "claude-3-5-sonnet-20241022"
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
        )
    
    def execute(self, **generate_kwargs):
        completion = self.client.messages.create(
        model=self.model,
        messages=self.messages,
        **generate_kwargs
        )
        return completion.content[0].text


MODEL_NAMES={
    "openai": OpenAIModel,
    "groq": GroqModel,
    "xai": GrokModel,
    "deepseek": DeepseekModel,
    "anthropic": ClaudeModel
}