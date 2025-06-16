from typing import Dict
from urllib.parse import urlparse

from src.core.state import GraphState
from src.utils.resources import absolutize_and_inline_resources

def clone_node(state: GraphState) -> Dict:
    """
    Nodo del grafo responsable de clonar el sitio web.
    """
    print("\n[FASE 3/4] Ejecutando Agente de Clonación...")
    url = state["url"]
    raw_html = state["cloned_html"]
    
    if not url or not raw_html:
        message = "[WARN] No hay contenido HTML para clonar. Omitiendo fase."
        print(message)
        return {"clone_confirmation": message}
    
    enhanced_html = absolutize_and_inline_resources(raw_html, url)
    host = urlparse(url).netloc.replace('.', '_').replace(':', '_')
    filename = f"{host}_enhanced_clone.html"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(enhanced_html)
        
        message = f"Clon estático del sitio guardado como '{filename}'."
        print(f"[SUCCESS] {message}")
        return {"clone_confirmation": message, "cloned_html": enhanced_html}
    except Exception as e:
        message = f"Error al guardar el archivo clonado: {e}"
        print(f"[ERROR] {message}")
        return {"clone_confirmation": message}