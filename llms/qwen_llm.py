import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from langchain_openai import ChatOpenAI
from utils.constants import QWEN_MODEL_PLUS, DASHSCOPE_API_BASE
from llms.llm import LLM

load_dotenv()

class QwenLLM(LLM):
    def __init__(self):
        super().__init__()

    def get_llm(self, model_name=QWEN_MODEL_PLUS, api_key=None, api_base=None):
        try:
            print(f"Initializing Qwen model: {model_name}")
            api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
            if not api_key:
                raise ValueError("DashScope/Qwen API Key not found. Please set DASHSCOPE_API_KEY or QWEN_API_KEY in your .env file.")
                
            api_base = api_base or os.getenv("DASHSCOPE_API_BASE", DASHSCOPE_API_BASE)
            
            llm = ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                openai_api_base=api_base,
                temperature=0.7,
                max_tokens=512
            )
            return llm
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}")

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage, SystemMessage
    
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
    if not api_key:
        print("\n⚠️  Error: DASHSCOPE_API_KEY or QWEN_API_KEY is not set in your .env file.")
        print("Please add DASHSCOPE_API_KEY=\"sk-your-dashscope-key\" to your .env file.")
    else:
        try:
            qwen = QwenLLM()
            llm = qwen.get_llm()
            messages = [
                SystemMessage(content="You are a helpful AI agent powered by Qwen."),
                HumanMessage(content="Explain the core benefit of an agentic workflow in 20 words.")
            ]
            response = llm.invoke(messages)
            print("--- Qwen Response ---")
            print(response.content)
        except Exception as e:
            print(f"Connection Error: {e}")
