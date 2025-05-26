"""
智能体状态管理
"""

from typing import Any, TypedDict, Union, Callable, TypeVar, Type
from pydantic import BaseModel
from typing_extensions import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep, RemainingSteps


StructuredResponse = Union[dict, BaseModel]
StructuredResponseSchema = Union[dict, type[BaseModel]]
F = TypeVar("F", bound=Callable[..., Any])


class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]

    is_last_step: IsLastStep

    remaining_steps: RemainingSteps


class AgentStatePydantic(BaseModel):
    """The state of the agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]

    remaining_steps: RemainingSteps = 25


class AgentStateWithStructuredResponse(AgentState):
    """The state of the agent with a structured response."""

    structured_response: StructuredResponse


class AgentStateWithStructuredResponsePydantic(AgentStatePydantic):
    """The state of the agent with a structured response."""

    structured_response: StructuredResponse


StateSchema = TypeVar("StateSchema", bound=Union[AgentState, AgentStatePydantic])
StateSchemaType = Type[StateSchema]


def get_state_value(state: StateSchema, key: str, default: Any = None) -> Any:
    return (
        state.get(key, default)
        if isinstance(state, dict)
        else getattr(state, key, default)
    )