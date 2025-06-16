import json
import requests
from typing import Dict

from src.core.state import GraphState
from src.config.settings import SERPER_API_KEY

def serper_first_url(query: str) -> str:
    """
    Obtiene la URL más relevante desde Serper API para una consulta dada.
    """
    try:
        payload = json.dumps({"q": query, "num": 5})
        headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
        response = requests.post("https://google.serper.dev/search", headers=headers, data=payload)
        response.raise_for_status()
        organic = response.json().get("organic", [])
        
        for result in organic:
            url = result.get("link", "")
            if url and not any(sub in url for sub in ["blog", "help", "support", "news", "careers"]):
                return url
        
        return organic[0]["link"] if organic else ""
    except Exception as e:
        print(f"[ERROR] Falló la consulta a Serper API: {e}")
        return ""

def search_node(state: GraphState) -> Dict:
    """
    Nodo del grafo que ejecuta la búsqueda de la URL objetivo.
    """
    print("\n[FASE 1/4] Ejecutando Agente de Búsqueda...")
    query = state["search_query"]
    print(f"[INFO] Identificando URL para la consulta: '{query}'")
    
    try:
        url = serper_first_url(query)
        if url:
            print(f"[SUCCESS] URL de destino identificada: {url}")
        else:
            print("[WARN] No se encontró una URL de destino.")
        return {"url": url}
    except Exception as e:
        print(f"[ERROR] El nodo de búsqueda falló: {e}")
        return {"url": ""}