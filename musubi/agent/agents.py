from rich import print, box
from rich.panel import Panel
import ast
from typing import List, Optional, Callable
from abc import ABC, abstractmethod
from .system_prompt import PIPELINE_TOOL_SYSTEM_PROMPT, GENERAL_ACTIONS_SYSTEM_PROMPT, MUSUBI_AGENT_PROMPT
from .models import MODEL_NAMES
from .actions.pipeline_tool_actions import pipeline_tool


class BaseAgent(ABC):
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

    def extract_action_dict(self, text: str):
        start_idx = text.find("<action>")
        end_idx = text.find("</action>")
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("Could not find <action> tags in the text")
            
        # Extract the string including dictionary string
        action_content = text[start_idx + len("<action>"):end_idx].strip()
        
        # Parse the string into a Python dictionary
        try:
            action_dict = ast.literal_eval(action_content)
            return action_dict
        except Exception as e:
            raise ValueError(f"Unexpected error during parsing: {str(e)}")
        
    @abstractmethod
    def execute(
        self,
        prompt: str,
        **generate_kwargs
    ):
        ...

    @abstractmethod
    def get_system_prompt(
        self,
        actions: List[Callable]
    ):
        ...


class MusubiAgent:
    def __init__(
        self, 
        candidates: List[Callable],
        model_source: str = "openai",
        api_key: Optional[str] = None,
        model_type: Optional[str] = None
    ):
        self.candidates = candidates
        self.candidates_dict = {candidate.__class__.__name__: candidate for candidate in candidates}
        self.system_prompt = self.get_system_prompt(self.candidates)
        if model_source.lower() not in MODEL_NAMES.keys():
            raise ValueError("Didn't get appropriate model source."
                             "The model source should be one of `{}`".format(str(list(MODEL_NAMES.keys()))))
        self.model = MODEL_NAMES[model_source.lower()](
            api_key = api_key,
            system_prompt = self.system_prompt,
            model_type = model_type
        )

        self.model_type = self.model.model_type

    def execute(
        self,
        prompt: str,
        temperature: float = 0.3,
        **generate_kwargs
    ):
        res, step_tokens = self.model(prompt, temperature=temperature, **generate_kwargs) 
        action_subtitle = "model_type: {}, step_token_use: {}".format(self.model_type, step_tokens)
        print(Panel(
            res, 
            title="Reasoning...", 
            box=box.DOUBLE_EDGE, 
            subtitle=action_subtitle,
            border_style="orange1",
            subtitle_align="left"
        ))
        chosen_action_dict = self.extract_action_dict(res)
        _, chosen_candidates = chosen_action_dict["action_name"], chosen_action_dict["agent_type"]
        print(Panel(
                "Executing assigned task. The assigned agent is {}.".format(str(chosen_candidates)),
                title="Assignment",
                box=box.DOUBLE_EDGE, 
                border_style="red1",
                subtitle_align="left"
            ))
        chosen_agent = self.candidates_dict[chosen_candidates]
        chosen_agent.execute(prompt)
            
    def extract_action_dict(self, text: str):
        start_idx = text.find("<action>")
        end_idx = text.find("</action>")
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("Could not find <action> tags in the text")
            
        # Extract the string including dictionary string
        action_content = text[start_idx + len("<action>"):end_idx].strip()
        
        # Parse the string into a Python dictionary
        try:
            action_dict = ast.literal_eval(action_content)
            return action_dict
        except Exception as e:
            raise ValueError(f"Unexpected error during parsing: {str(e)}")

    def get_system_prompt(
        self,
        candidates: List[Callable]
    ):
        template = MUSUBI_AGENT_PROMPT
        values = {
            "agent_names": ", ".join([candidate.__class__.__name__ for candidate in candidates]), 
            "agents_description": "\n".join([str(i+1) + ". " + candidate.__class__.__name__ + ":\n" + candidate.__class__.__doc__ for i, candidate in enumerate(candidates)])
        }
        for key, value in values.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template.strip()


class PipelineAgent(BaseAgent):
    """
    A pipeline-based agent that executes actions in a stepwise manner to get arguments for `pipeline_tool` function using a language model.
    The `pipeline_tool` function add new website into config json file and scrape website articles.

    This agent processes a given prompt through an iterative execution cycle, interacting 
    with predefined actions and a language model until a final answer is reached or the 
    maximum number of steps is exceeded.
    """
    def __init__(
        self, 
        actions: List[Callable],
        model_source: str = "openai",
        api_key: Optional[str] = None,
        model_type: Optional[str] = None,
        max_turns: Optional[int] = 10
    ):
        super().__init__(actions, model_source, api_key, model_type, max_turns)

    def execute(
        self,
        prompt: str,
        temperature: float = 0.3,
        **generate_kwargs
    ):
        done = False
        step = 1
        while not done or step <= self.max_turns:
            res, step_tokens = self.model(prompt, temperature=temperature, **generate_kwargs) 
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
            observation_title = "Observation {}".format(str(step))
            observation_subtitle = "action_name: {}, action_arguments: {}".format(chosen_action_name, str(chosen_action_arguments))
            if chosen_action_name == "final_answer":
                done = True
                print(Panel(
                    "Final_result:\n" + str(chosen_action_arguments), 
                    title=observation_title, 
                    box=box.DOUBLE_EDGE, 
                    subtitle=observation_subtitle,
                    border_style="green1",
                    subtitle_align="left"
                ))
                return chosen_action_arguments
            observation = self.actions_dict[chosen_action_name](**chosen_action_arguments)
            prompt = "\n<observation>\n" + str(observation) + "\n</observation>\n"
            
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
        template = PIPELINE_TOOL_SYSTEM_PROMPT
        values = {
            "pipeline_tool_description": pipeline_tool.__doc__, 
            "action_names": ", ".join([func.__name__ for func in actions]), 
            "action_descriptions": "\n".join([str(i+1) + ". " + func.__name__ + ":\n" + func.__doc__ for i, func in enumerate(actions)])
        }
        for key, value in values.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template.strip()


class GeneralAgent(BaseAgent):
    """
    A general-purpose agent that executes predefined actions using a language model.

    This agent processes a given prompt, selects an appropriate action, and executes it. 
    It supports different types of analyses and general task execution.
    """
    def __init__(
        self, 
        actions: List[Callable],
        model_source: str = "openai",
        api_key: Optional[str] = None,
        model_type: Optional[str] = None,
    ):
        super().__init__(actions, model_source, api_key, model_type)

    def execute(
        self,
        prompt: str,
        temperature: float = 0.3,
        **generate_kwargs
    ):
        res, step_tokens = self.model(prompt, temperature=temperature, **generate_kwargs) 
        action_title = "Action"
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
        observation_title = "Observation"
        observation_subtitle = "action_name: {}, action_arguments: {}".format(chosen_action_name, str(chosen_action_arguments))
        print(Panel(
                "Executing assigned task.",
                title=observation_title, 
                box=box.DOUBLE_EDGE, 
                subtitle=observation_subtitle,
                border_style="green1",
                subtitle_align="left"
            ))
        if chosen_action_name in ["domain_analyze", "type_analyze"]:
            res = self.actions_dict[chosen_action_name](**chosen_action_arguments)
            report = ", ".join(f"{k}: {v}" for k, v in res.items())
            print(Panel(
                "The task is finished!\n{}".format(report),
                title="Completion Report", 
                box=box.DOUBLE_EDGE, 
                border_style="cyan1",
            ))
        else:
            self.actions_dict[chosen_action_name](**chosen_action_arguments)
            print(Panel(
                    "The task is finished!",
                    title="Completion", 
                    box=box.DOUBLE_EDGE, 
                    border_style="cyan1",
                ))

    def get_system_prompt(
        self,
        actions: List[Callable]
    ):
        template = GENERAL_ACTIONS_SYSTEM_PROMPT
        values = {
            "action_names": ", ".join([func.__name__ for func in actions]), 
            "general_action_descriptions": "\n".join([str(i+1) + ". " + func.__name__ + ":\n" + func.__doc__ for i, func in enumerate(actions)])
        }
        for key, value in values.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template.strip()