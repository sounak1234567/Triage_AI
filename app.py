from fastapi import FastAPI
from langgraph.graph import add_messages
from langchain.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from typing import TypedDict, Annotated
from main import app as workflow_app, EmergencyAnalysis, EmergencyResponse

app = FastAPI()

@app.post("/triage")
async def triage(request: EmergencyAnalysis):
    print(request)
    
    initial_state = {
        "messages": [HumanMessage(content=request["messages"])], 
        "incident_type": str(request["incident_type"]),
        "severity": str(request["severity"]), 
        "trapped_status": bool(request["trapped_status"]), 
    }
    return await workflow_app.ainvoke(EmergencyAnalysis(**initial_state)) 
