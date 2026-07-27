from utils.constants import LLM_PROVIDER_GEMINI
from llms.llm_factory import LLMFactory
from utils.constants import GEMINI_MODEL_FLASH,LLM_PROVIDER_GEMINI
import os
import base64
from dotenv import load_dotenv



def test_blogger_wordpress():
    # 1. Target the Official WordPress.com Remote MCP Engine Endpoint
    # See documentation at https://wordpress.com
    wp_mcp_url = os.getenv("WORDPRESS_URL")
    
    # 2. Construct Basic Authentication Headers
    username = os.getenv("WORDPRESS_USERNAME")
    password = os.getenv("WORDPRESS_PASSWORD")
    auth_str = f"{username}:{password}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/json"
    }
    
    print("Connecting to WordPress.com MCP server...")
    

    

def test_connector_llm():

    # 2. Initialize your model as usual
    #llm = LLMFactory().get_llm(LLM_PROVIDER_GEMINI,GEMINI_MODEL_FLASH)
    llm = LLMFactory().get_llm(LLM_PROVIDER_GEMINI, GEMINI_MODEL_FLASH)

    # 3. Execute your run
    # This call is automatically intercepted and sent to your LangSmith project dashboard
    print("Sending request to Gemini...")
    response = llm.invoke("What are the core benefits of tracing LLM applications?")

    print("\nResponse:")
    print(response.content)
    print("\nSuccess! Open https://langchain.com to view your trace logs.")
    


if __name__ == "__main__":
    load_dotenv()
    test_connector_llm()



