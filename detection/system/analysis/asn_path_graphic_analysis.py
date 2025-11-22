def asn_path_graphic_analysis(G, as_relationships):
    # Edge styles and labels
    edge_colors = []
    edge_styles = []
    edge_labels = {}
    error_nodes = []

    # w = previous u, so on next iteration:
    # w <-- u; u <-- v
    w = None
    prev_v = None
    is_valley_free = False

    for u, v in G.edges():
        print(w, u, v)

        # we must 3 nodes (w, u, v) to analyze valley free
        if not w:
            w = u
            prev_v = v
            continue

        if is_valley_free:
            error_nodes.append(w)
            is_valley_free = False
            edge_colors.append('red')
            edge_styles.append('dashed')
            edge_labels[(w, prev_v)] = 'C2P'
            w = u
            prev_v = v
            continue

        # case of valid C2P route:
        # w --> (C2P) --> u --> (P2P) --> v
        if u in as_relationships[w]['providers'] and v in as_relationships[u]['other_peers']:
            edge_colors.append('green')
            edge_styles.append('solid')
            edge_labels[(w, u)] = 'C2P'
            w = u
            prev_v = v
            continue

        # case of valid C2P route:
        # w --> (C2P) --> u --> (C2P) --> v
        if u in as_relationships[w]['providers'] and v in as_relationships[u]['providers']:
            edge_colors.append('green')
            edge_styles.append('solid')
            edge_labels[(w, u)] = 'C2P'
            w = u
            prev_v = v
            continue

        # case of valid P2C route:
        # w --> (P2C) --> u --> (P2C) --> v
        if u in as_relationships[w]['customers'] and v in as_relationships[u]['customers']:
            edge_colors.append('green')
            edge_styles.append('solid')
            edge_labels[(w, u)] = 'P2C'

            w = u
            prev_v = v
            continue

        # case of valid P2C route:
        # w --> (P2C) --> u --> (P2P) --> v
        if u in as_relationships[w]['customers'] and v in as_relationships[u]['other_peers']:
            edge_colors.append('green')
            edge_styles.append('solid')
            edge_labels[(w, u)] = 'P2C'

            w = u
            prev_v = v
            continue

        # case of valid C2P --> P2C route:
        # w --> (C2P) --> u --> (P2C) --> v
        if w in as_relationships[u]['customers'] and v in as_relationships[u]['customers']:
            edge_colors.append('green')
            edge_styles.append('solid')
            edge_labels[(w, u)] = 'C2P'

            w = u
            prev_v = v
            continue

        # case of valid P2P route:
        # w --> (P2P) --> u --> (P2P) --> v
        if w in as_relationships[u]['other_peers'] and v in as_relationships[u]['other_peers']:
            edge_colors.append('blue')
            edge_styles.append('solid')

            w = u
            prev_v = v
            continue

        # case of valley free route:
        # w --> (P2C) --> u --> (C2P) --> v
        if w in as_relationships[u]['providers'] and v in as_relationships[u]['providers']:
            is_valley_free = True
            edge_colors.append('red')
            edge_styles.append('dashed')
            edge_labels[(w, u)] = 'P2C'

            w = u
            prev_v = v
            continue

        # default (Unknown AS-relationship)
        edge_colors.append('blue')
        edge_styles.append('dotted')
        edge_labels[(u, v)] = '?'
        prev_v = v
        w = u

    # handle potentially last node (kind of ugly, still working ... /:)
    if is_valley_free:
        error_nodes.append(w)
        edge_colors.append('red')
        edge_styles.append('dashed')
        edge_labels[(w, prev_v)] = 'C2P'

    if not is_valley_free:
        edge_colors.append('green')
        edge_styles.append('solid')
        edge_labels[(w, prev_v)] = 'P2C'

    return edge_colors, edge_styles, edge_labels, error_nodes