import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_core.messages import HumanMessage
from blueprint.chat_flow import ChatFlow
from llms.llm_factory import LLMFactory
from utils.constants import (
    LLM_PROVIDER_OPENAI_REASONING,
    OPENAI_MODEL_GPT_5_6,
    OPENAI_MODEL_GPT_5_4,
    OPENAI_MODEL_GPT_5_4_MINI,
    OPENAI_MODEL_O4_MINI,
    OPENAI_REASONING_EFFORT_LOW,
    OPENAI_REASONING_EFFORT_MEDIUM,
    OPENAI_REASONING_EFFORT_HIGH,
    HINDI_CHAT_THREAD_ID,
)
from utils.colors import print_cyan, print_green, print_red, print_yellow

if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

SUPPORTED_MODELS = [
    OPENAI_MODEL_GPT_5_4_MINI,
    OPENAI_MODEL_GPT_5_4,
    OPENAI_MODEL_GPT_5_6,
    OPENAI_MODEL_O4_MINI,
]
REASONING_EFFORTS = [
    OPENAI_REASONING_EFFORT_LOW,
    OPENAI_REASONING_EFFORT_MEDIUM,
    OPENAI_REASONING_EFFORT_HIGH,
]
EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit", "बाहर", "बंद"}

def build_hindi_chat_graph(model: str, reasoning_effort: str):
    """Wire an OpenAI reasoning model into the Hindi chat graph."""
    llm = LLMFactory().get_llm(
        LLM_PROVIDER_OPENAI_REASONING,
        model,
        reasoning_effort=reasoning_effort,
    )
    return ChatFlow(llm).setup_chat_flow("hindi")

def run_hindi_chat(model: str, reasoning_effort: str, thread_id: str):
    """Runs an interactive Hindi conversation against the compiled graph."""
    print_cyan(f"\n🚀 हिंदी चैट एजेंट शुरू हो रहा है (model: {model}, reasoning: {reasoning_effort})...\n")

    graph = build_hindi_chat_graph(model, reasoning_effort)
    # The thread_id is the conversation key — the checkpointer replays this
    # thread's history on every turn, which is what makes the agent multi-turn.
    config = {"configurable": {"thread_id": thread_id}}

    print_yellow("बाहर निकलने के लिए 'exit' लिखें।\n")

    while True:
        try:
            user_input = input("आप: ").strip()
        except (KeyboardInterrupt, EOFError):
            print_yellow("\nनमस्ते! 🙏")
            break

        if not user_input:
            continue
        if user_input.lower() in EXIT_COMMANDS:
            print_yellow("\nनमस्ते! 🙏")
            break

        try:
            graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
        except Exception as e:
            print_red(f"\n❌ त्रुटि: {e}\n")

def main():
    parser = argparse.ArgumentParser(description="TheBlogger Hindi Chat Agent")
    parser.add_argument("--model", "-m", type=str, default=OPENAI_MODEL_GPT_5_4_MINI,
                        choices=SUPPORTED_MODELS, help="OpenAI reasoning model to use")
    parser.add_argument("--effort", "-e", type=str, default=OPENAI_REASONING_EFFORT_MEDIUM,
                        choices=REASONING_EFFORTS, help="How much the model reasons before answering")
    parser.add_argument("--thread", "-t", type=str, default=HINDI_CHAT_THREAD_ID,
                        help="Conversation thread id (memory is scoped to this)")
    parser.add_argument("--message", type=str, help="Send a single message and exit instead of chatting")

    args = parser.parse_args()

    if args.message:
        graph = build_hindi_chat_graph(args.model, args.effort)
        config = {"configurable": {"thread_id": args.thread}}
        graph.invoke({"messages": [HumanMessage(content=args.message)]}, config=config)
        return

    run_hindi_chat(args.model, args.effort, args.thread)

if __name__ == "__main__":
    main()
