import base64
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def download_and_encode_image(img_url: str, base_url: str) -> str:
    """
    Descarga una imagen y la codifica en formato Base64.
    """
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

def absolutize_and_inline_resources(html: str, base_url: str) -> str:
    """
    Convierte URLs relativas a absolutas e incrusta recursos críticos.
    """
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