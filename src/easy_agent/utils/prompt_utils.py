import inspect
import functools
from typing import Callable, Optional, Type, TypeVar, Union, Any, cast
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.runnables import (
    Runnable
)
from langchain_core.language_models import (
    LanguageModelInput,
)
from langgraph.utils.runnable import RunnableCallable
from easy_agent.agents.react_agents import AgentState, AgentStatePydantic
from easy_agent.core.state import get_state_value

StateSchema = TypeVar("StateSchema", bound=Union[AgentState, AgentStatePydantic])
StateSchemaType = Type[StateSchema]

PROMPT_RUNNABLE_NAME = "Prompt"

Prompt = Union[
    SystemMessage,
    str,
    Callable[[StateSchema], LanguageModelInput],
    Runnable[StateSchema, LanguageModelInput],
]
F = TypeVar("F", bound=Callable[..., Any])

def get_prompt_runnable(prompt: Optional[Prompt]) -> Runnable:
    prompt_runnable: Runnable
    if prompt is None:
        prompt_runnable = RunnableCallable(
            lambda state: get_state_value(state, "messages"), name=PROMPT_RUNNABLE_NAME
        )
    elif isinstance(prompt, str):
        _system_message: BaseMessage = SystemMessage(content=prompt)
        prompt_runnable = RunnableCallable(
            lambda state: [_system_message] + get_state_value(state, "messages"),
            name=PROMPT_RUNNABLE_NAME,
        )
    elif isinstance(prompt, SystemMessage):
        prompt_runnable = RunnableCallable(
            lambda state: [prompt] + get_state_value(state, "messages"),
            name=PROMPT_RUNNABLE_NAME,
        )
    elif inspect.iscoroutinefunction(prompt):
        prompt_runnable = RunnableCallable(
            None,
            prompt,
            name=PROMPT_RUNNABLE_NAME,
        )
    elif callable(prompt):
        prompt_runnable = RunnableCallable(
            prompt,
            name=PROMPT_RUNNABLE_NAME,
        )
    elif isinstance(prompt, Runnable):
        prompt_runnable = prompt
    else:
        raise ValueError(f"Got unexpected type for `prompt`: {type(prompt)}")

    return prompt_runnable


def convert_modifier_to_prompt(func: F) -> F:
    """Decorator that converts state_modifier kwarg to prompt kwarg."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        prompt = kwargs.get("prompt")
        state_modifier = kwargs.pop("state_modifier", None)
        if sum(p is not None for p in (prompt, state_modifier)) > 1:
            raise ValueError(
                "Expected only one of (prompt, state_modifier), got multiple values"
            )

        if state_modifier is not None:
            prompt = state_modifier

        kwargs["prompt"] = prompt
        return func(*args, **kwargs)

    return cast(F, wrapper)