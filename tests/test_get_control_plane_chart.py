from detection.system.charts.get_control_plane_chart import get_control_plane_chart
from detection.utilities.as_relationships import get_as_relationships
import unittest
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

AS_RELATIONSHIPS = get_as_relationships()


class TestGetControlPlaneChart(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_chart = r'test_files/test_expected_control_plane_chart.png'


    def test_get_control_plane_chart(self):

        self.excepted_img = mpimg.imread(self.test_chart)
        actual_fig, actual_raw_as_path = get_control_plane_chart(sensor_asn=100)

        filename = "test_actual_chart.png"
        actual_fig.tight_layout()
        plt.savefig(filename, format="png", dpi=120)
        plt.close(actual_fig)
        plt.clf()

        actual_img = mpimg.imread("test_actual_chart.png")

        np.testing.assert_allclose(self.excepted_img, actual_img, rtol=1e-5, atol=1e-8)
