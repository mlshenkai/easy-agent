#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   state_templates.py
@Time    :   2025/05/06 15:53:50
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''

from typing_extensions import Annotated, TypedDict
from pydantic import BaseModel
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from typing import Union, Sequence, TypeVar, Type
from langgraph.managed import IsLastStep, RemainingSteps


StructuredResponse = Union[dict, BaseModel]
StructuredResponseSchema = Union[dict, type[BaseModel]]


class AgentState(TypedDict):
    """The State if the agent..."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


class AgentStateWithAStep(TypedDict):
    """The State if the agent..."""

    messages: Annotated[Sequence[BaseMessage], add_messages]

    is_last_step: IsLastStep

    remaining_steps: RemainingSteps


class AgentStatePydantic(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class AgentStatePydanticWithAStep(TypedDict):
    """The State if the agent..."""

    messages: Annotated[Sequence[BaseMessage], add_messages]

    remaining_steps: RemainingSteps = 25


class AgentStateWithStructuredResponse(AgentState):
    """The state of the agent with a structured response."""

    structured_response: StructuredResponse


class AgentStateWithStructuredResponsePydantic(AgentStatePydantic):
    """The state of the agent with a structured response."""

    structured_response: StructuredResponse


class AgentStateWithStepWithStructuredResponse(AgentStateWithAStep):
    """The state of the agent with a structured response."""

    structured_response: StructuredResponse


class AgentStateWithStepWithStructuredResponsePydantic(AgentStatePydanticWithAStep):
    """The state of the agent with a structured response."""

    structured_response: StructuredResponse


StateSchema = TypeVar("StateSchema", bound=Union[AgentState, AgentStatePydantic])
StateSchemaType = Type[StateSchema]

StateWithStepSchema = TypeVar("StateWithStepSchema", bound=Union[AgentStateWithAStep, AgentStatePydanticWithAStep])
StateWithTypeSchemaType = Type[StateWithStepSchema]
