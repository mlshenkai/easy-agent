"""
API使用示例
"""
import asyncio
import aiohttp
import json


class EasyAgentClient:
    """Easy Agent API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def chat(self, message: str, workflow: str = "simple_chat", session_id: str = None):
        """发送聊天消息"""
        async with aiohttp.ClientSession() as session:
            data = {
                "message": message,
                "workflow": workflow
            }
            if session_id:
                data["session_id"] = session_id
            
            async with session.post(f"{self.base_url}/chat", json=data) as response:
                return await response.json()
    
    async def resume_chat(self, session_id: str, message: str = None):
        """恢复聊天"""
        async with aiohttp.ClientSession() as session:
            data = {"session_id": session_id}
            if message:
                data["message"] = message
            
            async with session.post(f"{self.base_url}/resume", json=data) as response:
                return await response.json()
    
    async def list_workflows(self):
        """列出工作流"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/workflows") as response:
                return await response.json()
    
    async def list_sessions(self):
        """列出会话"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/sessions") as response:
                return await response.json()
    
    async def get_session(self, session_id: str):
        """获取会话详情"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/sessions/{session_id}") as response:
                return await response.json()
    
    async def delete_session(self, session_id: str):
        """删除会话"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self.base_url}/sessions/{session_id}") as response:
                return await response.json()
    
    async def get_config(self):
        """获取配置信息"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/config") as response:
                return await response.json()


async def simple_chat_example():
    """简单聊天示例"""
    print("=== 简单聊天示例 ===")
    
    client = EasyAgentClient()
    
    try:
        # 开始对话
        response = await client.chat("你好，你能帮我做什么？")
        print(f"AI: {response['response']}")
        print(f"智能体: {response['agent']}")
        print(f"会话ID: {response['session_id']}")
        
        session_id = response['session_id']
        
        # 继续对话
        response = await client.chat("告诉我关于人工智能的信息", session_id=session_id)
        print(f"AI: {response['response']}")
        
        return session_id
        
    except Exception as e:
        print(f"错误: {e}")
        return None


async def research_workflow_example():
    """研究工作流示例"""
    print("\n=== 研究工作流示例 ===")
    
    client = EasyAgentClient()
    
    try:
        # 开始研究任务
        response = await client.chat(
            "请帮我研究一下区块链技术的应用场景",
            workflow="research_writing"
        )
        
        print(f"研究开始...")
        print(f"当前智能体: {response['agent']}")
        print(f"响应: {response['response'][:200]}...")
        
        session_id = response['session_id']
        
        # 检查是否需要继续
        while not response['is_complete'] and not response['requires_input']:
            await asyncio.sleep(1)  # 等待一秒
            
            # 获取会话状态
            session_info = await client.get_session(session_id)
            state = session_info['state']
            
            if state['is_complete']:
                break
            
            # 如果需要输入，提供输入
            if state['context'].get('requires_human_input', False):
                response = await client.resume_chat(session_id, "继续")
                print(f"继续执行: {response['response'][:200]}...")
            
            # 如果没有完成，等待或恢复
            if not state['is_complete']:
                response = await client.resume_chat(session_id)
                if response['response']:
                    print(f"进展: {response['response'][:200]}...")
        
        print("研究工作流完成!")
        
    except Exception as e:
        print(f"错误: {e}")


async def session_management_example():
    """会话管理示例"""
    print("\n=== 会话管理示例 ===")
    
    client = EasyAgentClient()
    
    try:
        # 创建几个会话
        session1 = await client.chat("第一个会话")
        session2 = await client.chat("第二个会话")
        
        print(f"创建了两个会话:")
        print(f"  会话1: {session1['session_id']}")
        print(f"  会话2: {session2['session_id']}")
        
        # 列出所有会话
        sessions = await client.list_sessions()
        print(f"\n当前活跃会话数: {len(sessions)}")
        
        for session in sessions:
            print(f"  {session['session_id'][:8]}... - {session['workflow']} - {session['message_count']}条消息")
        
        # 获取会话详情
        session_detail = await client.get_session(session1['session_id'])
        print(f"\n会话1详情:")
        print(f"  工作流: {session_detail['workflow']}")
        print(f"  消息数: {len(session_detail['state']['messages'])}")
        
        # 删除一个会话
        await client.delete_session(session2['session_id'])
        print(f"\n已删除会话2")
        
        # 再次列出会话
        sessions = await client.list_sessions()
        print(f"剩余会话数: {len(sessions)}")
        
    except Exception as e:
        print(f"错误: {e}")


async def workflow_info_example():
    """工作流信息示例"""
    print("\n=== 工作流信息示例 ===")
    
    client = EasyAgentClient()
    
    try:
        # 获取系统配置
        config = await client.get_config()
        print(f"系统信息:")
        print(f"  应用名: {config['app_name']}")
        print(f"  版本: {config['version']}")
        print(f"  可用智能体: {', '.join(config['available_agents'])}")
        print(f"  可用工具: {', '.join(config['available_tools'])}")
        
        # 获取工作流列表
        workflows = await client.list_workflows()
        print(f"\n可用工作流 ({len(workflows)} 个):")
        
        for workflow in workflows:
            status = "✅" if workflow['enabled'] else "❌"
            print(f"  {status} {workflow['name']}: {workflow['description']}")
            print(f"     入口: {workflow['entry_point']}")
            print(f"     智能体: {', '.join(workflow['agents'])}")
        
    except Exception as e:
        print(f"错误: {e}")


async def interactive_chat_example():
    """交互式聊天示例"""
    print("\n=== 交互式聊天示例 ===")
    print("输入 'quit' 退出聊天")
    
    client = EasyAgentClient()
    session_id = None
    
    try:
        while True:
            user_input = input("\n您: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                break
            
            if not user_input:
                continue
            
            # 发送消息
            if session_id:
                response = await client.chat(user_input, session_id=session_id)
            else:
                response = await client.chat(user_input)
                session_id = response['session_id']
            
            print(f"{response['agent']}: {response['response']}")
            
            # 检查是否需要输入
            if response['requires_input']:
                print("(系统正在等待您的输入...)")
            
            # 检查是否完成
            if response['is_complete']:
                print("(对话已完成)")
                break
    
    except KeyboardInterrupt:
        print("\n对话已中断")
    except Exception as e:
        print(f"错误: {e}")


async def main():
    """主函数"""
    print("Easy Agent API 使用示例")
    print("=" * 50)
    print("请确保API服务器正在运行 (easy-agent serve)")
    print("=" * 50)
    
    try:
        # 各种示例
        session_id = await simple_chat_example()
        await research_workflow_example() 
        await session_management_example()
        await workflow_info_example()
        
        # 交互式聊天（可选）
        response = input("\n是否开始交互式聊天? (y/n): ").strip().lower()
        if response == 'y':
            await interactive_chat_example()
        
    except aiohttp.ClientError:
        print("无法连接到API服务器，请确保服务器正在运行：")
        print("  easy-agent serve")
    except Exception as e:
        print(f"示例执行失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
