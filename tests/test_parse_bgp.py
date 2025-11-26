from detection.system.analysis.parse_bgp import load_bgp_table_file, normalize_network, bgp_table_to_dict
from expected_bgp_routes import expected_bgp_routes
from ipaddress import IPv4Address, IPv4Network
import unittest


class TestParseBGP(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_file = r'test_files/test_bgp_table.txt'
        self.expected_file = 'test_expected_loaded_bgp_file.txt'

    def load_expected_bgp_lines(self):
        bgp_lines = []

        with open(self.expected_file, 'r') as f:
            for line in f:
                bgp_lines.append(line.strip('\n'))

        return bgp_lines

    def test_load_bgp_table_file(self):
        expected_bgp_lines = self.load_expected_bgp_lines()
        actual_bgp_lines = load_bgp_table_file(self.test_file)
        self.assertEqual(expected_bgp_lines, actual_bgp_lines)

    def test_normalize_network(self):
        # test case of not normalized prefix network (without /<num>), default is /24
        test_net: str = '192.168.0.0'

        expected_result = IPv4Network(test_net + "/24")
        actual_result = normalize_network(test_net)
        self.assertEqual(expected_result, actual_result)

        # test case of already normalized prefix network (with /<num>)
        test_normalized_net: str = '192.168.0.0/24'

        expected_result = IPv4Network(test_normalized_net)
        actual_result = normalize_network(test_normalized_net)
        self.assertEqual(expected_result, actual_result)

    def test_bgp_table_to_dict(self):
        actual_bgp_routes: dict = bgp_table_to_dict(self.test_file)
        self.assertEqual(expected_bgp_routes, actual_bgp_routes)
