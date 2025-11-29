from config import CONFIG
from detection.dashboard.tools.save_fig_png import save_fig_png
from detection.dashboard.tools.get_bgp_table_from_ftp import pull_bgp_table
from detection.system.charts.get_control_plane_chart import get_control_plane_chart
from detection.system.charts.get_data_plane_chart import get_data_plane_chart
from detection.system.charts.get_delay_chart import get_delay_chart
from bson.objectid import ObjectId
import time

DELAY_POINT_LIMIT = CONFIG['dashboard']['delay_points_limit']
DELAY_POINT_THRESHOLD = CONFIG['dashboard']['delay_points_threshold']


def get_sensor_id():
    sensor_ip = CONFIG['system']['monitor_setup']['sensor_ip']
    return CONFIG['sensors_dict'][sensor_ip]


def save_exception_wrapper(*args, **kwargs):
    # for some reason that I did not have enough time to investigate, I sometimes receive an error when attempting
    # to save figures. the quickest and deaerates solution is to ignore these errors ... /: (when refreshing the page
    # any glitch in the dashboard should be fixed)
    try:
        return save_fig_png(*args, **kwargs)

    except Exception as e:
        print(e)
        return None


def compute_state(collection, prefixes, traceroute_id):
    """

    fetch the latest data to the dashboard. this includes latest raw traceroute pulled from mongoDB and download
    and parse latest BGP snapshot from localISP routing table. then generating all the charts (delay chart,
    control-plane chart and data-plane chart). all these goods return by this function.

    :param collection: mongoDB MongoClient object (should equal to db['traceroutes'])
    :param prefixes: matrix of GNS3 lab project prefixes
    :param traceroute_id: traceroute Object id
    :return: a dictionary with the following keys:

        "data_plane": raw traceroute data
        "delay_chart_url": URL to delay chart
        "control_plane_chart_url": URL to control plane chart
        "data_plane_chart_url": URL to data plane chart
        "prev_id": previous traceroute Object id (if not exist return current traceroute id)
        "next_id": next traceroute Object id (if not exist return current traceroute id)
        "ts": time parameter for image caching
    """
    curr_data_plane = collection.find_one({"sensor_id": get_sensor_id(), "_id": ObjectId(f"{traceroute_id}")})
    if not curr_data_plane:
        return None

    destination_ip = curr_data_plane["destination_ip"]
    trace_hops = curr_data_plane["hops"]

    prev_data_plane = collection.find_one(
        {"destination_ip": destination_ip, "sensor_id": get_sensor_id(), "_id": {"$lt": ObjectId(traceroute_id)}},
        sort=[("_id", -1)]
    )
    next_data_plane = collection.find_one(
        {"destination_ip": destination_ip, "sensor_id": get_sensor_id(), "_id": {"$gt": ObjectId(traceroute_id)}},
        sort=[("_id", 1)]
    )

    pull_bgp_table('latest_bgp_table.txt')

    delay_chart_fig = get_delay_chart(collection)
    delay_chart_url = save_exception_wrapper(delay_chart_fig, prefix="delay_chart")

    control_plane_chart_fig, _ = get_control_plane_chart()
    control_plane_chart_url = save_exception_wrapper(control_plane_chart_fig, prefix="control_plane_chart")

    data_plane_chart_fig, data_plane_hops_to_asn = get_data_plane_chart(trace_hops, prefixes)
    data_plane_chart_url = save_exception_wrapper(data_plane_chart_fig, prefix="data_plane_chart")

    # expand raw traceroute data with ASN data when exist
    for hop in trace_hops:
        if hop["responded"]:
            hop_asn = data_plane_hops_to_asn.get(hop["hop_ip"])
            hop["asn"] = hop_asn if hop_asn else "*"

        if not hop["responded"]:
            hop["asn"] = '*'

    return {
        "data_plane": curr_data_plane,
        "delay_chart_url": delay_chart_url,
        "control_plane_chart_url": control_plane_chart_url,
        "data_plane_chart_url": data_plane_chart_url,
        "prev_id": str(prev_data_plane["_id"]) if prev_data_plane else traceroute_id,
        "next_id": str(next_data_plane["_id"]) if next_data_plane else traceroute_id,
        "ts": int(time.time())
    }


if __name__ == '__main__':
    pull_bgp_table("latest_bgp_table.txt")
