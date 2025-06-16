from urllib.parse import urlparse
from src.config.settings import PRESET_SITES

def display_header():
    """
    Muestra el encabezado de la aplicación.
    """
    print("=" * 70)
    print("Agente Avanzado de Clonación Web - Herramienta Educativa")
    print("ADVERTENCIA: Para fines exclusivamente educativos y de concientización.")
    print("=" * 70)

def get_user_choice() -> str:
    """
    Muestra el menú de opciones y captura la selección del usuario.
    """
    print("\nSitios Preconfigurados:")
    for key, site in PRESET_SITES.items():
        print(f"  {key}. {site['name']} ({site['query']})")
    print("  9. Sitio Personalizado")
    
    choice = input("\nSeleccione una opción (1-9): ").strip()
    
    if choice in PRESET_SITES:
        target_query = PRESET_SITES[choice]["query"]
        print(f"\n[INFO] Opción seleccionada: {PRESET_SITES[choice]['name']}")
    elif choice == "9":
        target_query = input("Ingrese el nombre o dominio del sitio personalizado: ").strip()
    else:
        target_query = PRESET_SITES["1"]["query"]
        print("\n[WARN] Opción no válida. Se utilizará el valor por defecto: Interbank.")
        
    if not target_query:
        print("[ERROR] No se ha ingresado un sitio válido. Abortando ejecución.")
        return None
        
    return target_query

def display_results(final_state: dict, duration: float):
    """
    Formatea y muestra el informe final de resultados.
    """
    print("\n" + "=" * 20 + " INFORME DE EJECUCIÓN " + "=" * 20)
    print(f"Duración Total: {duration:.2f} segundos")
    
    url = final_state.get('url', 'No disponible')
    print(f"URL Procesada: {url}")
    
    analysis = final_state.get('site_analysis')
    if analysis:
        print("\n--- Resultados del Análisis ---")
        print(f"  Título: {analysis.get('title', 'N/A')[:60]}")
        print(f"  Conteo de Formularios: {analysis.get('form_count', 0)}")
        colors = analysis.get('css_styles', {}).get('colors', [])
        if colors:
            print(f"  Colores Detectados: {', '.join(colors[:3])}")
    
    print("\n--- Estado de la Generación de Archivos ---")
    clone_msg = final_state.get('clone_confirmation', 'No ejecutado.')
    phishing_msg = final_state.get('phishing_confirmation', 'No ejecutado.')
    print(f"  - Clon Estático: {clone_msg}")
    print(f"  - Simulación Phishing: {phishing_msg}")

    if url != 'No disponible':
        print("\n--- Archivos Generados ---")
        host = urlparse(url).netloc.replace('.', '_').replace(':', '_')
        print(f"  - {host}_enhanced_clone.html")
        print(f"  - {host}_phishing_demo.html")
    
    print("=" * 62)

def display_error(exception: Exception):
    """
    Muestra un mensaje de error formateado en caso de una falla inesperada.
    """
    print(f"\n[FATAL] Ha ocurrido un error crítico durante la ejecución: {exception}")
    print("\nPosibles Causas y Soluciones:")
    print("  - Verifique la validez de las claves API en el archivo .env.")
    print("  - Asegure una conexión a internet estable.")
    print("  - El sitio objetivo puede tener protecciones avanzadas anti-bot.")
    print("  - Intente con otro sitio de la lista preconfigurada.")