from llms.llm_factory import LLMFactory
from utils.constants import LLM_PROVIDER_DEEPSEEK,DEEPSEEK_MODEL_V3_CHAT,LLM_PROVIDER_GEMINI,GEMINI_MODEL_FLASH,LLM_PROVIDER_GROQ,GROQ_MODEL_INSTA,OPENAI_MODEL_4O_MINI,LLM_PROVIDER_OPENAI



def test_connector():

    # 2. Initialize your model as usual
    #llm = LLMFactory().get_llm(LLM_PROVIDER_GEMINI,GEMINI_MODEL_FLASH)
    llm = LLMFactory().get_llm(LLM_PROVIDER_DEEPSEEK,DEEPSEEK_MODEL_V3_CHAT)

    # 3. Execute your run
    # This call is automatically intercepted and sent to your LangSmith project dashboard
    print("Sending request to Gemini...")
    response = llm.invoke("What are the core benefits of tracing LLM applications?")

    print("\nResponse:")
    print(response.content)
    print("\nSuccess! Open https://langchain.com to view your trace logs.")
    


if __name__ == "__main__":
    test_connector()



