import os
import pickle
import pandas as pd
import networkx as nx

DATA_DIR = "data"
OUTPUT_DIR = "output"
AUTHORS_FILE = os.path.join(DATA_DIR, "authors.csv")
EDGES_FILE = os.path.join(DATA_DIR, "edges.csv")
GRAPH_FILE = os.path.join(OUTPUT_DIR, "research_graph.gpickle")

def create_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_graph():
    df_authors = pd.read_csv(AUTHORS_FILE)
    df_edges = pd.read_csv(EDGES_FILE)
    G = nx.Graph()
    # Agregar nodos de autores al grafo
    for _, row in df_authors.iterrows():
        author_id = row["authorId"]
        name = row["name"]
        G.add_node(str(row["authorId"]), name=row["name"]) 
    # Agregar aristas de colaboración al grafo
    for _, row in df_edges.iterrows():
        source = str(row["source"])
        target = str(row["target"])
        weight = int(row["weight"])
        source_name = row["source_name"]
        target_name = row["target_name"]
        G.add_edge(source, target, weight=weight, source_name=source_name,
                    target_name=target_name)
    return G
    
def save_graph(graph):
    create_output_dir()
    with open(GRAPH_FILE, "wb") as f:
        #picke.dump serializa un objeto y lo guarda en un archivo
        #usa la extensión .gpickle que networkx utiliza para guardar grafos 
        pickle.dump(graph, f)

def main():
    graph = build_graph()
    save_graph(graph)
    print(f"Grafo guardado en {GRAPH_FILE}")

if __name__ == "__main__":
    main()