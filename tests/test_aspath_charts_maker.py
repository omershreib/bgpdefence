from detection.system.charts.aspath_charts_maker import assign_level, make_edges, get_aspath_chart_fig
from detection.utilities.as_relationships import get_as_relationships
import unittest
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

AS_RELATIONSHIPS = get_as_relationships()


class TestASPathChartsMaker(unittest.TestCase):
    def test_make_edges(self):
        nodes = [100, 200, 300]

        expected_edges = [(100, 200), (200, 300)]
        actual_edges = make_edges(nodes)

        self.assertEqual(expected_edges, actual_edges)

    def test_assign_level(self):
        nodes = [100, 200, 300, 400, 666]

        expected_level = {100: 0, 200: 1, 300: 1, 400: 0, 666: 0}
        actual_levels = assign_level(nodes, AS_RELATIONSHIPS)

        self.assertEqual(expected_level, actual_levels)


class TestGetAspathChartFig(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "test"
        self.nodes = [100, 200, 300, 400]
        self.egdes = make_edges(self.nodes)
        self.test_expected_chart = r'test_files/test_expected_chart.png'

    def test_get_aspath_chart_fig_returns_figure(self):
        # input: title, nodes, edges, as_relationships
        # Arrange: mock dependencies
        title = self.title
        nodes = self.nodes
        edges = self.egdes
        self.excepted_img = mpimg.imread(self.test_expected_chart)

        actual_fig = get_aspath_chart_fig(title, nodes, edges, AS_RELATIONSHIPS)

        filename = "test_actual_chart.png"
        actual_fig.tight_layout()
        plt.savefig(filename, format="png", dpi=120)
        plt.close(actual_fig)
        plt.clf()

        actual_img = mpimg.imread("test_actual_chart.png")

        np.testing.assert_allclose(self.excepted_img, actual_img, rtol=1e-5, atol=1e-8)
