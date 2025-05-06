#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   configuration_templates.py
@Time    :   2025/05/06 14:31:11
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''

from __future__ import annotations
from dataclasses import asdict, dataclass, field, fields
from typing import Annotated, Any, Literal, Optional, Type, TypeVar
from langchain_core.runnables import RunnableConfig, ensure_config

@dataclass(kw_only=True)
class BaseConfiguration:
    default_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="anthropic/claude-3-5-sonnet-20240620",
        metadata={
            "description": "The language model used for generating responses. Should be in the form: provider/model-name."
        },
    )
    @classmethod
    def from_runnable_config(
        cls: Type[T], config: Optional[RunnableConfig] = None
    ) -> T:
        """Create an IndexConfiguration instance from a RunnableConfig object.

        Args:
            cls (Type[T]): The class itself.
            config (Optional[RunnableConfig]): The configuration object to use.

        Returns:
            T: An instance of IndexConfiguration with the specified configuration.
        """
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})

T = TypeVar("T", bound=BaseConfiguration)


@dataclass(kw_only=True)
class BaseRagConfiguration(BaseConfiguration):
    """Configuration class for indexing and retrieval operations.

    This class defines the parameters needed for configuring the indexing and
    retrieval processes, including embedding model selection, retriever provider choice, and search parameters.
    """

    embedding_model: Annotated[
        str,
        {"__template_metadata__": {"kind": "embeddings"}},
    ] = field(
        default="openai/text-embedding-3-small",
        metadata={
            "description": "Name of the embedding model to use. Must be a valid embedding model name."
        },
    )

    retriever_provider: Annotated[
        Literal["elastic-local", "elastic", "pinecone", "mongodb", "api"],
        {"__template_metadata__": {"kind": "retriever"}},
    ] = field(
        default="api",
        metadata={
            "description": "The vector store provider to use for retrieval. Options are 'elastic', 'pinecone', or 'mongodb'."
        },
    )

    search_kwargs: dict[str, Any] = field(
        default_factory=lambda:{
            "kb_url":"https://XXX/knowledge/retrieval",
            "kb_args":{
                "header": {
                    "xUserId": 1
                },
                "model": {
                    "knowledge_ids":None,
                    "query": "{{#1742988726755.text#}}",
                    "text_type": None,
                    "biz_type": 18,
                    "first_level": None,
                    "second_level": None,
                    "three_level": None,
                    "doc_type": None,
                    "status": None,
                    "retrieval_setting": {
                        "top_k": 4,
                        "score_threshold": 0.7
                    },
                },
            },

        },
        metadata={
            "description": "Additional keyword arguments to pass to the search function of the retriever."
        },
    )



@dataclass(kw_only=True)
class BaseLlmModelConifuration:
    """The configuration for Llm model"""
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="openai/deepseek-v3",
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider/model-name."
        },
    )
    base_url: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="",
        metadata={
            "description": "API for language models used to process and optimize queries."
        }
    )
    api_key: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="",
        metadata={
            "description": "API_KEY for language models used to process and optimize queries."
        }
    )
    temperature: Annotated[int, {"__template_metadata__": {"kind": "llm"}}] = field(
        default=0,
        metadata={
            "description": "temperature for language models used to process and optimize queries."
        }
    )
    max_tokens: Annotated[int, {"__template_metadata__": {"kind": "llm"}}] = field(
        default=1024,
        metadata={
            "description": "max_tokens for language models used to process and optimize queries."
        }
    )
    def __post_init__(self):
        # 将 dataclass 字段转换成一个 dict
        self._data = asdict(self)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()
