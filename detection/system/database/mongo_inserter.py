from detection.system.sensor.traceroute import get_traceroute_list
from detection.system.database.json_factory import jsonify_trace_list
from pymongo import MongoClient
from queue import Queue
import threading
import time

trace_queue = Queue()


def make_mongo_inserter_parameters(items: dict, mode='prod'):
    client_url: str = items['client_url']

    if mode == 'prod':
        database: str = items['prod_database']

    if mode == 'test':
        database: str = items['test_database']

    collection: str = items['collection']
    frequency: int = items['trace_queue_check_frequency']

    mongo_client = MongoClient(client_url)
    mongo_db = mongo_client[database]
    mongo_collection = mongo_db[collection]

    return {'collection': mongo_collection, 'frequency': frequency}


class MongoInserter(threading.Thread):
    """mongoDB inserter thread class"""
    def __init__(self, collection: MongoClient, frequency: int):
        """

        :param collection (MongoClient): mongoDB MongoClient object (should equal to db['traceroutes'])
        :param client (MongoClient): client object for mongoDB instance
        :param frequency (int): the time gap (in seconds) between traced probes

        all these parameters can be configured in the config file located in the root of this project
        """
        super().__init__()
        self.collection = collection
        self.frequency = frequency
        self._stop_event = threading.Event()

    def run(self):
        inserter_sleep = self.frequency
        while True:
            if trace_queue.empty():
                print("traceroute queue is empty...")
                time.sleep(inserter_sleep)
                continue

            items = trace_queue.get()
            sensor_ip, target_ip, data_plane = items
            trace_list = get_traceroute_list(data_plane)

            to_json_doc = jsonify_trace_list(sensor_ip, target_ip, trace_list)
            result = self.collection.insert_one(to_json_doc)

            print("inserted document ID:", result.inserted_id)
            time.sleep(inserter_sleep)

    def stop(self):
        self._stop_event.set()


if __name__ == '__main__':
    from config import CONFIG

    mongo_inserter_parameters = CONFIG['system']['mongoDB']
    client = MongoClient("mongodb://localhost:27017/")

    # Select database
    db = client["network_monitoring"]

    MongoInserter(**mongo_inserter_parameters)
