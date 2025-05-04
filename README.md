# Easy Agent

基于 [LangGraph](https://github.com/langchain-ai/langgraph) 构建的多智能体（Multi-Agent）框架，让你可以轻松创建、组合并运行多个智能体，快速构建复杂的智能体系统。

## ✨ 项目特色

- 🧠 **多智能体支持**：原生集成 LangGraph，支持 Agent 间消息传递、状态共享、流程控制。
- ⚙️ **模块化设计**：定义 Agent 即可使用，无需编写大量控制逻辑。
- 🔄 **流程图驱动**：基于图结构灵活控制 Agent 执行顺序与条件跳转。
- 🚀 **快速上手**：只需少量代码即可搭建自己的 Multi-Agent 系统。

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/mlshenkai/easy-agent.git
cd easy-agent

### 2. 安装依赖
pip install -r requirements.txt
或者
uv sync

### 3. 运行示例
python examples/demo.py

📁 项目结构
你可以使用 Easy Agent 来实现：
	•	自动问答对话系统（多个角色协作）
	•	多步推理与规划任务
	•	多模型协作的任务执行（如查询、摘要、写作）
	•	自定义流程的智能助手

📚 依赖组件
	•	LangGraph
	•	LangChain
	•	Python 3.11+

🧩 开发计划
	•	支持 Web 界面流程设计器
	•	状态持久化与中断恢复
	•	Agent Market 模块，复用预设智能体

📄 License
MIT License

欢迎 Issue 和 PR，一起打造强大的多智能体开发工具！