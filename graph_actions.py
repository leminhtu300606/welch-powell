from welsh_powell import welsh_powell_coloring


def _reindex_nodes(app):
    old_to_new_id = {node["id"]: i for i, node in enumerate(app.nodes)}

    for i, node in enumerate(app.nodes):
        node["id"] = i

    app.edges = [
        {**e, "node1_id": old_to_new_id[e["node1_id"]], "node2_id": old_to_new_id[e["node2_id"]]}
        for e in app.edges
        if e["node1_id"] in old_to_new_id and e["node2_id"] in old_to_new_id
    ]


def _hsl_to_hex(h, s, l):
    s, l = s / 100, l / 100
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    r, g, b = int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)
    return f"#{r:02x}{g:02x}{b:02x}"


def _generate_color(index):
    return _hsl_to_hex((index * 137.5) % 360, 70 + (index % 2) * 20, 50 + (index % 3) * 5)


def delete_node(app, node):
    node_id = node["id"]
    app.canvas.delete(node["circle"])
    app.canvas.delete(node["text"])

    kept_edges = []
    for edge in app.edges:
        if edge["node1_id"] != node_id and edge["node2_id"] != node_id:
            kept_edges.append(edge)
            continue

        if edge.get("line"):
            app.canvas.delete(edge["line"])
        other = edge["node2_id"] if edge["node1_id"] == node_id else edge["node1_id"]
        if 0 <= other < len(app.nodes):
            app.nodes[other]["degree"] -= 1

    app.edges = kept_edges
    app.nodes.remove(node)

    if app.selected_node == node:
        app.selected_node = None
    if app.first_node_for_connection == node:
        app._clear_connection_highlight()

    _reindex_nodes(app)
    app.render_graph()


def _edge_exists(app, node1_id, node2_id):
    return any({e["node1_id"], e["node2_id"]} == {node1_id, node2_id} for e in app.edges)


def connect_nodes(app, node1, node2):
    node1_id, node2_id = node1["id"], node2["id"]
    if node1_id == node2_id:
        return False, "Không thể liên kết nút với chính nó!"
    if _edge_exists(app, node1_id, node2_id):
        return False, "Cạnh này đã tồn tại!"

    app.edges.append({"node1_id": node1_id, "node2_id": node2_id, "line": None})
    node1["degree"] += 1
    node2["degree"] += 1
    app.render_graph()
    return True, None


def delete_edge(app, edge):
    node1 = app.nodes[edge["node1_id"]]
    node2 = app.nodes[edge["node2_id"]]
    node1["degree"] -= 1
    node2["degree"] -= 1

    if edge.get("line"):
        app.canvas.delete(edge["line"])
    app.edges.remove(edge)
    app.render_graph()


def apply_welsh_powell_coloring(app):
    node_colors = welsh_powell_coloring(app.nodes, app.edges)
    if not node_colors:
        return None

    max_color = max(node_colors)
    color_groups = [[] for _ in range(max_color + 1)]

    for node, color_idx in zip(app.nodes, node_colors):
        node["color"] = _generate_color(color_idx)
        app.canvas.itemconfig(node["circle"], fill=node["color"])
        color_groups[color_idx].append(node["label"])

    return max_color, color_groups
