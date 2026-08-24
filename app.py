import uvicorn
from fastapi import FastAPI, Request
from blueprint.agent_flow import AgentFlow
from blueprint.chat_flow import ChatFlow
from llms.llm_factory import LLMFactory
from langchain_core.messages import HumanMessage
from utils.constants import (
    LLM_PROVIDER_GEMINI,
    GEMINI_MODEL_FLASH,
    LLM_PROVIDER_OPENAI_REASONING,
    OPENAI_MODEL_GPT_5_4_MINI,
    OPENAI_REASONING_EFFORT_MEDIUM,
    HINDI_CHAT_THREAD_ID,
    SARVAM_LANGUAGE_HINDI,
    SARVAM_TTS_SPEAKER_DEFAULT,
)

import os
import base64
import tempfile
from dotenv import load_dotenv
load_dotenv()

app=FastAPI()

if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")

## Built on first use so the API still starts without an OpenAI key configured.
## Holding one compiled graph keeps the in-memory checkpointer alive across requests.
_hindi_chat_graph = None

def get_hindi_chat_graph():
    global _hindi_chat_graph
    if _hindi_chat_graph is None:
        llm = LLMFactory().get_llm(
            LLM_PROVIDER_OPENAI_REASONING,
            OPENAI_MODEL_GPT_5_4_MINI,
            reasoning_effort=OPENAI_REASONING_EFFORT_MEDIUM,
        )
        _hindi_chat_graph = ChatFlow(llm).setup_chat_flow("hindi")
    return _hindi_chat_graph

_sarvam_speech = None

def get_sarvam_speech():
    """Imported lazily so the text routes work without a Sarvam key."""
    global _sarvam_speech
    if _sarvam_speech is None:
        from tools.sarvam_speech import SarvamSpeech
        _sarvam_speech = SarvamSpeech()
    return _sarvam_speech

def run_chat_turn(message, thread_id):
    graph=get_hindi_chat_graph()
    state=graph.invoke(
        {"messages":[HumanMessage(content=message)]},
        config={"configurable":{"thread_id":thread_id}},
    )
    return state["messages"][-1].content

## API's

@app.post("/blogs")
async def create_blogs(request:Request):
    
    data=await request.json()
    topic= data.get("topic","")

    ## get the llm object
    llm = LLMFactory().get_llm(LLM_PROVIDER_GEMINI, GEMINI_MODEL_FLASH)
    agent_flow=AgentFlow(llm)
    if topic:
        graph=agent_flow.setup_blog_flow("blog")
        state=graph.invoke({"topic":topic})

    return {"data":state}

@app.post("/chat")
async def hindi_chat(request:Request):

    data=await request.json()
    message=data.get("message","")
    thread_id=data.get("thread_id",HINDI_CHAT_THREAD_ID)

    if not message:
        return {"error":"message is required"}

    return {"reply":run_chat_turn(message,thread_id),"thread_id":thread_id}

@app.post("/chat/voice")
async def hindi_chat_voice(request:Request):
    """
    Speak in, speak out. The audio comes in base64 encoded, Sarvam Saaras turns
    it into English text, the agent answers, and Sarvam Bulbul voices the reply.
    """

    data=await request.json()
    audio_base64=data.get("audio_base64","")
    thread_id=data.get("thread_id",HINDI_CHAT_THREAD_ID)
    tts_language=data.get("tts_language",SARVAM_LANGUAGE_HINDI)
    speaker=data.get("speaker",SARVAM_TTS_SPEAKER_DEFAULT)
    speak_reply=data.get("speak",True)

    if not audio_base64:
        return {"error":"audio_base64 is required"}

    speech=get_sarvam_speech()

    with tempfile.TemporaryDirectory() as workdir:
        input_path=os.path.join(workdir,"input.wav")
        with open(input_path,"wb") as f:
            f.write(base64.b64decode(audio_base64))

        transcript=speech.speech_to_english_text(input_path)
        reply=run_chat_turn(transcript,thread_id)

        reply_audio_base64=None
        if speak_reply:
            output_path=os.path.join(workdir,"reply.wav")
            speech.text_to_speech(reply,output_path,language_code=tts_language,speaker=speaker)
            with open(output_path,"rb") as f:
                reply_audio_base64=base64.b64encode(f.read()).decode("utf-8")

    return {
        "transcript":transcript,
        "reply":reply,
        "reply_audio_base64":reply_audio_base64,
        "thread_id":thread_id,
    }

if __name__=="__main__":
    uvicorn.run("app:app",host="0.0.0.0",port=8000,reload=True)
