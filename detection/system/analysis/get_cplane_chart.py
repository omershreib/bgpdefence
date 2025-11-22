from detection.system.charts.aspath_charts_maker import make_edges, get_aspath_chart_fig, AS_RELATIONSHIPS
from detection.system.analysis import parse_bgp
from ipaddress import IPv4Address
import matplotlib
import pandas as pd
matplotlib.use('Agg')


# def assign_level(nodes, as_relationships):
#     levels = {}
#     current_level = 0
#     prev_node = None
#
#     for node in nodes:
#         if not prev_node:
#             prev_node = node
#             levels[node] = current_level
#             continue
#
#         if node in as_relationships[prev_node]['customers']:
#             current_level -= 1
#             levels[node] = current_level
#             prev_node = node
#             continue
#
#         if node in as_relationships[prev_node]['providers']:
#             current_level += 1
#             levels[node] = current_level
#             prev_node = node
#             continue
#
#         prev_node = node
#         levels[node] = current_level
#         continue
#
#     return levels
#
#
# def get_cplane_chart_deprecated(as_relationships):
#     # valid input
#     nodes = [100, 200, 300, 400, 500]
#     edges = [(100, 200), (200, 300), (300, 400), (400, 500)]
#
#     # as_relationships = {
#     #     100: {'customers': [], 'providers': [200]},
#     #     200: {'customers': [100], 'providers': [], 'others': [300]},
#     #     300: {'customers': [200, 400, 500], 'providers': [], 'others': [300]},
#     #     400: {'customers': [500], 'providers': [300]},
#     #     500: {'customers': [], 'providers': [400]}
#     # }
#
#     # build graph
#     G = nx.DiGraph()
#     G.add_nodes_from(nodes)
#     G.add_edges_from(edges)
#
#     levels = assign_level(nodes, as_relationships)
#
#     # Build positions: spread on x, y = level
#     pos = {}
#     for i, n in enumerate(nodes):
#         pos[n] = (i, levels[n])
#
#     edge_colors, edge_styles, edge_labels, error_nodes = asn_path_graphic_analysis(G, as_relationships)
#
#     node_colors = []
#     for n in G.nodes():
#         if n in error_nodes:
#             node_colors.append('red')
#         if n not in error_nodes:
#             node_colors.append('lightgray')
#
#     fig = plt.figure()
#
#     # draw graph
#     nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800)
#     nx.draw_networkx_labels(G, pos)
#     for (u, v), color, style in zip(G.edges(), edge_colors, edge_styles):
#         nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=color, style=style, arrows=True)
#     nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black')
#
#     # working...
#     #fig = Figure()
#
#     #fig.set_facecolor("#00000F")
#     fig.patch.set_facecolor('#343a40')
#
#
#     #set_facecolor('deepskyblue')
#     plt.axis('off')
#     plt.tight_layout()
#
#     return fig, None


def get_cplane_chart(prefixes, sensor_asn=100):

    raw_as_path = [sensor_asn]

    bgp_file = r"D:\Documents\open university\netSeminar\source\detection\system\sensor\bgp_table.txt"
    bgp_routes = parse_bgp.bgp_table_to_dict(bgp_file)

    #print(bgp_routes)

    df = pd.DataFrame(bgp_routes)
    df["network_obj"] = df["network"].apply(parse_bgp.normalize_network)
    print(df)

    query_ip = IPv4Address("198.18.1.13")
    matches_ip = df[df["network_obj"].apply(lambda net: query_ip in net)]

    if not matches_ip.empty:
        raw_as_path.extend([int(asn) for asn in matches_ip['path'].to_list()[0]])
        print(raw_as_path)

    egdes = make_edges(raw_as_path)

    fig = get_aspath_chart_fig("Control Plane AS-Path",raw_as_path, egdes, AS_RELATIONSHIPS)
    return fig, raw_as_path


if __name__ == '__main__':
    import pandas as pd
    prefix2as_csv = r"D:\Documents\open university\netSeminar\source\detection\detection_tools\prefix2as.csv"
    my_prefixes = pd.read_csv(prefix2as_csv)

    fig = get_cplane_chart(my_prefixes)
