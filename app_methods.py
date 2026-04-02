class AppMethods:
    def init_state(self):
        self.nodes, self.edges = [], []
        self.selected_node = self.drag_start = self.first_node_for_connection = None
        self.scale = 1.0

    def _clear_connection_highlight(self):
        """Xóa highlight khỏi nút được chọn để kết nối."""
        if self.first_node_for_connection is not None:
            self.canvas.itemconfig(self.first_node_for_connection["circle"], width=2, outline="black")
            self.first_node_for_connection = None

    def zoom_in(self, factor=1.2):
        self._apply_zoom(factor)

    def zoom_out(self, factor=1.2):
        self._apply_zoom(1 / factor)

    def _apply_zoom(self, factor):
        self.scale = max(0.1, self.scale * factor)
        self.render_graph()

    def _world_to_canvas(self, wx, wy):
        """Chuyển đổi từ tọa độ thế giới sang tọa độ canvas."""
        return wx * self.scale, wy * self.scale

    def _canvas_to_world(self, cx, cy):
        """Chuyển đổi từ tọa độ canvas sang tọa độ thế giới."""
        return cx / self.scale, cy / self.scale

    def create_node(self, x, y, label, color):
        """Tạo một nút hình tròn"""
        radius = 35
        node_data = {
            "id": len(self.nodes),
            "x": x,
            "y": y,
            "radius": radius,
            "label": label,
            "color": color,
            "circle": None,
            "text": None,
            "degree": 0,
        }

        cx, cy = self._world_to_canvas(x, y)
        node_data["circle"] = self.canvas.create_oval(
            cx - radius * self.scale,
            cy - radius * self.scale,
            cx + radius * self.scale,
            cy + radius * self.scale,
            fill=color,
            outline="black",
            width=2,
        )
        node_data["text"] = self.canvas.create_text(
            cx,
            cy,
            text=label,
            fill="black",
            font=("Arial", 12, "bold"),
        )
        self.nodes.append(node_data)

    def get_node_at(self, x, y):
        """Tìm nút tại vị trí (x, y) trên canvas"""
        wx, wy = self._canvas_to_world(x, y)
        return next(
            (
                node
                for node in reversed(self.nodes)
                if (wx - node["x"]) ** 2 + (wy - node["y"]) ** 2
                <= (node["radius"] * self.scale) ** 2
            ),
            None,
        )

    def render_graph(self):
        """Vẽ lại toàn bộ đồ thị (cạnh và nút)"""
        self.canvas.delete("all")

        for edge in self.edges:
            edge["line"] = None

        for edge in self.edges:
            n1 = self.nodes[edge["node1_id"]]
            n2 = self.nodes[edge["node2_id"]]
            cx1, cy1 = self._world_to_canvas(n1["x"], n1["y"])
            cx2, cy2 = self._world_to_canvas(n2["x"], n2["y"])
            edge["line"] = self.canvas.create_line(
                cx1,
                cy1,
                cx2,
                cy2,
                fill="gray",
                width=2,
                tags="edge",
            )

        for node in self.nodes:
            cx, cy = self._world_to_canvas(node["x"], node["y"])
            radius = node["radius"] * self.scale
            node["circle"] = self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill=node["color"],
                outline="black",
                width=2,
            )
            node["text"] = self.canvas.create_text(
                cx,
                cy,
                text=node["label"],
                fill="black",
                font=("Arial", 12, "bold"),
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
            if not (
                min(x1, x2) - tolerance_world <= wx <= max(x1, x2) + tolerance_world
                and min(y1, y2) - tolerance_world <= wy <= max(y1, y2) + tolerance_world
            ):
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
