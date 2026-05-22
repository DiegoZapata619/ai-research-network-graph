import os
from dotenv import load_dotenv

# Buscar archivo .env en la raíz del proyecto
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(root, ".env")
load_dotenv(dotenv_path)

SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

if not SEMANTIC_SCHOLAR_API_KEY:
    raise ValueError(
        "La clave de API de Semantic Scholar no está configurada. "
        "Por favor, establece SEMANTIC_SCHOLAR_API_KEY en tu entorno "
        "o en un archivo .env en la raíz del proyecto."
    )

# Encabezados para la API
HEADERS = {"x-api-key": SEMANTIC_SCHOLAR_API_KEY}

API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

DATA_DIR = "data"