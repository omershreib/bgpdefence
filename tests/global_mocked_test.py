from detection.dashboard.app import app
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import patch
from bs4 import BeautifulSoup
import unittest


class GlobalFlaskAppTest(unittest.TestCase):

    def setUp(self):
        self.current_uuid = "6922db4f70e2244faa2a3393"
        self.prev_uuid = "6922db3e1456de9ce70f7aa8"
        self.next_uuid = "6922db531456de9ce70f7aa9"

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

        current_fake_timestamp = datetime.now()
        prev_fake_timestamp = current_fake_timestamp - timedelta(minutes=1)
        next_fake_timestamp = current_fake_timestamp + timedelta(minutes=1)

        # define fake documents
        cls.doc_prev = {
            "_id": ObjectId("6922db3e1456de9ce70f7aa8"),
            "sensor_id": 2,
            "destination_ip": "198.18.1.13",
            "timestamp": prev_fake_timestamp,
            "hops": [{'hop_num': 1, 'hop_ip': '192.0.0.254', 'delays': [7.0, 10.0, 9.0], 'responded': True},
                     {'hop_num': 2, 'hop_ip': '23.9.1.1', 'delays': [13.0, 20.0, 30.0], 'responded': True},
                     {'hop_num': 3, 'hop_ip': '10.0.0.1', 'delays': [42.0, 42.0, 31.0], 'responded': True},
                     {'hop_num': 4, 'hop_ip': '10.0.0.9', 'delays': [64.0, 72.0, 72.0], 'responded': True},
                     {'hop_num': 5, 'hop_ip': '10.0.0.18', 'delays': [85.0, 51.0, 52.0], 'responded': True},
                     {'hop_num': 6, 'hop_ip': '198.18.1.13', 'delays': [78.0, 82.0, 82.0], 'responded': True}]

        }
        cls.doc_current = {
            "_id": ObjectId("6922db4f70e2244faa2a3393"),
            "sensor_id": 2,
            "destination_ip": "198.18.1.13",
            "timestamp": current_fake_timestamp,
            "hops": [{'hop_num': 1, 'hop_ip': '192.0.0.254', 'delays': [11.0, 10.0, 10.0], 'responded': True},
                     {'hop_num': 2, 'hop_ip': '23.9.1.1', 'delays': [23.0, 21.0, 31.0], 'responded': True},
                     {'hop_num': 3, 'hop_ip': '10.0.0.1', 'delays': [23.0, 31.0, 30.0], 'responded': True},
                     {'hop_num': 4, 'hop_ip': '10.0.0.9', 'delays': [43.0, 41.0, 51.0], 'responded': True},
                     {'hop_num': 5, 'hop_ip': '10.0.0.18', 'delays': [54.0, 62.0, 83.0], 'responded': True},
                     {'hop_num': 6, 'hop_ip': '198.18.1.13', 'delays': [81.0, 73.0, 81.0], 'responded': True}]

        }
        cls.doc_next = {
            "_id": ObjectId("6922db531456de9ce70f7aa9"),
            "sensor_id": 2,
            "destination_ip": "198.18.1.13",
            "timestamp": next_fake_timestamp,
            "hops": [{'hop_num': 1, 'hop_ip': '192.0.0.254', 'delays': [4.0, 10.0, 10.0], 'responded': True},
                     {'hop_num': 2, 'hop_ip': '23.9.1.1', 'delays': [17.0, 20.0, 20.0], 'responded': True},
                     {'hop_num': 3, 'hop_ip': '10.0.0.1', 'delays': [25.0, 30.0, 30.0], 'responded': True},
                     {'hop_num': 4, 'hop_ip': '10.0.0.9', 'delays': [54.0, 40.0, 51.0], 'responded': True},
                     {'hop_num': 5, 'hop_ip': '10.0.0.18', 'delays': [147.0, 62.0, 61.0], 'responded': True},
                     {'hop_num': 6, 'hop_ip': '198.18.1.13', 'delays': [79.0, 72.0, 83.0], 'responded': True}]
        }

    def make_state(self, uuid, prev_id, next_id):
        """Fake Compute State"""
        doc = dict(self.doc_current)
        hops = []

        # fake mapping of hop_ip to ASN
        data_plane_hops_to_asn = {
            "192.0.0.254": 65001,
            "23.9.1.1": 65001,
            "10.0.0.1": 300,
            "10.0.0.9": 300,
            "10.0.0.18": 400,
            "198.18.1.13": 400,
        }

        for hop in doc["hops"]:
            if hop.get("responded"):
                hop_asn = data_plane_hops_to_asn.get(hop["hop_ip"])
                hop["asn"] = hop_asn if hop_asn else "*"
            else:
                hop["asn"] = "*"
            hops.append(hop)

        doc["hops"] = hops

        return {
            "data_plane": self.doc_current,
            "delay_chart_url": "/static/charts/delay_chart.png",
            "control_plane_chart_url": "/static/charts/control_plane_chart.png",
            "data_plane_chart_url": "/static/charts/data_plane_chart.png",
            "prev_id": self.prev_uuid,
            "next_id": self.next_uuid,
            "ts": "2025-11-29T18:00:00Z",
        }

    @patch("detection.dashboard.app.compute_state")
    def test_dashboard_renders_all_data(self, mock_compute_state):
        mock_compute_state.return_value = self.make_state(self.current_uuid, self.prev_uuid, self.next_uuid)

        response = self.client.get(f"/dashboard?uuid={self.current_uuid}")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.data, "html.parser")

        # check header fields
        self.assertIn(f"UUID: {self.current_uuid}".encode(), response.data)
        self.assertIn(f"sensorId:    {self.doc_current['sensor_id']}".encode(), response.data)
        self.assertIn(f"destination: {self.doc_current['destination_ip']}".encode(), response.data)

        # check each hop row
        table = soup.find("table", {"id": "data_plane"})
        rows = table.find_all("tr")[1:]

        for hop, row in zip(self.doc_current["hops"], rows):
            cells = [c.get_text(strip=True) for c in row.find_all("td")]

            # check hop index number
            self.assertEqual(str(hop["hop_num"]), cells[0])

            # check delays (rounded to int in template)
            expected_delays = [f"{int(d)}ms" for d in hop["delays"]]
            self.assertEqual(expected_delays[0], cells[1])
            self.assertEqual(expected_delays[1], cells[2])
            self.assertEqual(expected_delays[2], cells[3])

            # check hop IP address
            self.assertEqual(hop["hop_ip"], cells[4])

            # check hop ASN
            self.assertEqual(str(hop["asn"]), cells[5])

    @patch("detection.dashboard.app.compute_state")
    def test_prev_next_navigation(self, mock_compute_state):
        # mock compute_state to return deterministic prev/current/next states
        def side_effect(collection, prefixes, traceroute_id):
            if traceroute_id == self.prev_uuid:
                return self.make_state(self.prev_uuid, None, self.current_uuid)
            if traceroute_id == self.current_uuid:
                return self.make_state(self.current_uuid, self.prev_uuid, self.next_uuid)
            if traceroute_id == self.next_uuid:
                return self.make_state(self.next_uuid, self.current_uuid, None)
            return None

        mock_compute_state.side_effect = side_effect

        # request current dashboard
        resp_current = self.client.get(f"/dashboard?uuid={self.current_uuid}")
        self.assertEqual(resp_current.status_code, 200)

        # parse HTML with BeautifulSoup
        soup = BeautifulSoup(resp_current.data, "html.parser")

        # find prev/next buttons
        prev_link = soup.find("a", {"name": "btn_previous"})
        next_link = soup.find("a", {"name": "btn_next"})

        # ensure that prev/next buttons exists
        self.assertIsNotNone(prev_link)
        self.assertIsNotNone(next_link)

        # check that prev/next buttons links contain correct UUIDs
        self.assertIn(self.prev_uuid, prev_link["href"])
        self.assertIn(self.next_uuid, next_link["href"])

        # illustrates user press prev button
        resp_prev = self.client.get(prev_link["href"])
        self.assertEqual(resp_prev.status_code, 200)
        self.assertIn(f"/dashboard?uuid={self.prev_uuid}&amp;only_stream_raw_data_plane=True".encode(), resp_prev.data)

        # illustrates user press next button
        resp_next = self.client.get(next_link["href"])
        self.assertEqual(resp_next.status_code, 200)
        self.assertIn(f"/dashboard?uuid={self.next_uuid}&amp;only_stream_raw_data_plane=True".encode(), resp_next.data)

    def test_root_redirects_to_dashboard(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.location)

    def test_dashboard_page(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"data_plane", response.data)

    def test_live_dashboard_page(self):
        response = self.client.get("/live_dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"data_plane" in response.data or b"cannot find traceroute" in response.data)


if __name__ == "__main__":
    unittest.main()
