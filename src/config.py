import os
from dotenv import load_dotenv

# Preferir variables de entorno; si no existen, buscar un archivo `api_key.env` en
# la raíz del proyecto (fuera de `src/`) que está ignorado por git.
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path)

SEMANTIC_SCOLAR_API_KEY = os.getenv("SEMANTIC_SCOLAR_API_KEY")

if not SEMANTIC_SCOLAR_API_KEY:
    raise ValueError("La clave de API de Semantic Scholar no está configurada. Por favor, establece SEMANTIC_SCOLAR_API_KEY en tu entorno o en api_key.env en la raíz del proyecto.")

HEADERS = {"x-api-key": SEMANTIC_SCOLAR_API_KEY}

# Limitar número de autores extraídos (por defecto 200)
MAX_AUTHORS = 200

API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
DATA_DIR = "data"
