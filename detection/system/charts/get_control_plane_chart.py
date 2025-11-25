from config import CONFIG
from detection.system.charts.aspath_charts_maker import make_edges, get_aspath_chart_fig, AS_RELATIONSHIPS
from detection.system.analysis import parse_bgp
from ipaddress import IPv4Address
from pprint import pprint
import pandas as pd


def get_control_plane_chart(sensor_asn=100):

    raw_as_path = [sensor_asn]

    bgp_file = CONFIG['utilites']['bgp_table']
    bgp_routes = parse_bgp.bgp_table_to_dict(bgp_file)

    df = pd.DataFrame(bgp_routes)
    df["network_obj"] = df["network"].apply(parse_bgp.normalize_network)

    query_ip = IPv4Address("198.18.1.13")
    matches_ip = df[df["network_obj"].apply(lambda net: query_ip in net)]

    if not matches_ip.empty:
        raw_as_path.extend([int(asn) for asn in matches_ip['path'].to_list()[0]])

    egdes = make_edges(raw_as_path)

    fig = get_aspath_chart_fig("Control Plane AS-Path",raw_as_path, egdes, AS_RELATIONSHIPS)
    return fig, raw_as_path


# if __name__ == '__main__':
#     import pandas as pd
#     import matplotlib
#     matplotlib.use('Agg')
#
#     import matplotlib.pyplot as plt
#
#     from detection.system.sensor.bgp_table_from_ftp import pull_bgp_table_from_ftp as pull_ftp
#
#     # filename = bgp_route_table_ftp_upload.get_bgp_output()
#     #print("Uploading to FTP...")
#
#     pull_ftp("latest_bgp_table.txt")
#
#     #prefix2as_csv = r"D:\Documents\open university\netSeminar\source\detection\utilites\prefix2as.csv"
#     #my_prefixes = pd.read_csv(prefix2as_csv)
#
#     fig = get_control_plane_chart()
#     plt.savefig("test_control_plane_fig.png")
