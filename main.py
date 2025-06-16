import time
from src.core.workflow import create_workflow
from src.ui.console import display_header, get_user_choice, display_results, display_error
from src.config.settings import SERPER_API_KEY, OPENAI_API_KEY

def main():
    """
    Punto de entrada principal de la aplicación.
    """
    display_header()
    
    if not SERPER_API_KEY or not OPENAI_API_KEY:
        print("[ERROR] Las claves API (SERPER_API_KEY, OPENAI_API_KEY) no están configuradas en el archivo .env.")
        return
        
    target_query = get_user_choice()
    if not target_query:
        return
        
    print("\n[INFO] Iniciando proceso de clonación y análisis...")
    print("-" * 50)
    
    try:
        app = create_workflow()
        initial_state = {"search_query": target_query}
        
        start_time = time.time()
        final_state = app.invoke(initial_state)
        end_time = time.time()
        
        display_results(final_state, end_time - start_time)
        
    except KeyboardInterrupt:
        print("\n[INFO] Proceso interrumpido por el usuario.")
    except Exception as e:
        display_error(e)

if __name__ == "__main__":
    main()