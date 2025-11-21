from pyparsing import Word, Combine, Optional, oneOf, nums, Group, OneOrMore, Literal, ParseException
from ipaddress import IPv4Address, IPv4Network
from parse_ip_route import ip_routes_to_net_masks_dict
import pandas as pd

def load_bgp_table_file(filename):
    flag = False
    file_lines = []

    with open(filename, 'r') as f:
        for line in f:
            # print(line)
            if flag and ('>' in line):
                file_lines.append(line.strip('\n'))

            if 'Network' in line:
                # print(line)
                # file_lines.append(line.strip('\n'))
                flag = True

    return file_lines


bgp_file = r"D:\Documents\open university\netSeminar\source\detection\system\sensor\bgp_table.txt"
table = load_bgp_table_file(bgp_file)

# Define grammar components
status_code = Combine(Optional(oneOf("r * >")) + Optional(Literal(">")))
ip_octet = Word(nums, max=3)
ip_addr = Combine(ip_octet + "." + ip_octet + "." + ip_octet + "." + ip_octet)
prefix = Combine(ip_addr + Optional("/" + Word(nums)))
next_hop = ip_addr
metric = Word(nums)
locprf = Word(nums)
weight = Word(nums)
path = Group(OneOrMore(Word(nums)))
origin = oneOf("i e ?")

bgp_fields = ["status", "network", "next_hop", "metric", "locprf", "weight", "path", "origin"]

# Full grammar
bgp_line_v1 = (
        status_code("status")
        + prefix("network")
        + next_hop("next_hop")
        + metric("metric")
        + locprf("locprf")
        + weight("weight")
        + Optional(path("path"))
        + origin("origin")
)

bgp_line_v2 = (
        status_code("status")
        + prefix("network")
        + next_hop("next_hop")
        + metric("metric")
        + weight("weight")
        + Optional(path("path"))
        + origin("origin")
)

bgp_line_v3 = (
        status_code("status")
        + prefix("network")
        + next_hop("next_hop")
        + weight("weight")
        + Optional(path("path"))
        + origin("origin")
)


def test_parse():
    line = "r> 1.1.1.1/32       2.2.2.2                  0             0 200 ?"
    # Parse the line
    result = bgp_line_v1.parseString(line)

    # Show parsed fields
    print("Status:", result["status"])
    print("Network:", result["network"])
    print("Next Hop:", result["next_hop"])
    print("Metric:", result["metric"])
    print("LocPrf:", result["locprf"])
    print("Weight:", result["weight"])
    print("Path:", result.get("path", []))
    print("Origin:", result["origin"])


# def normalize_network(net_str, net_mask):
#     if "/" not in net_str:
#         #return IPv4Network(net_str + "/32", strict=False)
#         return IPv4Network(f"{net_str}{net_mask[net_str]}", strict=False)
#     return IPv4Network(net_str, strict=False)


def normalize_network(net_str):
    if "/" not in net_str:
        # Default to /24 instead of /32
        return IPv4Network(net_str + "/24", strict=False)
    return IPv4Network(net_str, strict=False)



def bgp_table_to_dict():
    bgp_routes = []
    for row in table:
        results = []
        try:
            result_v1 = bgp_line_v1.parseString(row)
            results.append(result_v1)
        except ParseException:
            results.append(None)

        try:
            result_v2 = bgp_line_v2.parseString(row)
            results.append(result_v2)
        except ParseException:
            results.append(None)

        try:
            result_v3 = bgp_line_v3.parseString(row)
            results.append(result_v3)
        except ParseException:
            results.append(None)

        for i, result in enumerate(results):

            if not result:
                continue

            keys = list(result.keys())
            bgp_route: dict = {bgp_field: None for bgp_field in bgp_fields}

            if result['next_hop'] != '0.0.0.0' and 'path' not in keys:
                continue

            if 'weight' in keys and result['weight'] not in ['0', '32768']:
                continue

            if 'path' in keys and result['path'][0] in ['0', '32768']:
                continue

            for key in keys:
                if key == 'path':
                    bgp_route[key] = list(result[key])

                else:
                    bgp_route[key] = result[key]

            bgp_routes.append(bgp_route)

    return bgp_routes


if __name__ == '__main__':

    bgp_routes = bgp_table_to_dict()
    #masks = ip_routes_to_net_masks_dict()
    for route in bgp_routes:
        print(route)

    df = pd.DataFrame(bgp_routes)

    #df["network_obj"] = df["network"].apply(normalize_network, args=(masks,))
    df["network_obj"] = df["network"].apply(normalize_network)
    print(df)


    # === Query by IP address ===
    query_ip = IPv4Address("198.18.1.13")
    matches_ip = df[df["network_obj"].apply(lambda net: query_ip in net)]
    print("Matches for IP:", matches_ip.to_dict())

    # === Query by prefix ===
    query_net = IPv4Network("198.18.1.0/25")
    matches_net = df[df["network_obj"].apply(lambda net: net.overlaps(query_net))]
    print("Matches for prefix:", matches_net.to_dict())
