import uvicorn
from fastapi import FastAPI, Request
from blueprint.agent_flow import AgentFlow
from llms.llm_factory import LLMFactory
from utils.constants import LLM_PROVIDER_GEMINI, GEMINI_MODEL_FLASH

import os
from dotenv import load_dotenv
load_dotenv()

app=FastAPI()

print(os.getenv("LANGCHAIN_API_KEY"))

os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")

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

if __name__=="__main__":
    uvicorn.run("app:app",host="0.0.0.0",port=8000,reload=True)

