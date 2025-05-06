#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   utils.py
@Time    :   2025/05/06 14:38:25
@Author  :   shenkai 
@Email   :   mlshenkai@163.com 
@Desc    :   None
'''
import yaml
import json

from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, ToolCall, ToolMessage
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from easy_agent.templates.api_response_templates import ApiInfo
from easy_agent.templates.configuration_templates import BaseLlmModelConifuration

def load_chat_model(fully_specified_model_configuration: BaseLlmModelConifuration) -> BaseChatModel:
    return init_chat_model(
        **fully_specified_model_configuration
    )




def dict_to_yaml(data, file_path=None, sort_keys=False):
    """
    将字典转换为YAML格式的字符串或文件
    
    参数:
        data: 要转换的字典
        file_path: 可选，输出YAML的文件路径
        sort_keys: 是否按键排序
    
    返回:
        如果未指定file_path，返回YAML字符串；否则返回None
    """
    yaml_str = yaml.dump(
        data, 
        default_flow_style=False,  # 使用块格式而非行内格式
        allow_unicode=True,        # 允许Unicode字符
        sort_keys=sort_keys,       # 是否排序键
        indent=4                   # 缩进空格数
    )
    
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_str)
        return None
    else:
        return yaml_str


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = ""
        model = fully_specified_name
    return init_chat_model(model, model_provider=provider)



def _format_doc(doc: Document) -> str:
    """Format a single document as XML.

    Args:
        doc (Document): The document to format.

    Returns:
        str: The formatted document as an XML string.
    """
    metadata = doc.metadata or {}
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items())
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{doc.page_content}\n</document>"


def format_docs(docs: Optional[list[Document]]) -> str:
    """Format a list of documents as XML.

    This function takes a list of Document objects and formats them into a single XML string.

    Args:
        docs (Optional[list[Document]]): A list of Document objects to format, or None.

    Returns:
        str: A string containing the formatted documents in XML format.

    Examples:
        >>> docs = [Document(page_content="Hello"), Document(page_content="World")]
        >>> print(format_docs(docs))
        <documents>
        <document>
        Hello
        </document>
        <document>
        World
        </document>
        </documents>

        >>> print(format_docs(None))
        <documents></documents>
    """
    if not docs:
        return "<documents></documents>"
    formatted = "\n".join(_format_doc(doc) for doc in docs)
    return f"""<documents>
{formatted}
</documents>"""

def serialize_to_json(obj, ensure_ascii=False, indent=None, default=None):
    """
    将 Python 对象序列化为 JSON 字符串
    
    Args:
        obj: 要序列化的 Python 对象
        ensure_ascii: 是否确保 ASCII 编码（默认 False）
        indent: 缩进格式（默认 None）
        default: 自定义序列化函数（默认 None）
        
    Returns:
        str: JSON 字符串
    """
    try:
        return json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent, default=default)
    except (TypeError, OverflowError) as e:
        print(f"序列化错误: {str(e)}")
        return "{}"


def deserialize_from_json(json_str, default_value=None):
    """
    将 JSON 字符串反序列化为 Python 对象，支持多层 JSON 解析
    
    Args:
        json_str: JSON 字符串或已经是 Python 对象
        default_value: 解析失败时返回的默认值
        
    Returns:
        dict/list/等: 解析后的 Python 对象
    """
    if default_value is None:
        default_value = {}
    
    # 如果输入已经是非字符串类型，直接返回
    if not isinstance(json_str, str):
        return json_str
    
    # 处理空字符串或无效 JSON
    if not json_str or json_str.isspace():
        return default_value
    
    try:
        # 处理多层 JSON 编码
        content = json_str
        # 循环解析，直到不能再解析为止
        while isinstance(content, str):
            try:
                parsed = json.loads(content)
                # 防止无限循环（如果解析结果仍是相同的字符串）
                if isinstance(parsed, str) and parsed == content:
                    break
                content = parsed
            except json.JSONDecodeError:
                # 如果无法继续解析，则停止
                break
        
        return content
    except Exception as e:
        print(f"JSON 解析错误: {str(e)}")
        return default_value



def build_api_info(agent_results: list[BaseMessage]) -> list[ApiInfo]:
    api_infos = []
    for agent_result in agent_results:
        if isinstance(agent_result, ToolMessage):
            content = deserialize_from_json(agent_result.content)
            code = content["code"]
            if code["value"] == 200:
                error_message = ""
            else:
                error_message = code["description"]
            data = content["data"]
            extend_data = content.get("extendData", {})
            api_infos.append(
                ApiInfo(
                    metadata=extend_data,
                    api_data=data,
                    extend_data=extend_data,
                    error_message=error_message
                )
            )
    return api_infos

def _format_api(api: ApiInfo) -> str:
    """Format a single api as XML.

    Args:
        doc (ApiInfo): The api to format.

    Returns:
        str: The formatted api as an XML string.
    """
    metadata = api.metadata or {}
    meta = "".join(f" {k}={v!r}" for k, v in metadata.items() if k != "detailUrl")
    if meta:
        meta = f" {meta}"

    return f"<document{meta}>\n{dict_to_yaml(api.api_data)}\n</document>"

def format_apis(apis: Optional[list[ApiInfo]]) -> str:
    """Format a list of api as XML.

    This function takes a list of ApiInfo objects and formats them into a single XML string.

    Args:
        apis (Optional[list[ApiInfo]]): A list of ApiInfo objects to format, or None.

    Returns:
        str: A string containing the formatted apis in XML format.
    """
    if not apis:
        return "<apis></apis>"
    formatted = "\n".join(_format_api(api) for api in apis)
    return f"""<apis>
{formatted}
</apis>"""
    