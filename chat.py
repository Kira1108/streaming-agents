from agent import Agent, TextStreamDeltaEvent

class ChatWithAgent:
    
    def __init__(self, agent:Agent):
        self.agent = agent
        self.messages = []
        
    async def chat(self, message:str):
        self.messages.append({'role': 'user', 'content': message})
        buffer = ""
        async for event in self.agent.run(self.messages):
            if isinstance(event, TextStreamDeltaEvent):
                buffer += event.delta
                print(event.delta, end="", flush=True)
            else:
                self.messages.append(event.message)
        self.messages.append({"role": "assistant", "content": buffer})
        
        if hasattr(self.agent, "on_change") and self.agent.on_change:
            await self.chat(message)
            self.agent.on_change = False