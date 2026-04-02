from welsh_powell import welsh_powell_coloring


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
        other_node_id = edge["node2_id"] if edge["node1_id"] == node_id else edge["node1_id"]
        if 0 <= other_node_id < len(app.nodes):
            app.nodes[other_node_id]["degree"] -= 1

    app.edges = kept_edges
    app.nodes.remove(node)

    if app.selected_node == node:
        app.selected_node = None
    if app.first_node_for_connection == node:
        app._clear_connection_highlight()

    app._reindex_nodes()
    app.redraw_edges()


def _edge_exists(app, node1_id, node2_id):
    return any(
        (e["node1_id"] == node1_id and e["node2_id"] == node2_id)
        or (e["node1_id"] == node2_id and e["node2_id"] == node1_id)
        for e in app.edges
    )


def connect_nodes(app, node1, node2):
    node1_id, node2_id = node1["id"], node2["id"]
    if node1_id == node2_id:
        return False, "Không thể liên kết nút với chính nó!"
    if _edge_exists(app, node1_id, node2_id):
        return False, "Cạnh này đã tồn tại!"

    app.edges.append({"node1_id": node1_id, "node2_id": node2_id, "line": None})
    node1["degree"] += 1
    node2["degree"] += 1
    app.redraw_edges()
    return True, None


def delete_edge(app, edge):
    node1 = app.nodes[edge["node1_id"]]
    node2 = app.nodes[edge["node2_id"]]
    node1["degree"] -= 1
    node2["degree"] -= 1

    if edge.get("line"):
        app.canvas.delete(edge["line"])
    app.edges.remove(edge)
    app.redraw_edges()


def apply_welsh_powell_coloring(app):
    node_colors = welsh_powell_coloring(app.nodes, app.edges)
    if not node_colors:
        return None

    max_color = max(node_colors)
    color_groups = [[] for _ in range(max_color + 1)]

    for node, color_idx in zip(app.nodes, node_colors):
        node["color"] = app._generate_color(color_idx)
        app.canvas.itemconfig(node["circle"], fill=node["color"])
        color_groups[color_idx].append(node["label"])

    return max_color, color_groups
