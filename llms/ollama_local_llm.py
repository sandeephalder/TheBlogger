import os
from utils.constants import OLLAMA_MODEL_DEFAULT, OLLAMA_BASE_URL
from llms.llm import LLM

try:
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models import ChatOllama

class OllamaLocalLLM(LLM):
    def __init__(self):
        super().__init__()

    def get_llm(self, model_name=OLLAMA_MODEL_DEFAULT, base_url=None):
        try:
            print(f"Connecting to local Ollama server with model: {model_name}")
            base_url = base_url or os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
            llm = ChatOllama(
                model=model_name,
                base_url=base_url
            )
            return llm
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}")
