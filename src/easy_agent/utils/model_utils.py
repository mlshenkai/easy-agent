#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   model_utils.py
@Time    :   2025/05/26 14:27:32
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''
from typing import cast
from easy_agent.config import ModelConfig
from langchain_core.language_models import BaseChatModel
from typing import (
    Sequence,
)

from langchain_core.language_models import (
    LanguageModelLike,
)
from langchain_core.runnables import (
    RunnableBinding,
    RunnableSequence
)
from langchain_core.tools import BaseTool



def get_model(model_config: ModelConfig):
    if model_config.provider == "openai_format":
        model_config.model="openai:"+ model_config.model
    
    try:
        from langchain.chat_models import (  # type: ignore[import-not-found]
            init_chat_model,
        )
    except ImportError:
        raise ImportError(
            "Please install langchain (`pip install langchain`) to use '<provider>:<model>' string syntax for `model` parameter."
        )

    model = cast(BaseChatModel, init_chat_model(**model_config))
    return model


def should_bind_tools(model: LanguageModelLike, tools: Sequence[BaseTool]) -> bool:
    if isinstance(model, RunnableSequence):
        model = next(
            (
                step
                for step in model.steps
                if isinstance(step, (RunnableBinding, BaseChatModel))
            ),
            model,
        )

    if not isinstance(model, RunnableBinding):
        return True

    if "tools" not in model.kwargs:
        return True

    bound_tools = model.kwargs["tools"]
    if len(tools) != len(bound_tools):
        raise ValueError(
            "Number of tools in the model.bind_tools() and tools passed to create_react_agent must match"
        )

    tool_names = set(tool.name for tool in tools)
    bound_tool_names = set()
    for bound_tool in bound_tools:
        # OpenAI-style tool
        if bound_tool.get("type") == "function":
            bound_tool_name = bound_tool["function"]["name"]
        # Anthropic-style tool
        elif bound_tool.get("name"):
            bound_tool_name = bound_tool["name"]
        else:
            # unknown tool type so we'll ignore it
            continue

        bound_tool_names.add(bound_tool_name)

    if missing_tools := tool_names - bound_tool_names:
        raise ValueError(f"Missing tools '{missing_tools}' in the model.bind_tools()")

    return False

