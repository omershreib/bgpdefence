from datetime import datetime, timedelta
from detection.system.sensor.traceroute import traceroute_host
from detection.system.database.mongo_inserter import trace_queue
import threading
import time


class TraceMonitor(threading.Thread):
    """traceroute monitor thread class"""
    def __init__(self, ip_address: str, sensor_ip: str, delta: int, duration: int, frequency: int):
        """

        :param ip_address (str): monitored IP address
        :param sensor_ip (str): sensor's IP address
        :param delta (int): time in seconds before the monitor start-time
        :param duration (int): duration time in seconds of this monitor
        :param frequency (int): frequency of traceroute probes in seconds

        all these parameters can be configured in the config file located in the root of this project
        """
        super().__init__()
        self.ip_address = ip_address
        self.start_time = datetime.now() + timedelta(seconds=delta)
        self.end_time = self.start_time + timedelta(seconds=duration)
        self.sensor_ip = sensor_ip
        self._stop_event = threading.Event()
        self.frequency = frequency

    def run_traceroute(self):
        """run traceroute command and return output as string"""
        try:
            return traceroute_host(self.ip_address)
        except Exception as e:
            return f"Error running traceroute: {e}"

    def run(self):
        """Main thread loop: perform traceroute every 1 minute between start and end time"""
        while datetime.now() < self.start_time and not self._stop_event.is_set():
            time.sleep(1)

        while datetime.now() <= self.end_time and not self._stop_event.is_set():
            print(f"[{datetime.now()}] running traceroute to {self.ip_address}")
            output = self.run_traceroute()

            pack = (self.sensor_ip, self.ip_address, output)
            trace_queue.put(pack)

            # Sleep for 1 minute
            time.sleep(self.frequency)

    def stop(self):
        """stop the monitoring thread"""
        self._stop_event.set()


if __name__ == '__main__':
    from config import CONFIG

    monitor_parameters = CONFIG['system']['monitor_setup']

    monitor = TraceMonitor(**monitor_parameters)
