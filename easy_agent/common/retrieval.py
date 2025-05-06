#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   retrieval.py
@Time    :   2025/05/06 17:58:46
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''
import os
from contextlib import contextmanager
from typing import Generator
from easy_agent.templates.configuration_templates import BaseRagConfiguration
from easy_agent.common.kb_api_retriever import ApiRetrieveDocument
from langchain_core.runnables import RunnableConfig
from langchain_core.vectorstores import VectorStoreRetriever

from langchain_core.embeddings import Embeddings


def build_text_encoder(model: str) -> Embeddings:
    """build text encoder

    Args:
        model (str): embedding model

    Returns:
        Embeddings: mdoel encoder
    """

    provider, model = model.split("/", maxsplit=1)
    match provider:
        case "openai":
            from langchain_openai.embeddings import OpenAIEmbeddings
            return OpenAIEmbeddings(model=model)
            
        case "cohere":
            from langchain_cohere.embeddings import CohereEmbeddings
            return CohereEmbeddings(model=model)
        case _:
            raise ValueError(f"Unsupported embedding provider: {provider}")




@contextmanager
def make_elastic_retriever(
    configuration: BaseRagConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific elastic index."""
    from langchain_elasticsearch import ElasticsearchStore

    connection_options = {}
    if configuration.retriever_provider == "elastic-local":
        connection_options = {
            "es_user": os.environ["ELASTICSEARCH_USER"],
            "es_password": os.environ["ELASTICSEARCH_PASSWORD"],
        }

    else:
        connection_options = {"es_api_key": os.environ["ELASTICSEARCH_API_KEY"]}

    vstore = ElasticsearchStore(
        **connection_options,  # type: ignore
        es_url=os.environ["ELASTICSEARCH_URL"],
        index_name="langchain_index",
        embedding=embedding_model,
    )

    yield vstore.as_retriever(search_kwargs=configuration.search_kwargs)


@contextmanager
def make_pinecone_retriever(
    configuration: BaseRagConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific pinecone index."""
    from langchain_pinecone import PineconeVectorStore

    vstore = PineconeVectorStore.from_existing_index(
        os.environ["PINECONE_INDEX_NAME"], embedding=embedding_model
    )
    yield vstore.as_retriever(search_kwargs=configuration.search_kwargs)


@contextmanager
def make_mongodb_retriever(
    configuration: BaseRagConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific MongoDB Atlas index & namespaces."""
    from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

    vstore = MongoDBAtlasVectorSearch.from_connection_string(
        os.environ["MONGODB_URI"],
        namespace="langgraph_retrieval_agent.default",
        embedding=embedding_model,
    )
    yield vstore.as_retriever(search_kwargs=configuration.search_kwargs)

@contextmanager
def make_api_retriever(
    configuration_cls: BaseRagConfiguration
):
    """retriever api

    Args:
        configuration (BaseRagConfiguration): _description_

    Raises:
        ValueError: _description_

    Yields:
        _type_: _description_
    """
    yield ApiRetrieveDocument(configuration_cls=configuration_cls)

@contextmanager
def make_retriever(
    config: RunnableConfig,
) -> Generator[VectorStoreRetriever, None, None]:
    """Create a retriever for the agent, based on the current configuration."""
    configuration = BaseRagConfiguration.from_runnable_config(config)
    embedding_model = build_text_encoder(configuration.embedding_model)
    match configuration.retriever_provider:
        case "elastic" | "elastic-local":
            with make_elastic_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case "pinecone":
            with make_pinecone_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case "mongodb":
            with make_mongodb_retriever(configuration, embedding_model) as retriever:
                yield retriever
        case "api":
            with make_api_retriever(BaseRagConfiguration) as retriever:
                yield retriever

        case _:
            raise ValueError(
                "Unrecognized retriever_provider in configuration. "
                f"Expected one of: {', '.join(BaseRagConfiguration.__annotations__['retriever_provider'].__args__)}\n"
                f"Got: {configuration.retriever_provider}"
            )
