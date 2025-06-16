import re
from typing import Dict
from bs4 import BeautifulSoup

def extract_css_styles(soup: BeautifulSoup) -> Dict:
    """
    Extrae estilos CSS (colores, fuentes) del objeto BeautifulSoup.
    """
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
    """
    Analiza elementos de marca como logos y nombres desde el objeto BeautifulSoup.
    """
    brand_info = {"logo_urls": [], "brand_name": "", "button_styles": []}
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