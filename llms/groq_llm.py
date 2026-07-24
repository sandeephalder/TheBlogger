from langchain_groq import ChatGroq
import os 
from utils.constants import GROQ_MODEL_INSTA,GROQ_API_KEY
from llms.llm import LLM

class GroqLLM(LLM):
    def __init__(self):
        super().__init__()

    def get_llm(self,mode_name=GROQ_MODEL_INSTA):
        try:
            print("Trying to set groq api key")
            os.environ["GROQ_API_KEY"]=self.groq_api_key=os.getenv("GROQ_API_KEY")
            if not self.groq_api_key:
                raise ValueError("Groq api key not found")
            llm=ChatGroq(api_key=self.groq_api_key,model=mode_name)
            return llm
        except Exception as e:
            raise ValueError("Error occurred with exception : {e}") 