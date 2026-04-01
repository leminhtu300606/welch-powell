import tkinter as tk
from tkinter import messagebox
from welsh_powell import welsh_powell_coloring


def delete_node(app, node):
    app.canvas.delete(node["circle"])
    app.canvas.delete(node["text"])

    edges_to_remove = [
        e for e in app.edges if e["node1_id"] == node["id"] or e["node2_id"] == node["id"]
    ]
    for edge in edges_to_remove:
        if edge.get("line"):
            app.canvas.delete(edge["line"])
        other_node_id = edge["node2_id"] if edge["node1_id"] == node["id"] else edge["node1_id"]
        if 0 <= other_node_id < len(app.nodes):
            app.nodes[other_node_id]["degree"] -= 1

    app.edges = [e for e in app.edges if e not in edges_to_remove]
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
    if node1["id"] == node2["id"]:
        messagebox.showwarning("Lỗi", "Không thể liên kết nút với chính nó!")
    elif _edge_exists(app, node1["id"], node2["id"]):
        messagebox.showwarning("Lỗi", "Cạnh này đã tồn tại!")
    else:
        app.edges.append({"node1_id": node1["id"], "node2_id": node2["id"], "line": None})
        node1["degree"] += 1
        node2["degree"] += 1
        app.redraw_edges()


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
        messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
        return

    max_color = max(node_colors)
    color_groups = [[] for _ in range(max_color + 1)]

    for i, color_idx in enumerate(node_colors):
        app.nodes[i]["color"] = app._generate_color(color_idx)
        app.canvas.itemconfig(app.nodes[i]["circle"], fill=app.nodes[i]["color"])
        color_groups[color_idx].append(app.nodes[i]["label"])

    result = f"Kết quả Welch-Powell:\n\nSố màu cần thiết: {max_color + 1}\n\nPhân bổ màu:\n"
    for color_idx, nodes_in_color in enumerate(color_groups):
        result += f"Màu {color_idx}: {', '.join(nodes_in_color)}\n"

    result_window = tk.Toplevel(app.root)
    result_window.title("Kết quả Tô Màu")
    result_window.geometry("400x300")
    tk.Label(result_window, text=result, justify="left", padx=10, pady=10, font=("Arial", 10)).pack()
