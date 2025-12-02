from config import CONFIG
from detection.system.charts.as_path_chart_maker import make_edges, get_as_path_chart_fig, AS_RELATIONSHIPS
from detection.utilities.bgp_table import parse_bgp
from ipaddress import IPv4Address
import pandas as pd


def get_control_plane_chart(sensor_asn=100, mode='prod'):
    raw_as_path = [sensor_asn]

    if mode == 'test':
        bgp_file = CONFIG['utilities']['test_bgp_table']

    if mode == 'prod':
        bgp_file = CONFIG['utilities']['bgp_table']

    bgp_routes = parse_bgp.bgp_table_to_dict(bgp_file)

    df = pd.DataFrame(bgp_routes)
    df["network_obj"] = df["network"].apply(parse_bgp.normalize_network)

    monitored_ip = CONFIG['system']['monitor_setup']['destination_ip']
    query_ip = IPv4Address(monitored_ip)
    matches_ip = df[df["network_obj"].apply(lambda net: query_ip in net)]

    if not matches_ip.empty:
        raw_as_path.extend([int(asn) for asn in matches_ip['path'].to_list()[0]])

    edges = make_edges(raw_as_path)

    fig = get_as_path_chart_fig("Control Plane AS-Path", raw_as_path, edges, AS_RELATIONSHIPS)
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
#     #prefix2as_csv = r"D:\Documents\open university\netSeminar\source\detection\utilities\prefix2as.csv"
#     #my_prefixes = pd.read_csv(prefix2as_csv)
#
#     fig = get_control_plane_chart()
#     plt.savefig("test_control_plane_fig.png")
