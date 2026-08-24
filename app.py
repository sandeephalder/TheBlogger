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
)

import os
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

    graph=get_hindi_chat_graph()
    state=graph.invoke(
        {"messages":[HumanMessage(content=message)]},
        config={"configurable":{"thread_id":thread_id}},
    )

    return {"reply":state["messages"][-1].content,"thread_id":thread_id}

if __name__=="__main__":
    uvicorn.run("app:app",host="0.0.0.0",port=8000,reload=True)
