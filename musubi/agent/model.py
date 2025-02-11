import openai
import groq
from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv


load_dotenv()


class OpenAIModel:
    '''
    Wrapper class for OpenAI's Chat API. Designed by Simon
    '''
    def __init__(
        self,
        openai_api: str = None,
        system_prompt: str = None, 
        model: str = None
    ):
        if openai_api is not None:
            openai_api = openai_api
        else:
            openai_api = openai.api_key = os.getenv('OPENAI_API_KEY')
        self.system_prompt = system_prompt
        self.model = model
        self.messages = []
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        if self.model is None:
            self.model = "chatgpt-4o-latest"

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.exceute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def exceute(self):
        completion = openai.chat.completions.create(
        model=self.model,
        messages=self.messages
        )
        response = completion.choices[0].message.content
        return response