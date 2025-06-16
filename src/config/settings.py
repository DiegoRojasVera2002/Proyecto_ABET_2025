import os
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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