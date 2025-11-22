from detection.system.analysis.asn_path_graphic_analysis import asn_path_graphic_analysis
from detection.detection_tools.as_relationships import get_as_relationships
from pprint import pprint
import networkx as nx
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

AS_RELATIONSHIPS = get_as_relationships()


def make_edges(nodes):
    edges = []

    for i in range(len(nodes) - 1):
        u = nodes[i]
        v = nodes[i + 1]
        edge = (u, v)
        edges.append(edge)

    return edges


def assign_level(nodes, as_relationships):
    levels = {}
    current_level = 0
    prev_node = None

    for node in nodes:
        if not prev_node:
            prev_node = node
            levels[node] = current_level
            continue

        if node in as_relationships[prev_node]['customers']:
            current_level -= 1
            levels[node] = current_level
            prev_node = node
            continue

        if node in as_relationships[prev_node]['providers']:
            current_level += 1
            levels[node] = current_level
            prev_node = node
            continue

        prev_node = node
        levels[node] = current_level
        continue

    return levels


def get_aspath_chart_fig(title, nodes, edges, as_relationships):
    # build graph
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    levels = assign_level(nodes, as_relationships)

    pprint(levels)

    # Build positions: spread on x, y = level
    pos = {}
    for i, n in enumerate(nodes):
        pos[n] = (i, levels[n])

    edge_colors, edge_styles, edge_labels, error_nodes = asn_path_graphic_analysis(G, as_relationships)

    node_colors = []
    for n in G.nodes():
        if n in error_nodes:
            node_colors.append('red')
        if n not in error_nodes:
            node_colors.append('lightgray')

    plt.style.use('dark_background')
    fig = plt.figure()

    # draw graph
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800)
    nx.draw_networkx_labels(G, pos)
    for (u, v), color, style in zip(G.edges(), edge_colors, edge_styles):
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=color, style=style, arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black')

    plt.axis('off')
    plt.tight_layout()
    plt.title(title)

    return fig


if __name__ == '__main__':
    from pprint import pprint

    # valid route
    # nodes = [100, 200, 300, 400]

    # invalid (valley free) route
    nodes = [100, 200, 666, 300, 400]

    edges = make_edges(nodes)
    as_relationships = get_as_relationships()

    # pprint(as_relationships)

    fig = get_aspath_chart_fig(nodes, edges, as_relationships)
    filename = f"test_valley_free_chart.png"
    # filepath = os.path.join(STATIC_DIR, filename)
    fig.tight_layout()
    plt.savefig(filename, format="png", dpi=120)
    plt.close(fig)
