import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from blueprint.agent_flow import AgentFlow
from llms.llm_factory import LLMFactory
from utils.constants import GLM_4_7_FLASH,LLM_PROVIDER_GLM, GLM_MODEL_4_7, LLM_PROVIDER_OLLAMA, OLLAMA_MODEL_DEFAULT, LLM_PROVIDER_GEMINI, GEMINI_MODEL_FLASH
from utils.colors import print_cyan, print_green, print_red, print_yellow

if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

def run_blog_generator(topic: str):
    """Executes the agent flow graph directly for the given blog topic."""
    print_cyan(f"\n🚀 Starting Blog Generation for topic: '{topic}'...\n")
    
    # Get the LLM object
    # llm = LLMFactory().get_llm(LLM_PROVIDER_OLLAMA, OLLAMA_MODEL_DEFAULT)
    # llm = LLMFactory().get_llm(LLM_PROVIDER_GEMINI, GEMINI_MODEL_FLASH)
    llm = LLMFactory().get_llm(LLM_PROVIDER_GLM, GLM_4_7_FLASH)
    
    # Setup AgentFlow graph
    agent_flow = AgentFlow(llm)
    graph = agent_flow.setup_blog_flow("blog")
    
    # Invoke the graph state directly
    state = graph.invoke({"topic": topic})
    
    print_green("\n✅ Execution Complete!\n")
    print_cyan("=" * 60)
    print_green(str(state))
    print_cyan("=" * 60)
    return state

def main():
    parser = argparse.ArgumentParser(description="TheBlogger CLI Generator")
    parser.add_argument("--topic", "-t", type=str, help="Topic for the blog post")
    
    args = parser.parse_args()
    
    topic = args.topic
    if not topic:
        try:
            topic = input("Enter blog topic: ").strip()
        except (KeyboardInterrupt, EOFError):
            print_yellow("\nAborted.")
            sys.exit(0)
            
    if not topic:
        print_red("Error: Topic cannot be empty.")
        sys.exit(1)
        
    run_blog_generator(topic)

if __name__ == "__main__":
    main()
