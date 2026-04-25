import os
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from ingestion_loading import get_protocol_context
from pydantic import BaseModel

load_dotenv()

class EmergencyAnalysis(TypedDict):
    messages: Annotated[list, add_messages]
    incident_type: str
    severity: int
    trapped_status: str

class GuestState(TypedDict):
    messages: Annotated[list, add_messages]
    session_summary: str
    incident_type: str

class EmergencyResponse(BaseModel):
    summary: str
    incident_type: str
    severity: int
    trapped_status: str

# llm = init_chat_model("gemini-2.5-flash", temperature=0.2)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
emergency_structured_llm = llm.with_structured_output(EmergencyResponse)

def triage_node(state: EmergencyAnalysis) -> EmergencyAnalysis:
    prompt = f"""
    Analyze the following emergency message from a hotel guest. 
    Extract:
    1. Incident Type should be strictly one of: (Fire, Medical, Security, Maintenance)
    2. Severity should be strictly one of: (1-10)
    3. Trapped Status should be strictly one of: (Yes/No)

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

def guest_help_node(state: GuestState) -> GuestState:
    context = get_protocol_context(state.get("incident_type", "General"))
    system_msg = f"""
    Analyze the following messages from a hotel guest.
    Understand the guest's current situation and needs, and 
    provide practical and helpful advice on how the hotel protocols work
    and what the guest should do next.
    Protocols: "{context}"
    """
    prompt_template = SystemMessage(system_msg) + state["messages"]
    prompt_template = dict(prompt_template)
    prompt = prompt_template["messages"]
    response = llm.invoke(prompt)
    return {
        "messages": [response], 
        "session_summary": "", 
        "incident_type": state.get("incident_type", "General")
    }

guest_graph = StateGraph(GuestState)
guest_graph.add_node("help", guest_help_node)
guest_graph.set_entry_point("help")
guest_graph.add_edge("help", END)
guest_app = guest_graph.compile()

workflow = StateGraph(EmergencyAnalysis)
workflow.add_node("triage", triage_node)
workflow.set_entry_point("triage")
workflow.add_edge("triage", END)

app = workflow.compile()
