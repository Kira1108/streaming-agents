from llama_index.core.tools import FunctionTool
from tools import add, multiply
from agent import Agent

class SequentialHandoffAgent:
    
    def __init__(self, 
                 root_agent:Agent, 
                 handoff_to_agent:Agent):
        
        self.root_agent = root_agent
        self.handoff_to_agent = handoff_to_agent
        
        self.root_agent.extend_tools(
            [
                FunctionTool.from_defaults(
                    fn = self.handoff_to_wechat_customer_service_agent,
                    name = "handoff_to_wechat_customer_service_agent",
                    description="If the upstream agent determines to add the customer's wechat account, handoff to wechat customer service agent using this tool.",
                    return_direct=False
                )
            ]
        )
        
        self.current_agent = self.root_agent
    
    def handoff_to_wechat_customer_service_agent(self):
        """If the upstream agent determines to add the customer's wechat account, handoff to wechat customer service agent using this tool."""
        print("[日志通知]Handoff to WeChat customer service agent")
        self.current_agent = self.handoff_to_agent
        return "You are now connected to a WeChat customer service agent."
    
    
    async def run(self, messages:list):
        async for event in self.current_agent.run(messages):
            yield event