import os
import pickle
from matplotlib import cm
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from networkx.algorithms.community import greedy_modularity_communities

OUTPUT_DIR = "output"
FIGURES_DIR = "figures"
GRAPH_FILE = os.path.join(OUTPUT_DIR, "research_graph.gpickle")
CENTRALITY_FILE = os.path.join(OUTPUT_DIR, "centrality.csv")
COMPONENTS_FILE = os.path.join(OUTPUT_DIR, "components.csv")
ISOLATED_AUTHORS_FILE = os.path.join(OUTPUT_DIR, "isolated_authors.csv")
COMMUNITIES_FILE = os.path.join(OUTPUT_DIR, "communities.csv")
FULL_GRAPH_IMAGE = os.path.join(FIGURES_DIR, "full_graph.png")
IMPORTANT_NODES_IMAGE = os.path.join(FIGURES_DIR, "important_nodes.png")
GEXF_FILE = os.path.join(OUTPUT_DIR, "research_graph.gexf")
GEXF_IMPORTANT_NODES_FILE = os.path.join(OUTPUT_DIR, "important_nodes.gexf")

def load_graph():
    with open(GRAPH_FILE, "rb") as file:
        G = pickle.load(file)
    return G

def get_author_name(G,node_id):
    return G.nodes[node_id].get("name", "No disponible")

def analyze_graph(G):
    print("Informacion general del grafo")
    print(f"Número de nodos: {G.number_of_nodes()}")
    print(f"Número de aristas: {G.number_of_edges()}")
    print(f"Densidad del grafo: {nx.density(G):.4f}")
    isolated_authors = list(nx.isolates(G))
    print(f"Número de autores aislados: {len(isolated_authors)}")
    print(f"Autores aislados: {[get_author_name(G, author) for author in isolated_authors]}")
    components = list(nx.connected_components(G))
    print(f"Número de componentes conectados: {len(components)}")
    print(f"Tamaño de la componente más grande: {len(max(components, key=len))}")
    print(f"Autores en la componente más grande: {[get_author_name(G, author) for author in max(components, key=len)]}")


def analyze_centrality (G):
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    results = []
    for node in G.nodes ():
            results.append ({
                "authorId": node,
                "name": get_author_name(G, node),
                "degree": G.degree(node),
                "degree_centrality": degree_centrality[node],
                "betweenness_centrality": betweenness_centrality[node],
                "closeness_centrality": closeness_centrality[node]
            })

    df_centrality = pd.DataFrame(results)
    df_centrality = df_centrality.sort_values(by="degree_centrality", ascending=False)
    df_centrality.to_csv(CENTRALITY_FILE, index=False, encoding="utf-8-sig")
    return df_centrality
    
def analyze_components(G):
    components = list(nx.connected_components(G))
    results = []
    for i, component in enumerate(components, start=1):
        for node in component:
            results.append({
                "authorId": node,
                "name": get_author_name(G, node),
                "component": i,
                "component_size": len(component)
            })
    df_components = pd.DataFrame(results)
    df_components.to_csv(COMPONENTS_FILE, index=False, encoding="utf-8-sig")
    #funcion isolates de nx para identificar nodos sin conexiones
    isolated_nodes = list(nx.isolates(G))
    isolated_rows = []

    for node in isolated_nodes:
        isolated_rows.append({
            "authorId": node,
            "name": get_author_name(G, node)
        })
    df_isolated = pd.DataFrame(isolated_rows)
    df_isolated.to_csv(ISOLATED_AUTHORS_FILE, index=False, encoding="utf-8-sig")
    component_sizes = sorted ([len(c) for c in components], reverse=True)
    print(f"Tamaño de las componentes conectadas: {component_sizes}")

#Función para obtener el camino más corto entre dos nodos específicos
def analyze_shortest_path(G, source, target):
    try:
        shortest_path = nx.shortest_path(G, source=source, target=target)
        path_length = nx.shortest_path_length(G,source=source, target=target)
        print (f"Camino más corto entre {get_author_name(G, source)} y {get_author_name(G, target)}: {shortest_path} (longitud: {path_length})")
        print ("Ruta")
        for node in shortest_path:
            print(f"- {get_author_name(G, node)} (ID: {node}) ->")
    
    except nx.NetworkXNoPath:
        print (f"No hay camino entre {get_author_name(G, source)} y {get_author_name(G, target)}."
               "Intenta con otros nodos.")
        

#Función para analizar los caminos más cortos dentro de la componente más grande del grafo
def analyze_shortest_paths(G):
    components = list(nx.connected_components(G))
    if not components:
        print("El grafo no tiene componentes conectados.")
        return pd.DataFrame()
    #Obtenemos el componente más grande del grafo
    largest_component = max(components, key=len)
    subgraph = G.subgraph(largest_component)
    print (f"Componente más grande: {len(largest_component)} nodos")
    #Para estas pruebas, se seleccionan los 5 autores más importantes de la componente más grande utilizando betweennes_centrality
    selected_authors  = nx.betweenness_centrality(subgraph, weight="distance")
    #Se ordenan los autores por su centralidad y se seleccionan los 5 con mayor valor
    #El slicing [:5] se utiliza para obtener solo los 5 autores más importantes
    top5 = sorted(selected_authors, key=selected_authors.get, reverse=True)[:5]
    print ("Camino mínimo entre los nodos más importantes de la componente más grande")
    for i in range(len(top5)):
            for j in range(i + 1, len(top5)):
                source = top5[i]
                target = top5[j]
                try:
                    #Calculamos los caminos más cortos, la distancia de cada camino y los nombres para mejorar el formato de impresión y no usar sus ID
                    shortest_path = nx.shortest_path(subgraph, source=source, target=target,weight="distance")
                    path_length = nx.shortest_path_length(subgraph, source=source, target=target, weight="distance")
                    path_names = [get_author_name(G, node) for node in shortest_path]
                    print(f"Camino más corto entre {get_author_name(G, source)} y {get_author_name(G, target)}")
                    print(f"Distancia ponderada: {path_length:.4f}")
                    print(f"Pasos: {len(shortest_path) - 1}")
                    print("Ruta: " + " → ".join(path_names) + "\n")
                except nx.NetworkXNoPath:
                    print(f"No hay camino entre {get_author_name(G, source)} y {get_author_name(G, target)} en la componente más grande.")

def analyze_communities(G):
    if G.number_of_edges() == 0:
        print("El grafo no tiene aristas, no se pueden detectar comunidades.")
        return pd.DataFrame()
    largest_component = max(nx.connected_components(G), key=len)
    G_main = G.subgraph(largest_component).copy()
    communities = list(greedy_modularity_communities(G_main, weight="weight"))
    results = [
        {
            "community_id": i,
            "authorId": node,
            "name": get_author_name(G, node),
            "community_size": len(community)
        }
        for i, community in enumerate(communities, start=1)
        for node in community
    ]
    df_communities = pd.DataFrame(results).sort_values(by="community_size", ascending=False)
    df_communities.to_csv(COMMUNITIES_FILE, index=False, encoding="utf-8-sig")
    print(f"Número de comunidades detectadas: {len(communities)}")
    print(f"Tamaño de las comunidades: {[len(c) for c in communities]}")
    return df_communities
   

def export_gexf(G, filepath):
    G_export = G.copy()
    for u,v, data in G_export.edges(data=True):
        data.pop("source_name", None)
        data.pop("target_name", None)
    nx.write_gexf(G_export, filepath)
    
def visualize_graph(G):
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, seed=42)
    node_sizes = [
        80 + (G.degree(node)*20)
        for node in G.nodes()
    ]

    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_sizes,
        alpha=0.8,
        node_color="skyblue"
    )

    nx.draw_networkx_edges(
        G,
        pos,
        alpha=0.5,
        edge_color="gray"
    )
    plt.title("Grafo de colaboración entre autores")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(FULL_GRAPH_IMAGE, format="PNG")
    plt.close()
    
def visualize_important_nodes(G, df_centrality, top_n=20):
    top_degree = set (df_centrality.nlargest(top_n, "degree_centrality")["authorId"])
    top_betweenness = set (df_centrality.nlargest(top_n, "betweenness_centrality")["authorId"])
    top_closeness = set (df_centrality.nlargest(top_n, "closeness_centrality")["authorId"]) 
    important_nodes = top_degree|top_betweenness|top_closeness
    
    subgraph= G.subgraph(important_nodes).copy()
    degree_centrality = nx.degree_centrality(subgraph)
    node_sizes = [300 + (degree_centrality[node]*300) for node in subgraph.nodes()]

    betweenness_centrality = nx.betweenness_centrality(subgraph,weight="weight")
    betweeness_values = [betweenness_centrality[node] for node in subgraph.nodes()]
    norm = mcolors.Normalize(vmin=min(betweeness_values), vmax=max(betweeness_values))
    node_colors = [cm.plasma(norm(v)) for v in betweeness_values]
    fig, ax = plt.subplots(figsize=(14, 14))
    pos= nx.spring_layout(subgraph, seed=42)
    nx.draw_networkx_nodes(
        subgraph,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        alpha=0.9,
        ax=ax
    )
    nx.draw_networkx_edges(
        subgraph,
        pos,
        alpha=0.7,
        edge_color="gray",
        ax=ax
    )
    labels = {node: get_author_name(G, node) for node in subgraph.nodes()}
    nx.draw_networkx_labels(subgraph, pos, labels, font_size=8)

    #Leyenda personalizada
    sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label="Betweenness Centrality")
    ax.set_title(f"Autores más importantes (Top {top_n} en centralidad)")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(IMPORTANT_NODES_IMAGE, format="PNG",dpi=200)
    plt.close()
    export_gexf(subgraph, GEXF_IMPORTANT_NODES_FILE)
    return subgraph

def main():
    G = load_graph()
    analyze_graph(G)
    df_centrality = analyze_centrality(G)
    analyze_components(G)
    analyze_shortest_paths(G)
    analyze_communities(G)
    visualize_graph(G)
    visualize_important_nodes(G, df_centrality)
    export_gexf(G, GEXF_FILE)
    

if __name__ == "__main__":
    main()
