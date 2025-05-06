#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   rag.py
@Time    :   2025/05/06 15:28:01
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''
import os
from typing_extensions import Annotated
from easy_agent.templates.configuration_templates import BaseRagConfiguration, BaseLlmModelConifuration
from easy_agent.templates import prompt_template as rag_prompts
from easy_agent.utils.decorators import convert_modifier_to_prompt
from easy_agent.templates.state_templates import StateSchemaType, AgentState, AgentStatePydantic
from easy_agent.utils.decorators import log_io
from dataclasses import dataclass, field
from typing import Optional, Union, Type, Any, Literal
from langgraph.store.base import BaseStore
from langgraph.types import Checkpointer, Send
from langgraph.utils.runnable import RunnableCallable, RunnableLike

from pydantic import BaseModel

StructuredResponse = Union[dict, BaseModel]
StructuredResponseSchema = Union[dict, type[BaseModel]]




@dataclass(kw_only=True)
class RagAgentConfiguration(BaseRagConfiguration):
    retrieval_decision_model: Annotated[BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:"+os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={
            "description": "retrieval decision model"
        }
    )

    query_transformer_model: Annotated[BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:"+os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={
            "description": "query_transformer_model"
        }
    )

    query_model: Annotated[BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:"+os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider:model-name."
        }
    )
    rerank_model: Annotated[BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:"+os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={
            "description": "rerank model"
        }
    )

    responose_model: Annotated[BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:"+os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider:model-name."
        }
    )


# prompt

    ## Search rewriting
    retrieval_decision_system_prompt: str = field(
        default=rag_prompts.RETRIEVAL_DECISION_SYSTEM_PROMPT,
        metadata={
            "description": "Search rewriting System prompt"
        }
    )

    retrieval_decision_user_prompt: str = field(
        default=rag_prompts.RETRIEVAL_DECISION_USER_PROMPT,
        metadata={
            "description": "Search rewriting user prompt"
        }
    )

    ## universal response generation
    universal_response_generation_system_prompt: str = field(
        default=rag_prompts.UNIVERSAL_RESPONSE_GENERATION_SYSTEM_PROMPT,
        metadata={
            "description": "universal response generation system prompt"
        }
    )

    universal_response_generation_user_prompt: str = field(
        default=rag_prompts.UNIVERSAL_RESPONSE_GENERATION_USER_PROMPT,
        metadata={
            "description": "universal response generation user prompt"
        }
    )


    ## query transformer
    query_transformer_system_prompt: str = field(
        default=rag_prompts.QUERY_TRANSFORMER_SYSTEM_PROMPT,
        metadata={
            "description": "query transformers system prompt"
        }
    )
    query_transformer_user_prompt: str = field(
        default=rag_prompts.QUERY_TRANSFORMER_USER_PROMPT,
        metadata={
            "description": "query transformers user prompt"
        }
    )

    ## retrieval prompt
    query_api_system_prompt: str = field(
        default=rag_prompts.QUERY_API_SYSTEM_PROMPT,
        metadata={
            "description": "reAct agent prompt"
        }
    )

    # general system prompt
    general_system_prompt: str = field(
        default=rag_prompts.GENERAL_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for responding to general questions."
        },
    )

    # rerank prompt
    rerank_system_prompt: str = field(
        default=rag_prompts.RERANK_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for rerank document"
        }
    )

    rerank_user_prompt: str = field(
        default=rag_prompts.RERANK_USER_PROMPT,
        metadata={
            "description": "The user prompt used for rerank document"
        }
    )

    response_system_prompt: str = field(
        default=rag_prompts.RESPONSE_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt for final response"

        }
    )

from langgraph.prebuilt import create_react_agent

@convert_modifier_to_prompt
def create_rag_agent(
    Configuration: Type[BaseRagConfiguration],
    *,
    response_format: Optional[
        Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]
    ],
    pre_model_hook: Optional[RunnableLike] = None,
    state_schema: Optional[StateSchemaType] = None,
    config_schema: Optional[Type[Any]] = None,
    checkpointer: Optional[Checkpointer] = None,
    store: Optional[BaseStore] = None,
    interrupt_before: Optional[list[str]] = None,
    interrupt_after: Optional[list[str]] = None,
    debug: bool = False,
    version: Literal["v1", "v2"] = "v1",
    name: Optional[str] = None,

):
    ## TODO (mlshenkai) 添加create_rag_agent
    pass

