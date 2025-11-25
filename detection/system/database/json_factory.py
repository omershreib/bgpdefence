from datetime import datetime


sensors_dict = {'192.168.1.246': 1,
                '192.0.0.3': 2}

def jsonify_trace_list(sensor_ip, destination_ip, hops):

    #print(f"hops: {hops}")
    json_hops = []

    for hop in hops:
        #print(f"hop: {hop}")
        hop_num = hop[0]
        delays = hop[1]
        hop_ip = hop[2]
        json_hop = {}

        if hop_ip:
            json_hop = {"hop_num": hop_num, "hop_ip": hop_ip, "delays": delays, "responded": True}

        if not hop_ip:
            json_hop = {"hop_num": hop_num, "delays": delays, "responded": False}

        json_hops.append(json_hop)

    json_doc = {
        "timestamp": datetime.now(),  # required for time series
        "sensor_id": sensors_dict[sensor_ip],
        # "sensor_ip": sensor_ip,
        "destination_ip": destination_ip,
        "hops": json_hops
    }

    return json_doc
