#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   inject_utils.py
@Time    :   2025/05/06 14:50:49
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''



import functools
import inspect
from typing import List, Callable, Any
from langchain_core.tools import BaseTool, StructuredTool
import operator

def inject_params_if_exists(tools: List[BaseTool], inject_kwargs: dict) -> List[BaseTool]:
    """
    为工具列表选择性注入参数（只在函数有对应参数时注入）
    
    Args:
        tools: 工具列表
        inject_kwargs: 要注入的参数字典
    
    Returns:
        注入参数后的工具列表
    """
    for tool in tools:
        if isinstance(tool, StructuredTool):
            # 处理同步函数
            if tool.func:
                tool.func = _inject_params_to_function(tool.func, inject_kwargs)
            
            # 处理异步函数
            if tool.coroutine:
                tool.coroutine = _inject_params_to_function(tool.coroutine, inject_kwargs)
    
    return tools

def _inject_params_to_function(func: Callable, inject_kwargs: dict) -> Callable:
    """
    只在函数有对应参数时注入参数
    
    Args:
        func: 原始函数
        inject_kwargs: 要注入的参数字典
    
    Returns:
        注入参数后的函数
    """
    # 获取函数签名
    sig = inspect.signature(func)
    param_names = set(sig.parameters.keys())
    
    # 只保留函数参数中存在的注入参数
    filtered_kwargs = {k: v for k, v in inject_kwargs.items() if k in param_names and v}
    
    # 如果有需要注入的参数，则创建偏函数
    if filtered_kwargs:
        return functools.partial(func, **filtered_kwargs)
    
    # 如果没有需要注入的参数，返回原函数
    return func