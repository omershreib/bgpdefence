from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from detection.system.charts.aspath_charts_maker import make_edges, get_aspath_chart_fig, AS_RELATIONSHIPS
from pprint import pprint
from detection.detection_tools import prefix2as
import pandas as pd


def get_dplane_chart(trace_hops, prefixes, sensor_asn=100):

    hop_to_asn_dict = {}
    raw_as_path = [sensor_asn]

    for hop in trace_hops:
        print(hop)
        hop_ip = hop['hop_ip']
        response = prefixes.query('network == @hop_ip')

        if response.empty:
            hop_to_asn_dict[hop_ip] = None

        else:
            asn = int(response.asn.values[0])
            hop_to_asn_dict[hop_ip] = asn
            raw_as_path.append(asn)

        #print(response)

        #pprint(hop_to_asn_dict)
        #print(raw_as_path)

    egdes = make_edges(raw_as_path)

    fig = get_aspath_chart_fig("Data Plane AS-Path",raw_as_path, egdes, AS_RELATIONSHIPS)
    return fig, hop_to_asn_dict

def cplane_test():
    prefix2as_csv = r"D:\Documents\open university\netSeminar\source\detection\detection_tools\prefix2as.csv"
    prefixes = pd.read_csv(prefix2as_csv)

    trace_hops = [{'hop_num': 1, 'hop_ip': '192.0.0.254', 'delays': [3.0, 10.0, 10.0], 'responded': True},
                 {'hop_num': 2, 'hop_ip': '23.9.1.1', 'delays': [17.0, 20.0, 20.0], 'responded': True},
                 {'hop_num': 3, 'hop_ip': '10.0.0.1', 'delays': [42.0, 41.0, 41.0], 'responded': True},
                 {'hop_num': 4, 'hop_ip': '10.0.0.9', 'delays': [49.0, 42.0, 51.0], 'responded': True},
                 {'hop_num': 5, 'hop_ip': '10.0.0.18', 'delays': [60.0, 61.0, 72.0], 'responded': True},
                 {'hop_num': 6, 'hop_ip': '198.18.1.13', 'delays': [74.0, 72.0, 72.0], 'responded': True}]

    fig, hop_to_asn_dict = get_dplane_chart(trace_hops, prefixes)


if __name__ == '__main__':
    cplane_test()
    # # mongodb config
    # client = MongoClient("mongodb://localhost:27017/")
    # db = client["network_monitoring"]
    # collection = db["traceroutes"]
    # traceroute_id = ObjectId("69219177988e64c0570e10e8")
    #
    # prefix2as_csv = r"D:\Documents\open university\netSeminar\source\detection\detection_tools\prefix2as.csv"
    # prefixes = pd.read_csv(prefix2as_csv)
    #
    # print(prefixes)
    #
    # data_plane = collection.find_one({"sensor_id": 2, "_id": ObjectId(f"{traceroute_id}")})
    # destination_ip = data_plane['destination_ip']
    # trace_hops = data_plane['hops']
    # print(f"destination_ip: {destination_ip}")
    # print()
    # get_dplane_chart(trace_hops, prefixes)
