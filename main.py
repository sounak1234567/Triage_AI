import os
from fastapi import FastAPI
from flask import Flask, request, jsonify
from langgraph.graph import add_messages
from langchain.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from typing import TypedDict, Annotated
from apps import app as workflow_app
from apps import guest_app
from apps import EmergencyAnalysis, EmergencyResponse, GuestState
from ingestion_loading import cook_protocols
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()


client = genai.Client(project=os.getenv("PROJECT"))

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

@app.post('/guest_help')
async def guest_help(request: GuestState):
    print(request)
    
    initial_state = {
        "messages": [HumanMessage(content=request["messages"])],
        "session_summary": str(request["session_summary"]),
        "incident_type": str(request["incident_type"]),
    }
    return await guest_app.ainvoke(GuestState(**initial_state)) 

@app.post('/init')
async def initialize(request):
    cook_protocols()
