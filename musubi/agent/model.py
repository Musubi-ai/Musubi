import openai
import os
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


class OpenAIModel:
    '''
    Wrapper class for OpenAI's Chat API. Designed by Simon
    '''
    def __init__(
        self, 
        system_prompt: str = None, 
        model_api: str = None
    ):
        self.system_prompt = system_prompt
        self.model_api = model_api
        self.messages = []
        if self.system_prompt is not None:
            self.messages.append({"role": "system", "content": self.system_prompt})
        if self.model_api is None:
            self.model_api = "chatgpt-4o-latest"

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.exceute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def exceute(self):
        completion = openai.chat.completions.create(
        model=self.model_api,
        messages=self.messages
        )
        response = completion.choices[0].message.content
        return response