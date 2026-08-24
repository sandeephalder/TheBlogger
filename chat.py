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
    SARVAM_LANGUAGE_HINDI,
    SARVAM_LANGUAGE_ENGLISH,
    SARVAM_TTS_SPEAKER_DEFAULT,
    SARVAM_STT_MODE_TRANSLATE,
    SARVAM_STT_MODE_TRANSCRIBE,
    VOICE_OUTPUT_DIR,
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
STT_MODES = [SARVAM_STT_MODE_TRANSLATE, SARVAM_STT_MODE_TRANSCRIBE]
EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit", "बाहर", "बंद"}

def build_hindi_chat_graph(model: str, reasoning_effort: str):
    """Wire an OpenAI reasoning model into the Hindi chat graph."""
    llm = LLMFactory().get_llm(
        LLM_PROVIDER_OPENAI_REASONING,
        model,
        reasoning_effort=reasoning_effort,
    )
    return ChatFlow(llm).setup_chat_flow("hindi")

def build_speech():
    """Imported lazily so text-only chat never needs a Sarvam key installed."""
    from tools.sarvam_speech import SarvamSpeech
    return SarvamSpeech()

def transcribe(speech, audio_path: str, stt_mode: str) -> str:
    """Turn an audio file into text — English by default, via Sarvam Saaras."""
    if stt_mode == SARVAM_STT_MODE_TRANSLATE:
        return speech.speech_to_english_text(audio_path)
    return speech.speech_to_text(audio_path)

def speak_reply(speech, reply: str, args, turn: int) -> str:
    """Voice the agent's reply with Sarvam Bulbul."""
    out_path = os.path.join(args.voice_out, f"reply_{turn}.wav")
    return speech.text_to_speech(
        reply,
        out_path,
        language_code=args.tts_lang,
        speaker=args.speaker,
    )

def send_turn(graph, config, message: str) -> str:
    """Run one turn through the graph and hand back the agent's reply text."""
    state = graph.invoke({"messages": [HumanMessage(content=message)]}, config=config)
    return state["messages"][-1].content

def run_hindi_chat(args):
    """Runs an interactive Hindi conversation against the compiled graph."""
    print_cyan(f"\n🚀 हिंदी चैट एजेंट शुरू हो रहा है (model: {args.model}, reasoning: {args.effort})...\n")

    graph = build_hindi_chat_graph(args.model, args.effort)
    # The thread_id is the conversation key — the checkpointer replays this
    # thread's history on every turn, which is what makes the agent multi-turn.
    config = {"configurable": {"thread_id": args.thread}}
    speech = build_speech() if args.speak else None

    print_yellow("बाहर निकलने के लिए 'exit' लिखें।")
    if args.speak:
        print_yellow(f"उत्तर की ऑडियो '{args.voice_out}/' में सहेजी जाएगी।")
    print("")

    turn = 0
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
            turn += 1
            reply = send_turn(graph, config, user_input)
            if speech:
                speak_reply(speech, reply, args, turn)
        except Exception as e:
            print_red(f"\n❌ त्रुटि: {e}\n")

def run_single_turn(args, message: str = None):
    """One message in, one reply out — text or voice on either side."""
    graph = build_hindi_chat_graph(args.model, args.effort)
    config = {"configurable": {"thread_id": args.thread}}
    speech = build_speech() if (args.audio or args.speak) else None

    if args.audio:
        message = transcribe(speech, args.audio, args.stt_mode)

    reply = send_turn(graph, config, message)

    if args.speak:
        speak_reply(speech, reply, args, turn=1)

def main():
    parser = argparse.ArgumentParser(description="TheBlogger Hindi Chat Agent")
    parser.add_argument("--model", "-m", type=str, default=OPENAI_MODEL_GPT_5_4_MINI,
                        choices=SUPPORTED_MODELS, help="OpenAI reasoning model to use")
    parser.add_argument("--effort", "-e", type=str, default=OPENAI_REASONING_EFFORT_MEDIUM,
                        choices=REASONING_EFFORTS, help="How much the model reasons before answering")
    parser.add_argument("--thread", "-t", type=str, default=HINDI_CHAT_THREAD_ID,
                        help="Conversation thread id (memory is scoped to this)")
    parser.add_argument("--message", type=str, help="Send a single message and exit instead of chatting")

    voice = parser.add_argument_group("voice (Sarvam)")
    voice.add_argument("--audio", type=str,
                       help="Audio file to send as the message (transcribed with Sarvam Saaras)")
    voice.add_argument("--stt-mode", type=str, default=SARVAM_STT_MODE_TRANSLATE, choices=STT_MODES,
                       help="translate: speech to English text. transcribe: keep the spoken language")
    voice.add_argument("--speak", action="store_true",
                       help="Voice each reply with Sarvam Bulbul")
    voice.add_argument("--tts-lang", type=str, default=SARVAM_LANGUAGE_HINDI,
                       help=f"Language of the spoken reply, e.g. {SARVAM_LANGUAGE_HINDI} or {SARVAM_LANGUAGE_ENGLISH}")
    voice.add_argument("--speaker", type=str, default=SARVAM_TTS_SPEAKER_DEFAULT,
                       help="Bulbul voice to speak with")
    voice.add_argument("--voice-out", type=str, default=VOICE_OUTPUT_DIR,
                       help="Directory for generated audio")

    args = parser.parse_args()

    if args.audio:
        run_single_turn(args)
        return

    if args.message:
        run_single_turn(args, args.message)
        return

    run_hindi_chat(args)

if __name__ == "__main__":
    main()
