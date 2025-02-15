from rich import print, box
from rich.panel import Panel
import re
import json
from .system_prompt import TOOL_CALLING_SYSTEM_PROMPT
from .models import MODEL_NAMES
from typing import List, Optional, Callable
from .actions import pipeline_tool


class MusubiAgent:
    def __init__(
        self,
        actions: List[Callable],
        model_source: str = "openai",
        api_key: Optional[str] = None,
        model_type: Optional[str] = None,
        max_turns: Optional[int] = 10
    ):
        self.actions = actions
        self.actions_dict = {action.__name__: action for action in actions}
        self.max_turns = max_turns
        self.system_prompt = self.get_system_prompt(self.actions)
        if model_source.lower() not in MODEL_NAMES.keys():
            raise ValueError("Didn't get appropriate model source."
                             "The model source should be one of `{}`".format(str(list(MODEL_NAMES.keys()))))
        self.model = MODEL_NAMES[model_source.lower()](
            api_key = api_key,
            system_prompt = self.system_prompt,
            model_type = model_type
        )
        self.model_type = self.model.model_type

    def run(
        self,
        prompt: str,
        **generate_kwargs
    ):
        done = False
        step = 1
        while not done or step <= self.max_turns:
            res, step_tokens = self.model(prompt, **generate_kwargs) 
            action_title = "Action {}".format(str(step))
            action_subtitle = "model_type: {}, step_token_use: {}".format(self.model_type, step_tokens)
            print(Panel(
                res, 
                title=action_title, 
                box=box.DOUBLE_EDGE, 
                subtitle=action_subtitle,
                border_style="yellow1",
                subtitle_align="left"
            ))
            chosen_action_dict = self.extract_action_dict(res)
            chosen_action_name, chosen_action_arguments = chosen_action_dict["action_name"], chosen_action_dict["action_arguments"]
            observation = self.actions_dict[chosen_action_name](**chosen_action_arguments)
            prompt = "\n<observation>\n" + str(observation) + "\n</observation>\n"
            observation_title = "Observe {}".format(str(step))
            observation_subtitle = "action_name: {}, action_arguments: {}".format(chosen_action_name, str(chosen_action_arguments))
            print(Panel(
                str(observation), 
                title=observation_title, 
                box=box.DOUBLE_EDGE, 
                subtitle=observation_subtitle,
                border_style="green1",
                subtitle_align="left"
            ))
            if chosen_action_name == "final_answer":
                done = True
                return observation
            step += 1

    def get_system_prompt(
        self,
        actions: List[Callable]
    ):
        template = TOOL_CALLING_SYSTEM_PROMPT
        values = {
            "pipeline_tool_description": pipeline_tool.__doc__, 
            "action_names": ", ".join([func.__name__ for func in actions]), 
            "action_descriptions": "\n".join([str(i+1) + ". " + func.__name__ + ":\n" + func.__doc__ for i, func in enumerate(actions)])
        }
        for key, value in values.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template.strip()
    
    def extract_action_dict(
        self,
        text: str
    ):
        pattern = r'<action>(.*?)</action>'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            try:
                dict_str = match.group(1)
                return json.loads(dict_str)
            except json.JSONDecodeError:
                return None
        return None
