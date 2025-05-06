#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   api_response_templates.py
@Time    :   2025/05/06 14:53:44
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''
from langchain_core.documents.base import BaseMedia


class ApiInfo(BaseMedia):
    error_message: str
    api_data: dict
    extend_data: dict
