import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import time
import requests
import pandas as pd

from config import HEADERS, API_URL, DATA_DIR

#Archivos y constantes para el proyecto
RAW_PAPER_FILE = os.path.join(DATA_DIR, "raw_papers.csv")
PROCESSED_PAPER_FILE = os.path.join(DATA_DIR, "processed_papers.csv")
AUTHORS_FILE = os.path.join(DATA_DIR, "authors.csv")

#Palabras clave para búsqueda de artículos dentro de la API
QUERIES = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural networks"
]

def create_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

# Función para consultar la API de Semantic Scholar con una consulta específica y un límite de resultados. 
def fetch_papers(query, limit=15):
    params = {
        "query": query,
        "limit": limit,
        "fields": "paperId,title,year,authors"
    }
    try: 
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
        print(f"Consulta: {query} - Estatus: {response.status_code}")
        print (f"Respuesta: {response.status_code}")  
        #El número de respuesta 200 es una consulta exitosa
        if response.status_code ==200:
            return response.json().get("data", [])
        #El número de respuesta 429 notifica que se ha llegado al límite de requests
        if response.status_code == 429:
            print("Límite de tasa alcanzado. Esperando 60 segundos...")
            time.sleep(60)
            return fetch_papers(query, limit)
    except requests.exceptions.RequestException as e:
        print(f"Error al consultar la API: {e}")
    return []

#Formato de artículos guardados sin aplicar ningún filtro
def save_raw_data():
    all_papers = []
    for query in QUERIES:
        papers = fetch_papers(query,limit=15)
        for paper in papers:
            paper["query_used"] = query
            all_papers.append(paper)
        print(f"Artículos obtenidos: {len(papers)}")
        print("="*40)
        time.sleep(1)  # Para evitar exceder el límite de tasa
    
    return all_papers

#Aplicación de filtros para almacenar únicamente la información relevante:
#- Identificación del artículo (paperId)
#- Título del artículo (title)
#- Año de publicación (year)
#- Lista de autores (authors)

def clean_data(papers):
    cleaned = []
    for paper in papers:
        paper_id = paper.get("paperId")
        title = paper.get("title")
        year = paper.get("year")
        authors = paper.get("authors", [])
        
        if not paper_id or not title or not year:
            print(f"Artículo ignorado (datos faltantes): {paper}")
            continue
        if not isinstance(authors, list) or len(authors) < 2:
            print(f"Artículo ignorado (autores insuficientes): {title}")
            continue
        cleaned.append({
            "paperId": paper_id,
            "title": title,
            "year": year,
            "authors": authors
        })   
    df_clean = pd.DataFrame(cleaned)
    if not df_clean.empty:
         df_clean = df_clean.drop_duplicates(subset=["paperId"])
    return df_clean


#De los artículos obtenidos, se filtran los autores con sus posteriores campos de identificación
def extract_authors(papers):
    authors = []
    for _, paper in papers.iterrows():
        for author in paper["authors"]:
            author_id = author.get("authorId")
            name = author.get("name")
            if author_id and name:
                authors.append({"authorId": author_id, "name": name})
    df_authors = pd.DataFrame(authors)
    if not df_authors.empty:
        df_authors = df_authors.drop_duplicates(subset=["authorId"])
    # Limitar el número de autores guardados para evitar conjuntos demasiado grandes
    if not df_authors.empty:
        df_authors = df_authors
    return df_authors
 
#Función principal que ejecuta todo el proceso de recolección, limpieza y extracción de datos, además de guardar los resultados en archivos CSV para su posterior análisis. Se incluyen mensajes de impresión para monitorear el progreso y la cantidad de datos obtenidos en cada etapa.
def run_collection():
    create_data_dir()
    raw_papers = save_raw_data()
    df_raw = pd.DataFrame(raw_papers)
    df_raw.to_csv(RAW_PAPER_FILE, index=False, encoding="utf-8-sig")
    df_cleaned = clean_data (raw_papers)
    df_cleaned.to_csv(PROCESSED_PAPER_FILE, index=False, encoding="utf-8-sig")
    print (f"Articulos limpios obtenidos: {len(df_cleaned)}")
    df_authors = extract_authors(df_cleaned)
    df_authors.to_csv(AUTHORS_FILE, index=False, encoding="utf-8-sig")
    print (f"Autores extraidos: {len(df_authors)}")
    print("Recoleccion terminada")

#Función principal que ejecuta el proceso de recolección de datos al ejecutar el script.
def main():
    run_collection()

if __name__ == "__main__":
    print("Script iniciado")
    main()



    