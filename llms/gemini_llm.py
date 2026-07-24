from google import genai
import os 
from utils.constants import GEMINI_MODEL_PRO,GEMINI_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from llms.llm import LLM

class GeminiLLM(LLM):
    def __init__(self):
        super().__init__()

    def get_llm(self,mode_name=GEMINI_MODEL_PRO):
        try:
            print("Trying to set gemini api key")
            os.environ["GEMINI_API_KEY"]=self.gemini_api_key=os.getenv("GEMINI_API_KEY")
            if not self.gemini_api_key:
                raise ValueError("Gemini api key not found")
            llm=ChatGoogleGenerativeAI(model=mode_name,google_api_key=self.gemini_api_key)
            return llm
        except Exception as e:
            raise ValueError("Error occurred with exception : {e}") 