"""
file_manager.py - Xử lý lưu và tải file
Cho phép người dùng lưu và tải trạng thái đồ thị từ file
"""

import html
import json
import os
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox


def _collect_graph_data(app):
    """Thu thập dữ liệu đồ thị có thể serialize."""
    return {
        "scale": app.scale,
        "nodes": [
            {
                "id": node["id"],
                "x": node["x"],
                "y": node["y"],
                "radius": node["radius"],
                "label": node["label"],
                "color": node["color"],
                "degree": node["degree"],
            }
            for node in app.nodes
        ],
        "edges": [
            {
                "node1_id": edge["node1_id"],
                "node2_id": edge["node2_id"],
            }
            for edge in app.edges
        ],
    }


def _graph_data_to_svg(graph_data):
    """Tạo SVG để người dùng mở trực tiếp như một file hình, có nhúng dữ liệu để load lại."""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if nodes:
        min_x = min(node["x"] - node.get("radius", 35) for node in nodes) - 40
        min_y = min(node["y"] - node.get("radius", 35) for node in nodes) - 40
        max_x = max(node["x"] + node.get("radius", 35) for node in nodes) + 40
        max_y = max(node["y"] + node.get("radius", 35) for node in nodes) + 40
    else:
        min_x, min_y, max_x, max_y = 0, 0, 1000, 700

    width = max(300, int(max_x - min_x))
    height = max(220, int(max_y - min_y))
    view_box = f"{int(min_x)} {int(min_y)} {width} {height}"

    node_by_id = {node["id"]: node for node in nodes}
    graph_json = json.dumps(graph_data, ensure_ascii=False)

    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{view_box}">',
        '  <defs>',
        '    <style>',
        '      .node-label { font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; dominant-baseline: middle; }',
        '      .edge { stroke: #2c3e50; stroke-width: 2; }',
        '      .node { stroke: #111; stroke-width: 2; }',
        '    </style>',
        '  </defs>',
        f'  <metadata id="graph-data"><![CDATA[{graph_json}]]></metadata>',
        '  <rect x="-10000" y="-10000" width="20000" height="20000" fill="#d6ecff"/>',
        '  <g id="edges">',
    ]

    for edge in edges:
        node1 = node_by_id.get(edge.get("node1_id"))
        node2 = node_by_id.get(edge.get("node2_id"))
        if not node1 or not node2:
            continue
        svg_lines.append(
            f'    <line class="edge" x1="{node1["x"]}" y1="{node1["y"]}" x2="{node2["x"]}" y2="{node2["y"]}" />'
        )

    svg_lines.extend([
        '  </g>',
        '  <g id="nodes">',
    ])

    for node in nodes:
        label = html.escape(str(node.get("label", "")))
        color = html.escape(str(node.get("color", "#3498db")))
        radius = node.get("radius", 35)
        svg_lines.append(
            f'    <circle class="node" cx="{node["x"]}" cy="{node["y"]}" r="{radius}" fill="{color}" />'
        )
        svg_lines.append(
            f'    <text class="node-label" x="{node["x"]}" y="{node["y"]}">{label}</text>'
        )

    svg_lines.extend([
        '  </g>',
        '</svg>',
    ])

    return "\n".join(svg_lines)


def _extract_graph_data_from_svg(file_path):
    """Đọc JSON đã nhúng trong thẻ metadata của SVG."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    metadata_text = None
    for element in root.iter():
        tag_name = element.tag.split("}")[-1]
        if tag_name == "metadata" and element.attrib.get("id") == "graph-data":
            metadata_text = element.text
            break

    if not metadata_text:
        raise ValueError("Không tìm thấy dữ liệu đồ thị nhúng trong file SVG.")

    return json.loads(metadata_text)


def _apply_graph_data(app, graph_data):
    """Khôi phục graph_data vào trạng thái app hiện tại."""
    app.init_state()

    if "scale" in graph_data:
        app.scale = graph_data["scale"]

    if "nodes" in graph_data:
        for node_data in graph_data["nodes"]:
            app.create_node(
                x=node_data["x"],
                y=node_data["y"],
                label=node_data["label"],
                color=node_data["color"],
            )
            if app.nodes:
                app.nodes[-1]["degree"] = node_data.get("degree", 0)

    if "edges" in graph_data:
        for edge_data in graph_data["edges"]:
            edge = {
                "node1_id": edge_data["node1_id"],
                "node2_id": edge_data["node2_id"],
                "line": None,
            }
            app.edges.append(edge)

    app.render_graph()


def save_graph_to_file(app, file_path=None):
    """Lưu trạng thái đồ thị ra file SVG có nhúng dữ liệu để tải lại."""
    current_file_path = getattr(app, "current_file_path", None)

    if file_path is None and current_file_path:
        should_save = messagebox.askyesno(
            "Xác nhận lưu",
            f"File hiện tại đã được mở trước đó.\nBạn có muốn lưu thay đổi vào:\n{os.path.basename(current_file_path)} không?",
        )
        if not should_save:
            return False
        file_path = current_file_path

    if file_path is None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(__file__)) or ".",
        )
    
    if not file_path:
        return False
    
    try:
        graph_data = _collect_graph_data(app)
        if not file_path.lower().endswith(".svg"):
            file_path = f"{file_path}.svg"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(_graph_data_to_svg(graph_data))

        app.current_file_path = file_path

        messagebox.showinfo("Thành công", f"Đã lưu đồ thị vào: {os.path.basename(file_path)}")
        return True
 
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")
        return False


def load_graph_from_file(app, file_path=None):
    """Tải trạng thái đồ thị từ file SVG đã lưu trước đó."""
    if file_path is None:
        file_path = filedialog.askopenfilename(
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(__file__)) or ".",
        )
    
    if not file_path:
        return False

    if not file_path.lower().endswith(".svg"):
        messagebox.showerror("Lỗi", "Vui lòng chọn file .svg được tạo từ ứng dụng.")
        return False
    
    try:
        graph_data = _extract_graph_data_from_svg(file_path)

        _apply_graph_data(app, graph_data)
        app.current_file_path = file_path

        messagebox.showinfo("Thành công", f"Đã tải đồ thị từ: {os.path.basename(file_path)}")
        return True
 
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể tải file: {str(e)}")
        return False
