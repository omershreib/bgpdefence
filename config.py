import os

__path__ = os.getcwd()

if 'tests' in __path__:
    __path__ = __path__.removesuffix(r'\tests')

CONFIG = {}

# dashboard configuration
CONFIG['dashboard'] = {
    'delay_points_limit': 25,
    'delay_points_threshold': 150
}

CONFIG['system'] = {}

# system monitor configuration
CONFIG['system']['monitor_setup'] = {
    'sensor_ip': '192.0.0.3',
    'destination_ip': '198.18.1.13',
    'delta': 5,
    'duration': 10_800,
    'frequency': 15
}

# system mongoDB configuration
CONFIG['system']['mongoDB'] = {
    'client_url': 'mongodb://localhost:27017/',
    'prod_database': 'network_monitoring',
    'test_database': 'test_network_monitoring',
    'collection': 'traceroutes',
    'trace_queue_check_frequency': 5
}

# flask application configuration
CONFIG['system']['flask_app'] = {
    'server_name': 'bgp_defence',
    'secret_key': 'bgphijack',
    'host': '192.0.0.3',
    'port': 5000,
    'updater_loop_sleep_time': 60,
}

# utilities configuration
CONFIG['utilities'] = {
    'prefix2as': rf'{__path__}\detection\utilities\prefix2as\prefix2as.csv',
    'bgp_table': rf'{__path__}\detection\utilities\bgp_table'
                 r'\latest_bgp_table.txt',
    'test_bgp_table': rf'{__path__}\tests\test_files\test_bgp_table.txt'
}

# FTP upload/download process configuration
CONFIG['ftp_process'] = {
    'thread_worker_sleep_time': 60,
    'server_ip': '203.0.113.1',
    'user': 'ftpuser',
    'password': '051295',
    'filename': 'bgp_table.txt',
    'filepath': rf'{__path__}\detection',

    'local_isp': {'router_ip': '203.0.113.254',
                  'user': 'local_isp',
                  'password': '051295'}
}

# sensors dictionary configuration
# this enables to run multiple dashboards - each for a different sensor located in a different
# LAN or a different geographical location. but in order to do so we need to identify these
# sensor by their IP address, so we can query only the data from mongoDB that is relevant
# to traceroutes made by a specific sensor
CONFIG['sensors_dict'] = {
    '192.168.1.246': 1,
    '192.0.0.3': 2
}




