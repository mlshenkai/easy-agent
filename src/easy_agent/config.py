"""
配置管理模块
"""
from __future__ import annotations
import os
from typing import Dict, Any, Optional, List, Type, TypeVar
from dataclasses import asdict, dataclass, field, fields
from typing_extensions import Annotated
from langchain_core.runnables import RunnableConfig, ensure_config


@dataclass(kw_only=True)
class ModelConfig:
    """模型配置"""
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
    timeout: int = 30
    provider: str  # openai, anthropic, ollama, etc.
    def __post_init__(self):
        # 将 dataclass 字段转换成一个 dict
        if self.api_key is None:
            # 从环境变量获取API密钥
            env_key = f"{self.provider.upper()}_API_KEY"
            self.api_key = os.getenv(env_key)
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



@dataclass(kw_only=True)
class BaseAgentConfig:
    default_llm: Annotated[ModelConfig, {"__template_metadata__": {"kind": "llm"}}] = field(
        
    )

    @classmethod
    def from_runnable_config(
        cls: Type[BaseAgentConfig], config: Optional[RunnableConfig] = None
    ) -> BaseAgentConfig:
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

