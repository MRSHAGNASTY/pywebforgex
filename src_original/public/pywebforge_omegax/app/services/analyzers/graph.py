import ast, os, networkx as nx
from typing import Dict, Any, List

def build_dependency_graph(project_path: str) -> Dict[str, Any]:
    G = nx.DiGraph()
    for root, _, files in os.walk(project_path):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                module = os.path.relpath(path, project_path)
                G.add_node(module)
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        tree = ast.parse(fh.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom) and node.module:
                            G.add_edge(module, node.module.replace('.', '/') + ".py")
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                G.add_edge(module, alias.name.replace('.', '/') + ".py")
                except Exception:
                    pass
    nodes = list(G.nodes())
    edges = [{"source": u, "target": v} for u, v in G.edges() if u in nodes and v in nodes]
    return {"nodes": nodes, "edges": edges}
