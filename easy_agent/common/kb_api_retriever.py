#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   kb_api_retriever.py
@Time    :   2025/05/06 19:47:15
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''

"""api request"""
import aiohttp
from easy_agent.templates.configuration_templates import BaseRagConfiguration
from typing import Type
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.documents import Document


class ApiRetrieveDocument(Runnable):
    def __init__(self,  configuration_cls: Type[BaseRagConfiguration]):
        super().__init__()
        self.configuration_cls = configuration_cls
        
    
    async def ainvoke(self, query: str, config: RunnableConfig) -> list[Document]:
        configuration = self.configuration_cls.from_runnable_config(config=config)
        request_configuration = configuration.search_kwargs
        request_url = request_configuration.get("kb_url")
        request_args = request_configuration.get("kb_args")
        request_args["model"]["query"] = query
        async with aiohttp.ClientSession() as session:
            async with session.post(request_url, json=request_args) as response:
                response_json = await response.json()
                response_data = response_json.get("data", {})
                response_records = response_data.get("records")
                documents = []
                for response_record in response_records:
                    title = response_record.get("title", "")
                    content = response_record.get("content")
                    url = response_record.get("url")
                    score = response_record.get("score")
                    uuid = response_record.get("id")
                    documents.append(
                        Document(
                            page_content=content,
                            metadata={
                                "title": title,
                                "url": url,
                                "score": score,
                                "uuid": uuid,
                            }
                        )
                    )
                return documents
