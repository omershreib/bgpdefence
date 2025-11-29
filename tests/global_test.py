from bson import ObjectId
from pymongo import MongoClient
from detection.dashboard.app import (
    app,
    CONFIG,
    make_mongo_inserter_parameters,
    MongoInserter,
    trace_monitor,
    bgp_worker,
)
import threading
import unittest
import time


class GlobalFlaskAppTest(unittest.TestCase):
    collection = None
    next_uuid = None
    current_uuid = None
    prev_uuid = None
    mongo_client = None
    db = None
    ftp_uploader = None
    monitor = None
    mongo_inserter = None

    def setUp(self):
        # Insert into test DB
        self.collection.replace_one({"_id": self.prev_uuid}, self.doc_prev, upsert=True)
        self.collection.replace_one({"_id": self.current_uuid}, self.doc_current, upsert=True)
        self.collection.replace_one({"_id": self.next_uuid}, self.doc_next, upsert=True)

    @classmethod
    def setUpClass(cls):
        # mongodb config
        MONGO_CLIENT_URL = CONFIG['system']['mongoDB']['client_url']
        MONGO_DATABASE = CONFIG['system']['mongoDB']['test_database']
        MONGO_COLLECTION = CONFIG['system']['mongoDB']['collection']
        
        cls.mongo_client = MongoClient(MONGO_CLIENT_URL)
        cls.db = cls.mongo_client[MONGO_DATABASE]
        cls.collection = cls.db[MONGO_COLLECTION]
        cls.client = app.test_client()

        # Create three documents with predictable UUIDs and timestamps
        cls.prev_uuid = ObjectId("692b3a0f125015030de34232")
        cls.current_uuid = ObjectId("692b3a23125015030de34233")
        cls.next_uuid = ObjectId("692b3a37125015030de34234")

        cls.doc_prev = {
            "_id": cls.prev_uuid,
            "sensor_id": 2,
            "destination_ip": "198.18.1.13",
            "timestamp": "2025-11-29 18:40:00",
            "hops": [{"hop_num": 1, "hop_ip": "192.0.0.254", "delays": [10, 20, 30], "responded": True}],
        }
        cls.doc_current = {
            "_id": cls.current_uuid,
            "sensor_id": 2,
            "destination_ip": "198.18.1.13",
            "timestamp": "2025-11-29 18:48:44",
            "hops": [{"hop_num": 2, "hop_ip": "23.9.1.1", "delays": [23, 21, 31], "responded": True}],
        }
        cls.doc_next = {
            "_id": cls.next_uuid,
            "sensor_id": 2,
            "destination_ip": "198.18.1.13",
            "timestamp": "2025-11-29 18:55:00",
            "hops": [{"hop_num": 3, "hop_ip": "10.0.0.1", "delays": [23, 31, 30], "responded": True}],
        }

        mongo_parameters = make_mongo_inserter_parameters(CONFIG['system']['mongoDB'], mode='test')
        monitor_parameters = CONFIG['system']['monitor_setup']

        cls.mongo_inserter = MongoInserter(**mongo_parameters)
        cls.mongo_inserter.daemon = True
        cls.mongo_inserter.start()

        cls.monitor = trace_monitor.TraceMonitor(**monitor_parameters)
        cls.monitor.daemon = True
        cls.monitor.start()

        cls.ftp_uploader = threading.Thread(target=bgp_worker, daemon=True)
        cls.ftp_uploader.start()

    @classmethod
    def tearDownClass(cls):
        cls.collection.delete_many({"_id": {"$in": [cls.prev_uuid, cls.current_uuid, cls.next_uuid]}})

        # attempt to gracefully stop threads
        try:
            if hasattr(cls.mongo_inserter, "stop"):
                cls.mongo_inserter.stop()
            if hasattr(cls.monitor, "stop"):
                cls.monitor.stop()
        except Exception:
            pass

    def test_pipeline_inserts_traceroute(self):
        # wait for monitor to produce and inserter to consume
        time.sleep(20)

        # verify that at least one traceroute document exists
        doc = self.collection.find_one({})
        self.assertIsNotNone(doc, "no traceroute document was inserted into mongoDB")

        # check essential fields
        self.assertIn("sensor_id", doc)
        self.assertIn("destination_ip", doc)
        self.assertIn("timestamp", doc)
        self.assertIn("hops", doc)

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
