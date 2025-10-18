from rich import print, box
from rich.panel import Panel
import ast
from typing import List, Optional, Callable
from abc import ABC, abstractmethod
from .system_prompt import PIPELINE_TOOL_SYSTEM_PROMPT, GENERAL_ACTIONS_SYSTEM_PROMPT, MUSUBI_AGENT_PROMPT, SCHEDULER_ACTIONS_SYSTEM_PROMPT
from .models import MODEL_NAMES
from .actions.pipeline_tool_actions import pipeline_tool


class BaseAgent(ABC):
    """Base class for agent implementations that interact with language models and execute actions.

    This abstract base class provides the core functionality for agents that can:
    - Execute a series of actions through language model interactions
    - Parse and process action dictionaries from model responses
    - Manage conversation turns with configurable limits
    """
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
        """Initializes the BaseAgent with actions and model configuration.

        Args:
            actions (List[Callable]): List of callable functions that the agent can execute.
            model_source (str, optional): Source of the language model. Must be one of the keys
                in MODEL_NAMES. Defaults to "openai".
            api_key (Optional[str], optional): API key for the model service. Defaults to None.
            model_type (Optional[str], optional): Specific model type/version to use. 
                Defaults to None.
            max_turns (Optional[int], optional): Maximum number of turns in a conversation. 
                Defaults to 10.

        Raises:
            ValueError: If model_source is not in MODEL_NAMES keys.
        """
        start_idx = text.find("<action>")
        end_idx = text.find("</action>")
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("Could not find <action> tags in the text")
            
        # Extract the string including dictionary string
        action_content = text[(start_idx + len("<action>")):end_idx]
        action_content = action_content.replace("\\n", "\n")
        action_content = action_content.strip()
        
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
        """Executes the agent's main logic with the given prompt.

        Abstract method that must be implemented by subclasses to define the
        agent's execution behavior.

        Args:
            prompt (str): Input prompt or query for the agent to process.
            **generate_kwargs: Additional keyword arguments for text generation.

        Returns:
            Implementation-dependent return value.
        """
        ...

    @abstractmethod
    def get_system_prompt(
        self,
        actions: List[Callable]
    ):
        """Generates a system prompt based on available actions.

        Abstract method that must be implemented by subclasses to create an
        appropriate system prompt that describes the agent's capabilities.

        Args:
            actions (List[Callable]): List of available action functions.

        Returns:
            str: Generated system prompt.
        """
        ...


class MusubiAgent:
    """Agent that delegates tasks to specialized candidate agents based on LLM reasoning.

    MusubiAgent acts as a coordinator that analyzes user prompts and selects the most
    appropriate candidate agent to handle the task. It uses a language model to reason
    about which agent is best suited for a given prompt, then delegates execution to
    that agent.
    """
    def __init__(
        self, 
        candidates: List[Callable],
        model_source: str = "openai",
        api_key: Optional[str] = None,
        model_type: Optional[str] = None
    ):
        """Initializes the MusubiAgent with candidate agents and model configuration.

        Args:
            candidates (List[Callable]): List of candidate agent instances that can be
                delegated to. Each candidate should have a class name and docstring
                that describes its capabilities.
            model_source (str, optional): Source of the language model. Must be one of
                the keys in MODEL_NAMES. Defaults to "openai".
            api_key (Optional[str], optional): API key for the model service. 
                Defaults to None.
            model_type (Optional[str], optional): Specific model type/version to use.
                Defaults to None.

        Raises:
            ValueError: If model_source is not in MODEL_NAMES keys.
        """
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
        """Executes task delegation by reasoning about and selecting the best candidate agent.

        Analyzes the input prompt using the language model to determine which candidate
        agent is most suitable, then delegates the task to that agent. Displays reasoning
        and assignment information in formatted panels.

        Args:
            prompt (str): Input prompt or query to be processed.
            temperature (float, optional): Sampling temperature for model generation.
                Lower values make output more deterministic. Defaults to 0.3.
            **generate_kwargs: Additional keyword arguments passed to the model's
                generation method.

        Raises:
            ValueError: If action tags cannot be found or parsed from model response.
            KeyError: If the selected agent type is not found in candidates_dict.
        """
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
        """Extracts and parses an action dictionary from text enclosed in <action> tags.

        Searches for content between <action> and </action> tags, then parses it as
        a Python dictionary using ast.literal_eval for safe evaluation.

        Args:
            text (str): Input text containing <action> tags with dictionary content.

        Returns:
            dict: Parsed action dictionary containing at least 'action_name' and 
                'agent_type' keys.

        Raises:
            ValueError: If <action> tags are not found in the text.
            ValueError: If the content cannot be parsed as a valid Python dictionary.
        """
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
        """Generates a system prompt describing available candidate agents.

        Creates a formatted system prompt by populating a template with candidate agent
        names and descriptions extracted from their class names and docstrings.

        Args:
            candidates (List[Callable]): List of candidate agent instances. Each must
                have a __class__.__name__ and __class__.__doc__ attribute.

        Returns:
            str: Formatted system prompt with agent names and descriptions.
        """
        template = MUSUBI_AGENT_PROMPT
        values = {
            "agent_names": ", ".join([candidate.__class__.__name__ for candidate in candidates]), 
            "agents_description": "\n".join([str(i+1) + ". " + candidate.__class__.__name__ + ":\n" + candidate.__class__.__doc__ for i, candidate in enumerate(candidates)])
        }
        for key, value in values.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template.strip()


class PipelineAgent(BaseAgent):
    """A pipeline-based agent that executes actions in a stepwise manner to get arguments for `pipeline_tool` function using a language model.
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
        """Initializes the PipelineAgent with actions and model configuration.

        Args:
            actions (List[Callable]): List of callable functions that the agent can execute
                during the pipeline process. Should include a 'final_answer' action.
            model_source (str, optional): Source of the language model. Must be one of the keys
                in MODEL_NAMES. Defaults to "openai".
            api_key (Optional[str], optional): API key for the model service. Defaults to None.
            model_type (Optional[str], optional): Specific model type/version to use. 
                Defaults to None.
            max_turns (Optional[int], optional): Maximum number of execution steps before
                terminating. Defaults to 10.

        Raises:
            ValueError: If model_source is not in MODEL_NAMES keys.
        """
        super().__init__(actions, model_source, api_key, model_type, max_turns)

    def execute(
        self,
        prompt: str,
        temperature: float = 0.3,
        **generate_kwargs
    ):
        """Executes the pipeline agent's iterative action loop until completion.

        Processes the input prompt through multiple steps, where each step involves:
        1. Generating a response from the language model
        2. Extracting and parsing the chosen action
        3. Executing the action and observing results
        4. Updating the prompt with observations for the next step

        The loop terminates when either the 'final_answer' action is called or the
        maximum number of turns is reached. Upon completion with 'final_answer',
        the pipeline_tool is executed with the final arguments.

        Args:
            prompt (str): Input prompt or query to be processed through the pipeline.
            temperature (float, optional): Sampling temperature for model generation.
                Lower values make output more deterministic. Defaults to 0.3.
            **generate_kwargs: Additional keyword arguments passed to the model's
                generation method.

        Returns:
            dict: The final action arguments when 'final_answer' is called, containing
                parameters for the pipeline_tool function.

        Raises:
            ValueError: If action tags cannot be found or parsed from model response.
            KeyError: If the selected action name is not found in actions_dict.

        Note:
            Displays formatted panels for each action step and observation, showing:
            - Action reasoning and token usage
            - Chosen action name and arguments
            - Observation results
        """
        done = False
        step = 1
        while (not done) or (step <= self.max_turns):
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
                print()
                pipeline_tool(**chosen_action_arguments)
                done = True
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
            step += 1

    def get_system_prompt(
        self,
        actions: List[Callable]
    ):
        """Generates a system prompt for the pipeline agent based on available actions.

        Creates a formatted system prompt by populating the PIPELINE_TOOL_SYSTEM_PROMPT
        template with pipeline_tool description and available action descriptions.

        Args:
            actions (List[Callable]): List of available action functions. Each must have
                a __name__ attribute and __doc__ docstring.

        Returns:
            str: Formatted system prompt with pipeline_tool description, action names,
                and detailed action descriptions for guiding the language model.
        """
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
    """A general-purpose agent that executes predefined actions using a language model.

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
        """Initializes the GeneralAgent with actions and model configuration.

        Args:
            actions (List[Callable]): List of callable functions that the agent can execute.
                May include special actions like 'domain_analyze' and 'type_analyze' that
                return structured results.
            model_source (str, optional): Source of the language model. Must be one of the keys
                in MODEL_NAMES. Defaults to "openai".
            api_key (Optional[str], optional): API key for the model service. Defaults to None.
            model_type (Optional[str], optional): Specific model type/version to use. 
                Defaults to None.

        Raises:
            ValueError: If model_source is not in MODEL_NAMES keys.
        """
        super().__init__(actions, model_source, api_key, model_type)

    def execute(
        self,
        prompt: str,
        temperature: float = 0.3,
        **generate_kwargs
    ):
        """Executes a single action based on the input prompt.

        Processes the prompt through the following steps:
        1. Generates a response from the language model to select an action
        2. Extracts and parses the chosen action and its arguments
        3. Executes the selected action
        4. Displays results in a formatted panel

        For analysis actions ('domain_analyze', 'type_analyze'), displays a detailed
        completion report with key-value results. For other actions, displays a simple
        completion message.

        Args:
            prompt (str): Input prompt or query describing the task to be executed.
            temperature (float, optional): Sampling temperature for model generation.
                Lower values make output more deterministic. Defaults to 0.3.
            **generate_kwargs: Additional keyword arguments passed to the model's
                generation method.

        Raises:
            ValueError: If action tags cannot be found or parsed from model response.
            KeyError: If the selected action name is not found in actions_dict.

        Note:
            Displays three types of formatted panels:
            - Action panel: Shows the model's reasoning and token usage
            - Observation panel: Shows the action being executed
            - Completion/Report panel: Shows task completion status and results
        """
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
        """Generates a system prompt for the general agent based on available actions.

        Creates a formatted system prompt by populating the GENERAL_ACTIONS_SYSTEM_PROMPT
        template with action names and descriptions to guide the language model in
        selecting appropriate actions.

        Args:
            actions (List[Callable]): List of available action functions. Each must have
                a __name__ attribute and __doc__ docstring.

        Returns:
            str: Formatted system prompt with action names and detailed descriptions
                for guiding action selection.
        """
        template = GENERAL_ACTIONS_SYSTEM_PROMPT
        values = {
            "action_names": ", ".join([func.__name__ for func in actions]), 
            "general_action_descriptions": "\n".join([str(i+1) + ". " + func.__name__ + ":\n" + func.__doc__ for i, func in enumerate(actions)])
        }
        for key, value in values.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template.strip()
    

class SchedulerAgent(BaseAgent):
    """A specialized assistant for implementing and managing scheduled tasks.

    The Scheduler Agent handles all aspects of task scheduling management, including 
    creating, monitoring, pausing, and removing scheduled tasks. It follows a structured 
    reasoning process before taking actions and provides formatted feedback throughout 
    the execution process.
    """
    def __init__(
        self, 
        actions: List[Callable],
        model_source: str = "openai",
        api_key: Optional[str] = None,
        model_type: Optional[str] = None,
    ):
        """Initializes the SchedulerAgent with scheduling actions and model configuration.

        Args:
            actions (List[Callable]): List of callable functions for task scheduling
                operations. Typically includes actions for creating, monitoring, pausing,
                and removing scheduled tasks.
            model_source (str, optional): Source of the language model. Must be one of the keys
                in MODEL_NAMES. Defaults to "openai".
            api_key (Optional[str], optional): API key for the model service. Defaults to None.
            model_type (Optional[str], optional): Specific model type/version to use. 
                Defaults to None.

        Raises:
            ValueError: If model_source is not in MODEL_NAMES keys.
        """
        super().__init__(actions, model_source, api_key, model_type)

    def execute(
        self,
        prompt: str,
        temperature: float = 0.3,
        **generate_kwargs
    ):
        """Executes a scheduling action based on the input prompt.

        Processes the prompt through the following steps:
        1. Generates a response from the language model to determine the appropriate
        scheduling action
        2. Extracts and parses the chosen action and its arguments
        3. Executes the selected scheduling action
        4. Displays completion status

        Args:
            prompt (str): Input prompt or query describing the scheduling task to be
                executed (e.g., create a daily task, pause task X, show all tasks).
            temperature (float, optional): Sampling temperature for model generation.
                Lower values make output more deterministic. Defaults to 0.3.
            **generate_kwargs: Additional keyword arguments passed to the model's
                generation method.

        Raises:
            ValueError: If action tags cannot be found or parsed from model response.
            KeyError: If the selected action name is not found in actions_dict.

        Note:
            Displays three types of formatted panels:
            
            - Action panel: Shows the model's reasoning and token usage (yellow border)
            - Observation panel: Shows the action being executed (green border)
            - Completion panel: Shows task completion status (cyan border)
        """
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
        """Generates a system prompt for the scheduler agent based on available actions.

        Creates a formatted system prompt by populating the SCHEDULER_ACTIONS_SYSTEM_PROMPT
        template with scheduling action names and descriptions to guide the language model
        in managing scheduled tasks.

        Args:
            actions (List[Callable]): List of available scheduling action functions. Each
                must have a __name__ attribute and __doc__ docstring describing its
                scheduling functionality.

        Returns:
            str: Formatted system prompt with action names and detailed descriptions
                for guiding scheduling task management.
        """
        template = SCHEDULER_ACTIONS_SYSTEM_PROMPT
        values = {
            "action_names": ", ".join([func.__name__ for func in actions]), 
            "scheduler_action_descriptions": "\n".join([str(i+1) + ". " + func.__name__ + ":\n" + func.__doc__ for i, func in enumerate(actions)])
        }
        for key, value in values.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template.strip()