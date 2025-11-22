

def get_as_relationships():
    asn_list = [100, 200, 300, 400, 666]

    as_relationships = {asn: {'customers': [], 'providers': [], 'other_peers': []} for asn in asn_list}

    # as-relationships setup for ASN 100
    as_relationships[100]['providers'].append(200)

    # as-relationships setup for ASN 200
    as_relationships[200]['customers'].append(100)
    as_relationships[200]['customers'].append(666)
    as_relationships[200]['providers'].append(200)
    as_relationships[200]['other_peers'].append(300)

    # as-relationships setup for ASN 300
    as_relationships[300]['customers'].append(400)
    as_relationships[300]['customers'].append(666)
    as_relationships[300]['other_peers'].append(200)
    #as_relationships[300]['other_peers'].append(666)

    # as-relationships setup for ASN 400
    as_relationships[400]['providers'].append(300)

    # as-relationships setup for ASN 666
    as_relationships[666]['providers'].append(200)
    #as_relationships[666]['other_peers'].append(300)
    as_relationships[666]['providers'].append(300)

    return as_relationships
