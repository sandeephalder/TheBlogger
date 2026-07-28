import os 
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from utils.constants import GLM_MODEL_4_7, GLM_API_BASE
from langchain_openai import ChatOpenAI
from llms.llm import LLM

load_dotenv()

class GLMLLM(LLM):
    def __init__(self):
        super().__init__()

    def get_llm(self, mode_name=GLM_MODEL_4_7):
        try:
            print("Trying to set glm api key")
            os.environ["GLM_API_KEY"] = self.glm_api_key = os.getenv("GLM_API_KEY")
            if not self.glm_api_key:
                raise ValueError("Glm api key not found")
            llm = ChatOpenAI(
                model=mode_name,
                openai_api_key=self.glm_api_key,
                openai_api_base=GLM_API_BASE
            )
            return llm
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}")

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage, SystemMessage
    
    try:
        glm = GLMLLM()
        llm = glm.get_llm()
        messages = [
            SystemMessage(content="You are a smart and creative novelist."),
            HumanMessage(content="Please write a short fairy tale story as a fairy tale master.")
        ]
        response = llm.invoke(messages)
        print("--- GLM Response ---")
        print(response.content)
    except Exception as e:
        print(f"Connection Error: {e}")