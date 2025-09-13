from llama_index.llms.ollama import Ollama

llm = Ollama(model="qwen3:8b", request_timeout=60.0, thinking=False)