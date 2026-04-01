import tkinter as tk
from tkinter import messagebox
from ui import setup_interface
from welsh_powell import welsh_powell_coloring

class WelshPowellApp:
    def __init__(self, root):
        self.root = root
        self.nodes = []
        self.selected_node = None
        self.drag_start = None

        self.edges = []
        self.first_node_for_connection = None

        self.scale = 1.0

        setup_interface(self)

    def _clear_connection_highlight(self):
        """Xóa highlight khỏi nút được chọn để kết nối."""
        if self.first_node_for_connection is not None:
            self.canvas.itemconfig(self.first_node_for_connection["circle"], width=2, outline="black")
            self.first_node_for_connection = None

    def _generate_color(self, index):
        """Tạo màu từ HSL color space - không giới hạn số lượng màu."""
        hue = (index * 137.5) % 360
        saturation = 70 + (index % 2) * 20
        lightness = 50 + (index % 3) * 5

        return self._hsl_to_hex(hue, saturation, lightness)
    
    def _hsl_to_hex(self, h, s, l):
        """Convert HSL color to HEX format."""
        s = s / 100
        l = l / 100
        
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
        
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def _world_to_canvas(self, wx, wy):
        """Chuyển đổi từ tọa độ thế giới sang tọa độ canvas."""
        cx = wx * self.scale
        cy = wy * self.scale
        return cx, cy

    def _canvas_to_world(self, cx, cy):
        """Chuyển đổi từ tọa độ canvas sang tọa độ thế giới."""
        wx = cx / self.scale
        wy = cy / self.scale
        return wx, wy

    def _reindex_nodes(self):
        """Giữ id nút khớp với vị trí trong danh sách để tránh lệch tham chiếu cạnh."""
        old_to_new_id = {node["id"]: i for i, node in enumerate(self.nodes)}

        for i, node in enumerate(self.nodes):
            node["id"] = i

        self.edges = [
            {**e, "node1_id": old_to_new_id[e["node1_id"]], "node2_id": old_to_new_id[e["node2_id"]]}
            for e in self.edges if e["node1_id"] in old_to_new_id and e["node2_id"] in old_to_new_id
        ]

    def create_node(self, x, y, label, color):
        """Tạo một nút hình tròn"""
        radius = 35
        node_data = {
            "id": len(self.nodes),
            "x": x, "y": y, "radius": radius,
            "label": label, "color": color,
            "circle": None, "text": None, "degree": 0
        }
        
        cx, cy = self._world_to_canvas(x, y)
        node_data["circle"] = self.canvas.create_oval(
            cx - radius * self.scale, cy - radius * self.scale,
            cx + radius * self.scale, cy + radius * self.scale,
            fill=color, outline="black", width=2
        )
        node_data["text"] = self.canvas.create_text(
            cx, cy, text=label, fill="black", font=("Arial", 12, "bold")
        )
        self.nodes.append(node_data)

    def get_node_at(self, x, y):
        """Tìm nút tại vị trí (x, y) trên canvas"""
        wx, wy = self._canvas_to_world(x, y)
        return next((node for node in reversed(self.nodes) 
                    if (wx - node["x"]) ** 2 + (wy - node["y"]) ** 2 <= (node["radius"] * self.scale) ** 2), None)

    def redraw_edges(self):
        """Vẽ lại tất cả các cạnh hiện có"""
        self.canvas.delete("all")
        
        for edge in self.edges:
            edge["line"] = None

        for edge in self.edges:
            n1 = self.nodes[edge["node1_id"]]
            n2 = self.nodes[edge["node2_id"]]
            cx1, cy1 = self._world_to_canvas(n1["x"], n1["y"])
            cx2, cy2 = self._world_to_canvas(n2["x"], n2["y"])
            edge["line"] = self.canvas.create_line(
                cx1, cy1, cx2, cy2, fill="gray", width=2, tags="edge"
            )
        
        for node in self.nodes:
            cx, cy = self._world_to_canvas(node["x"], node["y"])
            radius = node["radius"] * self.scale
            node["circle"] = self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill=node["color"], outline="black", width=2
            )
            node["text"] = self.canvas.create_text(
                cx, cy, text=node["label"], fill="black", font=("Arial", 12, "bold")
            )

    def get_edge_at(self, x, y, tolerance=5):
        """Tìm cạnh gần điểm click"""
        wx, wy = self._canvas_to_world(x, y)
        
        tol_sq = (tolerance / self.scale) ** 2
        for edge in self.edges:
            if not edge.get("line"):
                continue

            n1 = self.nodes[edge["node1_id"]]
            n2 = self.nodes[edge["node2_id"]]
            x1, y1 = n1["x"], n1["y"]
            x2, y2 = n2["x"], n2["y"]

            tolerance_world = tolerance / self.scale
            if not (min(x1, x2) - tolerance_world <= wx <= max(x1, x2) + tolerance_world and
                    min(y1, y2) - tolerance_world <= wy <= max(y1, y2) + tolerance_world):
                continue

            dx, dy = x2 - x1, y2 - y1
            dd = dx * dx + dy * dy
            if dd == 0:
                continue

            t = max(0, min(1, ((wx - x1) * dx + (wy - y1) * dy) / dd))
            closest_x, closest_y = x1 + t * dx, y1 + t * dy
            dist_sq = (wx - closest_x) ** 2 + (wy - closest_y) ** 2
            
            if dist_sq <= tol_sq:
                return edge
        return None

    def delete_node(self, node):
        """Xóa một nút"""
        self.canvas.delete(node["circle"])
        self.canvas.delete(node["text"])
        
        edges_to_remove = [e for e in self.edges if e["node1_id"] == node["id"] or e["node2_id"] == node["id"]]
        for edge in edges_to_remove:
            if edge.get("line"):
                self.canvas.delete(edge["line"])
            other_node_id = edge["node2_id"] if edge["node1_id"] == node["id"] else edge["node1_id"]
            if 0 <= other_node_id < len(self.nodes):
                self.nodes[other_node_id]["degree"] -= 1
        
        self.edges = [e for e in self.edges if e not in edges_to_remove]
        self.nodes.remove(node)

        if self.selected_node == node:
            self.selected_node = None
        if self.first_node_for_connection == node:
            self._clear_connection_highlight()

        self._reindex_nodes()
        self.redraw_edges()
        
    
    def _edge_exists(self, node1_id, node2_id):
        """Kiểm tra cạnh đã tồn tại giữa hai nút."""
        return any((e["node1_id"] == node1_id and e["node2_id"] == node2_id) or 
                   (e["node1_id"] == node2_id and e["node2_id"] == node1_id) 
                   for e in self.edges)

    def connect_nodes(self, node1, node2):
        """Liên kết hai nút"""
        if node1["id"] == node2["id"]:
            messagebox.showwarning("Lỗi", "Không thể liên kết nút với chính nó!")
        elif self._edge_exists(node1["id"], node2["id"]):
            messagebox.showwarning("Lỗi", "Cạnh này đã tồn tại!")
        else:
            self.edges.append({"node1_id": node1["id"], "node2_id": node2["id"], "line": None})
            node1["degree"] += 1
            node2["degree"] += 1
            self.redraw_edges()
    
    def delete_edge(self, edge):
        """Xóa một cạnh"""
        node1 = self.nodes[edge["node1_id"]]
        node2 = self.nodes[edge["node2_id"]]
        node1["degree"] -= 1
        node2["degree"] -= 1
        
        if edge.get("line"):
            self.canvas.delete(edge["line"])
        self.edges.remove(edge)
        self.redraw_edges()

    def welsh_powell_coloring(self):
        """Gọi hàm Welsh-Powell đã tách riêng và cập nhật giao diện."""
        node_colors = welsh_powell_coloring(self.nodes, self.edges)
        if not node_colors:
            messagebox.showwarning("Lỗi", "Không có nút nào để tô màu!")
            return

        max_color = max(node_colors)
        color_groups = [[] for _ in range(max_color + 1)]
        
        for i, color_idx in enumerate(node_colors):
            self.nodes[i]["color"] = self._generate_color(color_idx)
            self.canvas.itemconfig(self.nodes[i]["circle"], fill=self.nodes[i]["color"])
            color_groups[color_idx].append(self.nodes[i]["label"])

        result = f"Kết quả Welch-Powell:\n\nSố màu cần thiết: {max_color + 1}\n\nPhân bổ màu:\n"
        for color_idx, nodes_in_color in enumerate(color_groups):
            result += f"Màu {color_idx}: {', '.join(nodes_in_color)}\n"

        result_window = tk.Toplevel(self.root)
        result_window.title("Kết quả Tô Màu")
        result_window.geometry("400x300")
        tk.Label(result_window, text=result, justify="left", padx=10, pady=10, font=("Arial", 10)).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = WelshPowellApp(root)
    root.mainloop()
