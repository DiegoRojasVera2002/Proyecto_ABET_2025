from langgraph.graph import StateGraph, END
from src.core.state import GraphState
from src.agents.search_agent import search_node
from src.agents.analysis_agent import analysis_node
from src.agents.clone_agent import clone_node
from src.agents.phishing_agent import phishing_node

def create_workflow():
    """
    Construye y compila el grafo de ejecución de agentes.
    """
    workflow = StateGraph(GraphState)
    
    workflow.add_node("SearchAgent", search_node)
    workflow.add_node("AnalysisAgent", analysis_node)
    workflow.add_node("CloneAgent", clone_node)
    workflow.add_node("PhishingAgent", phishing_node)
    
    workflow.set_entry_point("SearchAgent")
    workflow.add_edge("SearchAgent", "AnalysisAgent")
    workflow.add_edge("AnalysisAgent", "CloneAgent")
    workflow.add_edge("CloneAgent", "PhishingAgent")
    workflow.add_edge("PhishingAgent", END)
    
    return workflow.compile()