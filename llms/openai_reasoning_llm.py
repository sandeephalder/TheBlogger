import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from langchain_openai import ChatOpenAI
from llms.llm import LLM
from utils.constants import OPENAI_MODEL_GPT_5_4_MINI, OPENAI_REASONING_EFFORT_MEDIUM

load_dotenv()

class OpenAIReasoningLLM(LLM):
    """
    Wrapper for OpenAI's reasoning models (gpt-5.x / o-series).

    These models differ from the regular chat models in two ways that matter here:
    they take a `reasoning_effort` budget, and they reject a custom `temperature`,
    so we deliberately do not pass one.
    """

    def __init__(self):
        super().__init__()

    def get_llm(self, mode_name=OPENAI_MODEL_GPT_5_4_MINI, reasoning_effort=OPENAI_REASONING_EFFORT_MEDIUM):
        try:
            print("Trying to set openai api key")
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                raise ValueError("Open ai api key not found")
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
            llm = ChatOpenAI(
                model=mode_name,
                openai_api_key=self.openai_api_key,
                reasoning_effort=reasoning_effort,
            )
            return llm
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}")

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage, SystemMessage

    try:
        openai_reasoning = OpenAIReasoningLLM()
        llm = openai_reasoning.get_llm()
        messages = [
            SystemMessage(content="आप एक सहायक हैं। हमेशा हिंदी में उत्तर दें।"),
            HumanMessage(content="भारत में मानसून क्यों आता है? संक्षेप में समझाइए।")
        ]
        response = llm.invoke(messages)
        print("--- OpenAI Reasoning Response ---")
        print(response.content)
    except Exception as e:
        print(f"Connection Error: {e}")
