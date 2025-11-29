from pymongo import MongoClient
from bson.objectid import ObjectId
from detection.system.charts.as_path_chart_maker import make_edges, get_as_path_chart_fig, AS_RELATIONSHIPS
from detection.utilities.prefix2as import prefix2as
import pandas as pd


def get_data_plane_chart(trace_hops, prefixes, sensor_asn=100):
    """
    Get Data Plane Chart

    :param trace_hops: list of traceroute hops
    :param prefixes:
    :param sensor_asn: in the lab is always 100
    (when running this code in a real environment this number need to change)
    :return: a matplotlib chart figure and a hop-to-asn mapping dictionary
    """
    hop_to_asn_dict = {}
    raw_as_path = [sensor_asn]
    fixed_as_path = []
    prev_asn = None

    for hop in trace_hops:
        if hop['responded']:
            hop_ip = hop['hop_ip']
            asn = prefix2as.ip_to_asn(hop_ip, prefixes)

            if not asn:
                hop_to_asn_dict[hop_ip] = None

            else:
                hop_to_asn_dict[hop_ip] = asn
                raw_as_path.append(asn)

    # clean raw AS path from duplicate ASNs
    for asn in raw_as_path:
        if asn != prev_asn:
            prev_asn = asn
            fixed_as_path.append(asn)

    edges = make_edges(fixed_as_path)

    fig = get_as_path_chart_fig("Data Plane AS-Path", fixed_as_path, edges, AS_RELATIONSHIPS)
    return fig, hop_to_asn_dict
