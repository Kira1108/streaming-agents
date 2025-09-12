from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama
from tools import add, multiply
from dataclasses import dataclass
from typing import List

from llama_index.core.agent.workflow import (AgentInput, AgentOutput,
                                             AgentStream, FunctionAgent,
                                             ToolCallResult)
from dataclasses import dataclass, field


@dataclass
class ToolCallEvent:
    message:dict
    
@dataclass
class ToolCallResultEvent:
    message:dict
    
@dataclass
class TextStreamDeltaEvent:
    delta:str
    
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant, when answering questions you always use `multiply` and `add` to do all multiplications and additions. always use emojis in your answers."
   
@dataclass 
class Agent:
    llm:Ollama = field(
        default_factory=lambda: Ollama(model="qwen3:8b", request_timeout=60.0, thinking=False)
    )
    system_prompt:str = DEFAULT_SYSTEM_PROMPT
    tools:List = field(default_factory=lambda: [multiply, add])
    
    def __post_init__(self):
            
        self.agent = FunctionAgent(
            llm=self.llm,
            system_prompt=self.system_prompt,
            tools = self.tools
        )
        
    def print_messages(self, messages):
        print("=== Chat Messages ===")
        for msg in messages:
            role = msg.get('role', 'UnknownRole')
            content = msg.get('content', '')
            print(f"--{role}: {content}")
        print("=====================")
            
    async def run(self, messages:List[dict]):
        self.print_messages(messages)
        messages = [ChatMessage.model_validate(m) for m in messages]
        
        handler = self.agent.run(chat_history = messages)
        
        async for event in handler.stream_events():
            if isinstance(event, AgentStream):
                yield TextStreamDeltaEvent(delta=event.delta)
                
            elif isinstance(event, AgentInput):
                pass
                
            elif isinstance(event, AgentOutput):
                if len(event.response.additional_kwargs['tool_calls']) > 0:
                    tool_call_message = event.response.model_dump()
                    yield ToolCallEvent(message=tool_call_message)
                    
            elif isinstance(event, ToolCallResult): 
                tool_result_message = ChatMessage(
                    role = 'tool',
                    content = event.tool_output.content,
                    additional_kwargs={"tool_call_id": event.tool_id}
                ).model_dump()
                yield ToolCallResultEvent(message=tool_result_message)