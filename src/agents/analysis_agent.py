from typing import Dict
from bs4 import BeautifulSoup

from src.core.state import GraphState
from src.utils.browser import setup_driver, smart_page_analysis
from src.utils.analysis import extract_css_styles, analyze_brand_elements

def analysis_node(state: GraphState) -> Dict:
    """
    Nodo del grafo que analiza la estructura y contenido del sitio web.
    """
    print("\n[FASE 2/4] Ejecutando Agente de Análisis...")
    url = state["url"]
    if not url:
        print("[WARN] No hay URL para analizar. Omitiendo fase.")
        return {"site_analysis": {}, "cloned_html": ""}
    
    driver = setup_driver(headless=True, stealth=True)
    try:
        print(f"[INFO] Realizando análisis en: {url}")
        raw_html = smart_page_analysis(driver, url)
    finally:
        driver.quit()
    
    soup = BeautifulSoup(raw_html, "html.parser")
    css_styles = extract_css_styles(soup)
    brand_elements = analyze_brand_elements(soup)
    
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_desc_tag.get('content', '') if meta_desc_tag else ""
    
    analysis = {
        "url": url,
        "title": soup.find('title').string if soup.find('title') else "",
        "css_styles": css_styles,
        "brand_elements": brand_elements,
        "form_count": len(soup.find_all('form')),
        "meta_description": meta_description,
    }
    
    print("[SUCCESS] Análisis de sitio completado.")
    return {"site_analysis": analysis, "cloned_html": raw_html}