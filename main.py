import os
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from pydantic import BaseModel

load_dotenv()

class EmergencyAnalysis(TypedDict):
    messages: Annotated[list, add_messages]
    incident_type: str
    severity: int
    trapped_status: str

class EmergencyResponse(BaseModel):
    summary: str
    incident_type: str
    severity: int
    trapped_status: str

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
emergency_structured_llm = llm.with_structured_output(EmergencyResponse)

def triage_node(state: EmergencyAnalysis) -> EmergencyAnalysis:
    prompt = f"""
    Analyze the following emergency message from a hotel guest. 
    Extract:
    1. Incident Type (Fire, Medical, Security, Infrastructure)
    2. Severity (1-10)
    3. Trapped Status (Yes/No)

    Return ONLY a JSON object.
    Message: "{state['messages'][-1].content}"
    """
    print(f"{state}")
    response = emergency_structured_llm.invoke(prompt)
    return {
        "messages": state["messages"] + [AIMessage(content=response.summary)], # type: ignore
        "incident_type": response.incident_type, # type: ignore
        "severity": response.severity, # type: ignore
        "trapped_status":response.trapped_status #type: ignore
    }

workflow = StateGraph(EmergencyAnalysis)
workflow.add_node("triage", triage_node)
workflow.set_entry_point("triage")
workflow.add_edge("triage", END)

app = workflow.compile()
