from langchain_openai import ChatOpenAI
import os 
from utils.constants import OPENAI_API_KEY,OPENAI_MODEL_4O_MINI
from llms.llm import LLM

class OpenAILLM(LLM):
    def __init__(self):
        super().__init__()

    def get_llm(self,mode_name=OPENAI_MODEL_4O_MINI):
        try:
            print("Trying to set groq api key")
            os.environ["OPENAI_API_KEY"]=self.openai_api_key=os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                raise ValueError("Open ai api key not found")
            llm=ChatOpenAI(temperature=1,openai_api_key=self.openai_api_key,model=mode_name)
            return llm
        except Exception as e:
            raise ValueError("Error occurred with exception : {e}") 