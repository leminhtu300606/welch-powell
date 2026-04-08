"""graph_actions.py - Các thao tác nghiệp vụ trên nút/cạnh và tô màu đồ thị."""

from algorithms.welsh_powell import welsh_powell_coloring

from algorithms.prim import prim
from algorithms.kruskal import kruskal

def _reindex_nodes(app):
    old_to_new_id = {node["id"]: index for index, node in enumerate(app.nodes)}
    for new_id, node in enumerate(app.nodes):
        node["id"] = new_id

    app.edges = [
        {
            **edge,
            "node1_id": old_to_new_id[edge["node1_id"]],
            "node2_id": old_to_new_id[edge["node2_id"]],
        }
        for edge in app.edges
        if edge["node1_id"] in old_to_new_id and edge["node2_id"] in old_to_new_id
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
        node1_id, node2_id = edge["node1_id"], edge["node2_id"]
        if node_id != node1_id and node_id != node2_id:
            kept_edges.append(edge)
            continue

        if edge.get("line"):
            app.canvas.delete(edge["line"])

        other_node_id = node2_id if node1_id == node_id else node1_id
        if 0 <= other_node_id < len(app.nodes):
            app.nodes[other_node_id]["degree"] -= 1

    app.edges = kept_edges
    app.nodes.remove(node)

    if app.selected_node == node:
        app.selected_node = None
    if app.first_node_for_connection == node:
        app._clear_connection_highlight()

    _reindex_nodes(app)
    app.render_graph()


def _edge_exists(app, node1_id, node2_id):
    for edge in app.edges:
        left, right = edge["node1_id"], edge["node2_id"]
        if (left == node1_id and right == node2_id) or (left == node2_id and right == node1_id):
            return True
    return False


def connect_nodes(app, node1, node2, weight=None):
    node1_id, node2_id = node1["id"], node2["id"]
    if node1_id == node2_id:
        return False, "Không thể liên kết nút với chính nó!"
    if _edge_exists(app, node1_id, node2_id):
        return False, "Cạnh này đã tồn tại!"

    edge_data = {"node1_id": node1_id, "node2_id": node2_id, "line": None}
    if weight is not None:
        edge_data["weight"] = weight

    app.edges.append(edge_data)
    node1["degree"] += 1
    node2["degree"] += 1
    app.render_graph()
    return True, None


def delete_edge(app, edge):
    app.nodes[edge["node1_id"]]["degree"] -= 1
    app.nodes[edge["node2_id"]]["degree"] -= 1

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
    coloring_plan = []
    ordered_nodes = sorted(
        enumerate(app.nodes),
        key=lambda item: (node_colors[item[0]], -item[1]["degree"], item[0]),
    )

    for node_index, node in ordered_nodes:
        color_idx = node_colors[node_index]
        color_value = _generate_color(color_idx)
        node["color"] = color_value
        coloring_plan.append((node, color_value))
        color_groups[color_idx].append(node["label"])

    return max_color, color_groups, coloring_plan



def run_prim_algorithm(app, start_edge=None):
    mst = prim(app.nodes, app.edges, start_edge)
    if not mst:
        return None

    # convert sang edge object
    mst_edges = []
    for u, v in mst:
        for edge in app.edges:
            if (edge["node1_id"] == u and edge["node2_id"] == v) or \
               (edge["node1_id"] == v and edge["node2_id"] == u):
                mst_edges.append(edge)
                break

    app.highlighted_edges = mst_edges   # ✅ QUAN TRỌNG
    return mst_edges


def run_kruskal_algorithm(app):
    mst = kruskal(app.nodes, app.edges)
    if not mst:
        return None

    mst_edges = []
    for u, v in mst:
        for edge in app.edges:
            if (edge["node1_id"] == u and edge["node2_id"] == v) or \
               (edge["node1_id"] == v and edge["node2_id"] == u):
                mst_edges.append(edge)
                break

    app.highlighted_edges = mst_edges
    return mst_edges, app.edges   # trả thêm sorted_edges nếu cần