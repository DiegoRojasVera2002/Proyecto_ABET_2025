import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver(headless: bool = True, stealth: bool = True) -> webdriver.Chrome:
    """
    Configura e inicializa una instancia de Chrome WebDriver.
    """
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
    """
    Detecta el tipo de sitio web para optimizar la extracción de contenido.
    """
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
    """
    Realiza un análisis de página adaptativo basado en el tipo de sitio detectado.
    """
    try:
        driver.get(url)
        time.sleep(3)
        site_type = detect_site_type(driver)
        
        if site_type == "spa":
            print("[INFO] Sitio SPA detectado. Esperando carga de contenido dinámico.")
            time.sleep(8)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
        elif site_type == "heavy":
            print("[INFO] Sitio con alto contenido de scripts detectado. Optimizando carga.")
            time.sleep(6)
            for i in range(3):
                driver.execute_script(f"window.scrollTo(0, {i * 300});")
                time.sleep(1)
        elif site_type == "protected":
            print("[WARN] Sitio con protección detectado. Empleando modo sigiloso.")
            time.sleep(10)
            driver.execute_script("document.body.click();")
            time.sleep(2)
        else:
            time.sleep(4)
            
        driver.implicitly_wait(max_wait)
        return driver.page_source
    except Exception as e:
        print(f"[ERROR] Ocurrió un error durante el análisis de la página: {e}")
        return driver.page_source