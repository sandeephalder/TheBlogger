
from utils.constants import LLM_PROVIDER_GEMINI, LLM_PROVIDER_GROQ, LLM_PROVIDER_OPENAI, LLM_PROVIDER_DEEPSEEK, LLM_PROVIDER_OLLAMA, LLM_PROVIDER_QWEN, LLM_PROVIDER_GLM
from llms.gemini_llm import GeminiLLM
from llms.groq_llm import GroqLLM
from llms.openapi_llm import OpenAILLM
from llms.deepseek_llm import DeepSeekLLM
from llms.ollama_local_llm import OllamaLocalLLM
from llms.qwen_llm import QwenLLM
from llms.glm_llm import GLMLLM

class LLMFactory:
    def __init__(self):
        pass
    
    def get_llm(self, llm_name, model_name):
        try:
            if llm_name == LLM_PROVIDER_GEMINI:
                gemini = GeminiLLM()
                return gemini.get_llm(model_name)
            elif llm_name == LLM_PROVIDER_GROQ:
                groq = GroqLLM()
                return groq.get_llm(model_name)
            elif llm_name == LLM_PROVIDER_OPENAI:
                openai = OpenAILLM()
                return openai.get_llm(model_name)
            elif llm_name == LLM_PROVIDER_DEEPSEEK:
                deepseek = DeepSeekLLM()
                return deepseek.get_llm(model_name)
            elif llm_name == LLM_PROVIDER_OLLAMA:
                ollama = OllamaLocalLLM()
                return ollama.get_llm(model_name)
            elif llm_name == LLM_PROVIDER_QWEN:
                qwen = QwenLLM()
                return qwen.get_llm(model_name)
            elif llm_name == LLM_PROVIDER_GLM:
                glm = GLMLLM()
                return glm.get_llm(model_name)
            else:
                raise ValueError("Invalid LLM name")
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}") 