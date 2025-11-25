from detection.system.analysis.asn_path_graphic_analysis import asn_path_graphic_analysis2
from detection.detection_tools.as_relationships import get_as_relationships
from detection.system.charts.aspath_charts_maker import make_edges
import unittest
import networkx as nx

AS_RELATIONSHIPS = get_as_relationships()


class TestAsnPathGraphicAnalysis(unittest.TestCase):

    def test_asn_path_graphic_analysis(self):
        # input G, as_relationships
        nodes = [100, 200, 300, 400]
        edges = make_edges(nodes)

        # utilities

        #print(edges)

        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        expected_edge_colors = ['green', 'blue', 'green']
        expected_edge_styles = ['solid', 'solid', 'solid']
        expected_edge_tors = {(100, 200): 'C2P',
                              (200, 300): 'P2P',
                              (300, 400): 'P2C'}

        expected_error_nodes = []

        edge_colors, edge_styles, edge_tors, error_nodes = asn_path_graphic_analysis2(G, AS_RELATIONSHIPS)

        self.assertEqual(expected_edge_colors, edge_colors)
        self.assertEqual(expected_edge_styles, edge_styles)
        self.assertEqual(expected_edge_tors, edge_tors)
        self.assertEqual(expected_error_nodes, error_nodes)
