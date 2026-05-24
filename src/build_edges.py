import os
import ast
import pandas as pd
from itertools import combinations
from collections import defaultdict


DATA_DIR = "data"
PROCESSED_PAPER_FILE = os.path.join(DATA_DIR, "processed_papers.csv")
AUTHORS_FILE = os.path.join(DATA_DIR, "authors.csv")
EDGES_FILE = os.path.join(DATA_DIR, "edges.csv")


def parse_authors(authors_text):
    try:
        #authors crea un diccionario con ast, que convierte la cadena en una estructura de datos de Python
        authors = ast.literal_eval(authors_text)
        #ifinstance verifica si authors es una lista, lo que es esperado. Si es así, se devuelve la lista de autores. 
        #caso contrario, devuelve una lista vacía
        if isinstance(authors, list):
            return authors
    except Exception:
        return []

    return []


def build_edges():
    df_papers = pd.read_csv(PROCESSED_PAPER_FILE)
    df_authors = pd.read_csv(AUTHORS_FILE)

    # Autores permitidos: son los autores oficiales del grafo.
    allowed_authors = set(df_authors["authorId"].astype(str))

    edge_weights = defaultdict(int)
    edge_names = {}

    for _, paper in df_papers.iterrows():
        authors = parse_authors(paper["authors"])

        clean_authors = []

        for author in authors:
            author_id = author.get("authorId")
            name = author.get("name")

            if author_id and name:
                author_id = str(author_id)

                # Solo se conservan autores que estén dentro del subconjunto oficial.
                if author_id in allowed_authors:
                    clean_authors.append((author_id, name))

        # Si dentro del artículo hay menos de 2 autores del subconjunto oficial,
        # no se puede crear una arista.
        if len(clean_authors) < 2:
            continue

        # Crear colaboraciones reales entre pares de autores del mismo artículo.
        for author1, author2 in combinations(clean_authors, 2):
            id1, name1 = author1
            id2, name2 = author2

            source, target = sorted([id1, id2])

            if source == id1:
                source_name = name1
                target_name = name2
            else:
                source_name = name2
                target_name = name1

            edge = (source, target)

            edge_weights[edge] += 1
            edge_names[edge] = (source_name, target_name)

    edges = []

    for (source, target), weight in edge_weights.items():
        source_name, target_name = edge_names[(source, target)]

        edges.append({
            "source": source,
            "target": target,
            "source_name": source_name,
            "target_name": target_name,
            "weight": weight
        })

    df_edges = pd.DataFrame(edges)
    df_edges.to_csv(EDGES_FILE, index=False, encoding="utf-8-sig")

    print("Archivo de aristas creado.")
    print(f"Autores oficiales del grafo: {len(allowed_authors)}")
    print(f"Total de aristas creadas: {len(df_edges)}")


if __name__ == "__main__":
    build_edges()