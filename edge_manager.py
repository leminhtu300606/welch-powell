from tkinter import messagebox

class EdgeManager:
    def redraw_edges(self):
        """Vẽ lại tất cả cạnh"""
        for edge in self.edges:
            if "line" in edge:
                self.canvas.delete(edge["line"])

        for edge in self.edges:
            n1, n2 = self.nodes[edge["node1_id"]], self.nodes[edge["node2_id"]]
            edge["line"] = self.canvas.create_line(
                n1["x"], n1["y"], n2["x"], n2["y"], fill="gray", width=2
            )

    def get_edge_at(self, x, y, tolerance=5):
        """Tìm cạnh gần vị trí"""
        tol_sq = tolerance ** 2

        for edge in self.edges:
            if "line" not in edge:
                continue

            n1, n2 = self.nodes[edge["node1_id"]], self.nodes[edge["node2_id"]]
            x1, y1, x2, y2 = n1["x"], n1["y"], n2["x"], n2["y"]

            if not (min(x1, x2) - tolerance <= x <= max(x1, x2) + tolerance and
                    min(y1, y2) - tolerance <= y <= max(y1, y2) + tolerance):
                continue

            dx, dy = x2 - x1, y2 - y1
            dd = dx * dx + dy * dy
            if dd == 0:
                continue

            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / dd))
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy

            dist_sq = (x - closest_x) ** 2 + (y - closest_y) ** 2
            if dist_sq <= tol_sq:
                return edge

        return None

    def connect_nodes(self, node1, node2):
        """Tạo cạnh mới nếu chưa tồn tại"""
        if node1["id"] == node2["id"]:
            messagebox.showwarning("Lỗi", "Không thể liên kết nút với chính nó!")
            return

        n1_id, n2_id = node1["id"], node2["id"]
        if any((e["node1_id"] == n1_id and e["node2_id"] == n2_id) or
               (e["node1_id"] == n2_id and e["node2_id"] == n1_id) for e in self.edges):
            messagebox.showwarning("Lỗi", "Cạnh này đã tồn tại!")
            return

        self.edges.append({"node1_id": n1_id, "node2_id": n2_id, "line": None})
        self.nodes[n1_id]["degree"] += 1
        self.nodes[n2_id]["degree"] += 1
        self.redraw_edges()

    def delete_edge(self, edge):
        node1 = self.nodes[edge["node1_id"]]
        node2 = self.nodes[edge["node2_id"]]
        node1["degree"] -= 1
        node2["degree"] -= 1
        self.edges.remove(edge)
        self.redraw_edges()