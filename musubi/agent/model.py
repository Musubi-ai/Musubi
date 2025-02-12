import openai
import groq
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
        message: str
    ):
        if not isinstance(message, str):
            raise ValueError("The message should be string.")
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    @abstractmethod
    def execute(self):
        """Abstract method for executing API calls."""
        pass


class OpenAIModel(BaseModel):
    def __init__(
        self, 
        api_key: str,
        system_prompt: Optional[str] = None, 
        model: Optional[str] = None
    ):
        super().__init__(system_prompt, model)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is required for OpenAIModel.")
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