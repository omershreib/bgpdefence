from detection.dashboard.dashboard_tools.save_fig_png import save_fig_png
from detection.system.sensor.bgp_table_from_ftp import pull_bgp_table
from detection.system.charts.get_control_plane_chart import get_control_plane_chart
from detection.system.charts.get_data_plane_chart import get_data_plane_chart
from detection.system.charts.get_delay_chart import get_delay_chart
from bson.objectid import ObjectId
import time


def compute_state(collection, prefixes, traceroute_id: str):
    """Fetch latest state and generate charts for a given traceroute id."""
    curr_data_plane = collection.find_one({"sensor_id": 2, "_id": ObjectId(f"{traceroute_id}")})
    if not curr_data_plane:
        return None

    destination_ip = curr_data_plane["destination_ip"]
    trace_hops = curr_data_plane["hops"]

    prev_data_plane = collection.find_one(
        {"destination_ip": destination_ip, "sensor_id": 2, "_id": {"$lt": ObjectId(traceroute_id)}},
        sort=[("_id", -1)]
    )
    next_data_plane = collection.find_one(
        {"destination_ip": destination_ip, "sensor_id": 2, "_id": {"$gt": ObjectId(traceroute_id)}},
        sort=[("_id", 1)]
    )

    # Delay chart
    print("update delay chart")
    delay_chart_fig = get_delay_chart(collection)
    delay_chart_url = save_fig_png(delay_chart_fig, prefix="delay_chart")

    # update BGP table (provided by LocalISP)
    pull_bgp_table('latest_bgp_table.txt')

    # control plane chart
    control_plane_chart_fig, _ = get_control_plane_chart()
    control_plane_chart_url = save_fig_png(control_plane_chart_fig, prefix="control_plane_chart")

    # data plane chart
    data_plane_chart_fig, data_plane_hops_to_asn = get_data_plane_chart(trace_hops, prefixes)
    data_plane_chart_url = save_fig_png(data_plane_chart_fig, prefix="data_plane_chart")

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
        # Timestamp used to bust browser cache on images
        "ts": int(time.time())
    }


if __name__ == '__main__':
    pull_bgp_table("latest_bgp_table.txt")