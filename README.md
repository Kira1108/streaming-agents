# 流式智能体系统 (Streaming Agents)

> 构建可观测的流式输出智能体系统

## 概述

这个项目实现了一个基于 LlamaIndex 的流式智能体系统，支持智能体之间的交接（handoff）功能、自定义系统提示词和工具定义。主要特性包括：

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 基础智能体使用

```python
from llm import llm
from agent import Agent
from chat import ChatWithAgent

# 创建一个基础智能体
agent = Agent(
    llm=llm,
    system_prompt="你是一个有用的助手",
    tools=[],
    name="助手"
)

# 创建对话接口
chatter = ChatWithAgent(agent)

# 开始对话
await chatter.chat("你好！")
```

### 2. 工具定义和使用

#### 创建自定义工具

```python
from llama_index.core.tools import FunctionTool

def add_wechat_account(account: str):
    """添加用户的微信账号到系统中"""
    print(f"🔧添加微信账号: {account}")
    return f"微信账号 {account} 已添加"

# 将函数转换为工具
wechat_tool = FunctionTool.from_defaults(
    fn=add_wechat_account,
    name="add_wechat_account",
    description="添加客户的微信账号到系统中，添加前需要确认账号格式正确"
)
```

#### 将工具分配给智能体

```python
agent_with_tools = Agent(
    llm=llm,
    system_prompt="你是微信客服，可以帮助用户添加微信账号",
    tools=[wechat_tool],
    name="微信客服"
)
```

### 3. 自定义系统提示词

#### 在 prompts.py 中定义提示词

```python
# prompts.py
CUSTOMER_SERVICE_SYSTEM_PROMPT = """
你是一个有用的客服智能体，负责回答客户问题并帮助解决iPhone设备问题。
如果客户想要添加微信账号，使用"handoff_to_wechat_customer_service_agent"工具交接给微信客服。
在回答微信或微信号相关问题时，务必使用交接工具。

客户姓名 = "易小鑫"
"""

WECHAT_SYSTEM_PROMPT = """
你是微信客服智能体，帮助客户添加微信账号并回答相关问题。
在调用工具前，你应该询问客户的微信账号并确认账号格式正确。
你可以使用"add_wechat_account"工具将客户的微信账号添加到系统中。

客户姓名 = "易小鑫"
客户电话 = 18612345678
"""
```

#### 使用自定义提示词

```python
from prompts import CUSTOMER_SERVICE_SYSTEM_PROMPT, WECHAT_SYSTEM_PROMPT

customer_service_agent = Agent(
    llm=llm,
    system_prompt=CUSTOMER_SERVICE_SYSTEM_PROMPT,
    tools=[],
    name="客服智能体"
)

wechat_agent = Agent(
    llm=llm,
    system_prompt=WECHAT_SYSTEM_PROMPT,
    tools=[wechat_tool],
    name="微信客服智能体"
)
```

## 智能体交接功能

### 顺序交接智能体 (SequentialHandoffAgent)

这是最常用的交接模式，允许从一个主智能体交接到另一个专门化智能体。

```python
from handoff import SequentialHandoffAgent

# 创建交接智能体
handoff_agent = SequentialHandoffAgent(
    root_agent=customer_service_agent,    # 主智能体
    handoff_to_agent=wechat_agent        # 交接目标智能体
)

# 使用交接智能体
chatter = ChatWithAgent(handoff_agent)
```

### 交接工作流程

1. **初始阶段**: 用户与主智能体（root_agent）交互
2. **触发交接**: 当主智能体识别到需要专门处理的请求时，调用交接工具
3. **智能体切换**: 系统自动切换到目标智能体（handoff_to_agent）
4. **专门处理**: 目标智能体使用其专门的工具和知识处理请求
5. **持续对话**: 后续对话继续在目标智能体上进行

### 交接示例场景

```python
# 用户开始对话
await chatter.chat("你好")
# -> 客服智能体回应

await chatter.chat("怎么用airdrop传文件？")
# -> 客服智能体提供技术支持

await chatter.chat("咱们加微信说吧")
# -> 客服智能体识别到微信相关需求，自动交接给微信客服

await chatter.chat("我的微信号是 user123")
# -> 微信客服智能体处理并添加微信账号
```

