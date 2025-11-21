import re


def load_ip_route_file(filename):
    flag = False
    file_lines = []

    curr_subnet = None

    with open(filename, 'r') as f:
        for line in f:
            if line == '\n':
                continue

            prefix = None
            #subnet = re.findall(r'(\/[\d]{1,2})\s', line)
            subnet = re.findall(r'\d+\.\d+\.\d+\.\d+(\/[\d]{1,2})\s', line)

            if subnet:
                curr_subnet = subnet[0]

            if line.startswith('B') or line.startswith('C'):
                prefix = re.findall(r'(\d+\.\d+\.\d+\.\d+)[^\,]', line)

            if prefix:
                print(prefix[0], curr_subnet)
                file_lines.append((prefix[0], curr_subnet))

    return file_lines


def ip_routes_to_net_masks_dict():
    ip_route_file = r"D:\Documents\open university\netSeminar\source\detection\system\sensor\ip_route_bgp.txt"
    ip_routes = load_ip_route_file(ip_route_file)
    net_masks: dict = {}

    for network, mask in ip_routes:
        net_masks[network] = mask

    return net_masks


if __name__ == '__main__':
    masks = ip_routes_to_net_masks_dict()
    print(masks)

