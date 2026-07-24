from langchain_deepseek import ChatDeepSeek
from openai import OpenAI
import os 
from utils.constants import DEEPSEEK_API_KEY,DEEPSEEK_MODEL_CHAT,DEEPSEEK_API_BASE
from llms.llm import LLM

class DeepSeekLLM(LLM):
    def __init__(self):
        super().__init__()

    def get_llm(self,mode_name=DEEPSEEK_MODEL_CHAT):
        try:
            print("Trying to set groq api key")
            os.environ["DEEPSEEK_API_KEY"]=self.deepseek_api_key=os.getenv("DEEPSEEK_API_KEY")
            if not self.deepseek_api_key:
                raise ValueError("Deepseek api key not found")
       
            llm= ChatDeepSeek(
                model=mode_name,
                api_key=self.deepseek_api_key         
            )
            return llm
        except Exception as e:
            raise ValueError("Error occurred with exception : {e}") 