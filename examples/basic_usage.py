"""
基本使用示例
"""
import asyncio
from easy_agent import workflow_manager, get_config


async def basic_chat_example():
    """基本聊天示例"""
    print("=== 基本聊天示例 ===")
    
    # 获取简单聊天工作流
    workflow = workflow_manager.get_workflow("simple_chat")
    
    # 开始对话
    state = await workflow.execute("你好，你能帮我做什么？")
    
    # 打印对话历史
    for message in state["messages"]:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        agent = message.get("agent", "")
        
        if role == "user":
            print(f"用户: {content}")
        elif role == "assistant":
            print(f"{agent}: {content}")
    
    print(f"\n会话ID: {state['session_id']}")
    print(f"当前智能体: {state.get('current_agent')}")
    print(f"是否完成: {state['is_complete']}")


async def research_writing_example():
    """研究写作工作流示例"""
    print("\n=== 研究写作工作流示例 ===")
    
    # 获取研究写作工作流
    workflow = workflow_manager.get_workflow("research_writing")
    
    # 开始研究任务
    state = await workflow.execute("请帮我研究人工智能的发展历史，并写一篇总结文章")
    
    # 打印执行过程
    print(f"工作流执行了 {state['iteration_count']} 步")
    print(f"涉及的智能体: {set(msg.get('agent', '') for msg in state['messages'] if msg.get('agent'))}")
    
    # 打印最终结果
    for message in state["messages"]:
        if message.get("role") == "assistant":
            agent = message.get("agent", "")
            content = message.get("content", "")
            print(f"\n{agent}的输出:")
            print("-" * 50)
            print(content[:300] + "..." if len(content) > 300 else content)


async def custom_workflow_example():
    """自定义工作流示例"""
    print("\n=== 自定义工作流示例 ===")
    
    from easy_agent.config import WorkflowConfig
    from easy_agent import workflow_manager
    
    # 创建自定义工作流配置
    custom_workflow = WorkflowConfig(
        name="custom_assistant",
        description="自定义助手工作流",
        entry_point="assistant",
        agents=["assistant", "researcher"],
        edges=[
            {
                "from": "assistant",
                "to": "researcher", 
                "condition": "message.研究"
            },
            {
                "from": "researcher",
                "to": "assistant",
                "condition": "context.research_complete"
            }
        ]
    )
    
    # 创建工作流引擎
    workflow = workflow_manager.create_workflow(custom_workflow)
    
    # 执行工作流
    state = await workflow.execute("请帮我研究一下量子计算的基本原理")
    
    print(f"自定义工作流执行完成")
    print(f"执行步数: {state['iteration_count']}")
    print(f"最终智能体: {state.get('current_agent')}")


async def tool_usage_example():
    """工具使用示例"""
    print("\n=== 工具使用示例 ===")
    
    from easy_agent.tools import get_tool
    
    # 使用计算器工具
    calculator = get_tool("calculator")
    result = await calculator.execute("2 + 3 * 4")
    print(f"计算结果: {result}")
    
    # 使用文本生成工具
    text_gen = get_tool("text_generation")
    generated = await text_gen.execute("写一首关于春天的短诗", style="creative")
    print(f"生成的文本: {generated}")
    
    # 使用网络搜索工具
    search = get_tool("web_search")
    results = await search.execute("人工智能最新发展")
    print(f"搜索到 {len(results)} 个结果")
    for i, result in enumerate(results[:2], 1):
        print(f"  {i}. {result['title']}")


def config_example():
    """配置示例"""
    print("\n=== 配置示例 ===")
    
    config = get_config()
    
    print(f"应用名称: {config.app_name}")
    print(f"版本: {config.version}")
    print(f"可用模型: {list(config.models.keys())}")
    print(f"可用智能体: {list(config.agents.keys())}")
    print(f"可用工作流: {list(config.workflows.keys())}")


async def main():
    """主函数"""
    print("Easy Agent 示例程序")
    print("=" * 50)
    
    # 配置示例
    config_example()
    
    # 基本功能示例
    await basic_chat_example()
    await research_writing_example()
    await custom_workflow_example()
    await tool_usage_example()
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
