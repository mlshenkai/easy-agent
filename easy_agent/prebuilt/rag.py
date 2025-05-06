#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   rag.py
@Time    :   2025/05/06 15:28:01
@Author  :   shenkai
@Email   :   mlshenkai@163.com
@Desc    :   None
"""
import os
from typing_extensions import Annotated
from easy_agent.templates.configuration_templates import (
    BaseRagconfig_schema,
    BaseLlmModelConifuration,
)
from easy_agent.templates import prompt_template as rag_prompts
from easy_agent.utils.decorators import convert_modifier_to_prompt
from easy_agent.templates.state_templates import AgentState
from easy_agent.utils.utils import load_chat_model
from easy_agent.utils.decorators import log_io
from easy_agent.common import retrieval
from easy_agent.utils.utils import format_docs
from dataclasses import dataclass, field
from typing import Optional, Union, Type, Any, Literal, TypeVar, cast
from langgraph.store.base import BaseStore
from langgraph.graph import StateGraph, END
from langgraph.types import Checkpointer, Send
from langgraph.utils.runnable import RunnableCallable, RunnableLike
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from langchain_core.documents import Document

from typing_extensions import Annotated, TypedDict
import operator


StructuredResponse = Union[dict, BaseModel]
StructuredResponseSchema = Union[dict, type[BaseModel]]


class RagAgentState(AgentState):
    query: str
    transformer_query: str
    documents: list[Document]
    reranked_documents: Annotated[list[Document], operator.add]
    response: str


RagStateSchema = TypeVar("RagStateSchema", bound=RagAgentState)
RagStateSchemaType = Type[RagStateSchema]


@dataclass(kw_only=True)
class RagAgentconfig_schema(BaseRagconfig_schema):
    retrieval_decision_model: Annotated[
        BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}
    ] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:" + os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={"description": "retrieval decision model"},
    )

    query_transformer_model: Annotated[
        BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}
    ] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:" + os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={"description": "query_transformer_model"},
    )

    query_model: Annotated[
        BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}
    ] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:" + os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider:model-name."
        },
    )
    rerank_model: Annotated[
        BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}
    ] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:" + os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={"description": "rerank model"},
    )

    responose_model: Annotated[
        BaseLlmModelConifuration, {"__template_metadata__": {"kind": "llm"}}
    ] = field(
        default_factory=lambda: BaseLlmModelConifuration(
            model="openai:" + os.getenv("OPENAI_API_VERSION"),
            base_url=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
        ),
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider:model-name."
        },
    )

    # prompt

    ## Search rewriting
    retrieval_decision_system_prompt: str = field(
        default=rag_prompts.RETRIEVAL_DECISION_SYSTEM_PROMPT,
        metadata={"description": "Search rewriting System prompt"},
    )

    retrieval_decision_user_prompt: str = field(
        default=rag_prompts.RETRIEVAL_DECISION_USER_PROMPT,
        metadata={"description": "Search rewriting user prompt"},
    )

    ## universal response generation
    universal_response_generation_system_prompt: str = field(
        default=rag_prompts.UNIVERSAL_RESPONSE_GENERATION_SYSTEM_PROMPT,
        metadata={"description": "universal response generation system prompt"},
    )

    universal_response_generation_user_prompt: str = field(
        default=rag_prompts.UNIVERSAL_RESPONSE_GENERATION_USER_PROMPT,
        metadata={"description": "universal response generation user prompt"},
    )

    ## query transformer
    query_transformer_system_prompt: str = field(
        default=rag_prompts.QUERY_TRANSFORMER_SYSTEM_PROMPT,
        metadata={"description": "query transformers system prompt"},
    )
    query_transformer_user_prompt: str = field(
        default=rag_prompts.QUERY_TRANSFORMER_USER_PROMPT,
        metadata={"description": "query transformers user prompt"},
    )

    ## retrieval prompt
    query_api_system_prompt: str = field(
        default=rag_prompts.QUERY_API_SYSTEM_PROMPT,
        metadata={"description": "reAct agent prompt"},
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
        metadata={"description": "The system prompt used for rerank document"},
    )

    rerank_user_prompt: str = field(
        default=rag_prompts.RERANK_USER_PROMPT,
        metadata={"description": "The user prompt used for rerank document"},
    )

    response_system_prompt: str = field(
        default=rag_prompts.RESPONSE_RAG_SYSTEM_PROMPT,
        metadata={"description": "The system prompt for final response"},
    )


from langgraph.prebuilt import create_react_agent


@convert_modifier_to_prompt
def create_rag_agent(
    *,
    response_format: Optional[
        Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]
    ],
    pre_model_hook: Optional[RunnableLike] = None,
    state_schema: Optional[RagStateSchemaType] = None,
    config_schema: Optional[Type[RagAgentconfig_schema]] = RagAgentconfig_schema,
    checkpointer: Optional[Checkpointer] = None,
    store: Optional[BaseStore] = None,
    interrupt_before: Optional[list[str]] = None,
    interrupt_after: Optional[list[str]] = None,
    debug: bool = False,
    version: Literal["v1", "v2"] = "v1",
    name: Optional[str] = None,
    skip_final_reponse: bool = False,
):

    ## TODO (mlshenkai) 添加create_rag_agent
    async def query_transformers(
        state: RagStateSchema, *, config: RunnableConfig
    ) -> dict:
        configuration = config_schema.from_runnable_config(config=config)
        model = load_chat_model(configuration.query_transformer_model)
        messages = [
            {
                ("system", configuration.query_transformer_system_prompt),
                (
                    "user",
                    configuration.query_transformer_user_prompt.format(
                        query=state["query"]
                    ),
                ),
            }
        ]

        result = cast(AIMessage, await model.ainvoke(messages))

        return {"transformer_query": result.content}

    async def retrieve_documents(
        state: RagStateSchema, *, config: RunnableConfig
    ) -> dict:
        with retrieval.make_retriever(config=config) as retriever:
            response = await retriever.ainvoke(state["query"], config=config)
            return {"documents": response}

    class RerankState(TypedDict):
        query: str
        document: Document

    async def document_rerank(state: RerankState, *, config: RunnableConfig) -> dict:
        configuration = config_schema.from_runnable_config(config=config)

        class RelevanceScore(BaseModel):
            """document 相关性分数"""

            relevance_score: int = Field(default=0, description="相关性分数(0-10)")

        llm = load_chat_model(configuration.rerank_model)
        model = llm.with_structured_output(RelevanceScore, method="function_calling")
        query = state["query"]
        document = state["document"]
        messages = [
            {"role": "system", "content": configuration.rerank_system_prompt},
            {
                "role": "user",
                "content": configuration.rerank_user_prompt.format(
                    query=query, document=document.page_content
                ),
            },
        ]

        relevance_score: RelevanceScore = await model.ainvoke(messages)
        document.metadata["relevance_score"] = relevance_score.relevance_score
        return {
            "reranked_documents": [document],
        }

    def continue_document_rank(state: RagStateSchema, *, config: RunnableConfig):
        return [
            Send("document_rerank", {"query": state["query"], "document": document})
            for document in state["documents"]
        ]

    async def respond(state: RagStateSchema, *, config: RunnableConfig):
        configuration = config_schema.from_runnable_config(config)
        documents_context = format_docs(state["documents"])
        system_prompt = configuration.response_system_prompt.format(
            documents=documents_context
        )
        llm = load_chat_model(configuration.responose_model)
        if response_format:
            structured_response_schema = response_format
            if isinstance(response_format, tuple):
                system_prompt, structured_response_schema = response_format
                system_prompt = system_prompt.format(documents=documents_context)
            llm = llm.with_structured_output(cast(StructuredResponseSchema, structured_response_schema))
            
        messages = [
                SystemMessage(content=system_prompt)
            ] + list(state["messages"]) + [HumanMessage(content=state["transformer_query"])]

        result = await llm.ainvoke(messages)
        return {
            "response": result,
        }
    
    

    graph_builder = StateGraph(RagStateSchema, config_schema=config_schema)
    
    graph_builder.add_node(query_transformers)
    graph_builder.add_node(retrieve_documents)
    graph_builder.add_node(document_rerank)
    if not skip_final_reponse:
        graph_builder.add_node(respond)
    if pre_model_hook is not None:
        graph_builder.add_node("pre_model_hook", pre_model_hook)
        graph_builder.add_edge("pre_model_hook", "query_transformers")
        entrypoint = "pre_model_hook"
    else:
        entrypoint = "query_transformers"
    
    graph_builder.set_entry_point(entrypoint)
    graph_builder.add_edge("query_transformers", "retrieve_documents")
    graph_builder.add_edge("retrieve_documents", continue_document_rank, ["document_rerank"])
    if not skip_final_reponse:
        graph_builder.add_edge("document_rerank", "respond")
        graph_builder.add_edge("respond", END)
    else:
        graph_builder.add_edge("document_rerank", END)
    
    return graph_builder.compile(
        checkpointer=checkpointer,
        store=store,
        interrupt_before=interrupt_before,
        interrupt_after=interrupt_after,
        debug=debug,
        name=name
    )






    

