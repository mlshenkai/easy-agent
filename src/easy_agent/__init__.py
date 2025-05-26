"""
Easy Agent - 多智能体框架

一个基于LangGraph的轻量级多智能体框架，支持配置化的智能体和工作流定义。

主要特性:
- 配置化的智能体和工作流
- 预定义的节点和智能体类型
- 灵活的工具系统
- RESTful API接口
- 命令行工具
- 状态管理和持久化

基本使用:
```python
from easy_agent import workflow_manager

# 获取工作流引擎
engine = workflow_manager.get_workflow("simple_chat")

# 执行工作流
state = await engine.execute("你好，我需要帮助")
```

命令行使用:
```bash
# 启动API服务器
easy-agent serve

# 交互式聊天
easy-agent chat

# 查看可用工作流
easy-agent list-workflows
```
"""
