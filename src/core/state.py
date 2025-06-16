from typing import TypedDict

class GraphState(TypedDict):
    """
    Define el estado compartido a través del grafo de agentes.
    """
    search_query: str
    url: str
    site_analysis: dict
    cloned_html: str
    phishing_form: str
    clone_confirmation: str
    phishing_confirmation: str