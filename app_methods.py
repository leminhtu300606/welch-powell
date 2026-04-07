"""app_methods.py - Chứa trạng thái ứng dụng và các phương thức vẽ/zoom đồ thị."""

import math


class AppMethods:
    def init_state(self):
        self.nodes, self.edges = [], []
        self.selected_node = self.drag_start = self.first_node_for_connection = None
        self.scale = 1.0
        self.view_offset_x = 0.0
        self.view_offset_y = 0.0
        self.auto_center_pending = True
        self.is_panning = False

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
        has_canvas = hasattr(self, "canvas")
        if has_canvas:
            center_cx, center_cy = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
            center_wx, center_wy = self._canvas_to_world(center_cx, center_cy)
        else:
            center_cx = center_cy = center_wx = center_wy = 0

        self.scale = max(0.1, self.scale * factor)

        if has_canvas:
            # Giữ tâm khung nhìn ổn định khi zoom.
            self.view_offset_x = center_cx - center_wx * self.scale
            self.view_offset_y = center_cy - center_wy * self.scale

        self.render_graph()

    def _world_to_canvas(self, wx, wy):
        """Chuyển đổi từ tọa độ thế giới sang tọa độ canvas."""
        return wx * self.scale + self.view_offset_x, wy * self.scale + self.view_offset_y

    def _canvas_to_world(self, cx, cy):
        """Chuyển đổi từ tọa độ canvas sang tọa độ thế giới."""
        return (cx - self.view_offset_x) / self.scale, (cy - self.view_offset_y) / self.scale

    def _center_view_on_graph(self):
        """Canh giữa đồ thị một lần để đảm bảo nhìn thấy các nút khi khởi tạo/tải file."""
        if not hasattr(self, "canvas"):
            return

        canvas_w = max(1, self.canvas.winfo_width())
        canvas_h = max(1, self.canvas.winfo_height())

        if not self.nodes:
            self.view_offset_x = canvas_w / 2
            self.view_offset_y = canvas_h / 2
            return

        min_x = min(node["x"] - node["radius"] for node in self.nodes)
        max_x = max(node["x"] + node["radius"] for node in self.nodes)
        min_y = min(node["y"] - node["radius"] for node in self.nodes)
        max_y = max(node["y"] + node["radius"] for node in self.nodes)

        graph_center_x = ((min_x + max_x) / 2) * self.scale
        graph_center_y = ((min_y + max_y) / 2) * self.scale

        self.view_offset_x = canvas_w / 2 - graph_center_x
        self.view_offset_y = canvas_h / 2 - graph_center_y

    def _edge_control_point(self, n1, n2):
        """Tính điểm điều khiển cho cạnh cong để giảm chồng lấn."""
        x1, y1 = n1["x"], n1["y"]
        x2, y2 = n2["x"], n2["y"]
        dx, dy = x2 - x1, y2 - y1
        distance = math.hypot(dx, dy)

        if distance == 0:
            return x1, y1

        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        perp_x, perp_y = -dy / distance, dx / distance

        pair_key = (min(n1["id"], n2["id"]), max(n1["id"], n2["id"]))
        direction = 1 if (pair_key[0] + pair_key[1]) % 2 == 0 else -1
        offset = max(18, min(60, distance * 0.12)) * direction

        return mid_x + perp_x * offset, mid_y + perp_y * offset

    def _edge_curve_points(self, n1, n2, steps=24):
        """Sinh các điểm xấp xỉ của đường cong để vẽ và phát hiện click."""
        x1, y1 = n1["x"], n1["y"]
        cx, cy = self._edge_control_point(n1, n2)
        x2, y2 = n2["x"], n2["y"]

        points = []
        for i in range(steps + 1):
            t = i / steps
            one_minus_t = 1 - t
            x = one_minus_t * one_minus_t * x1 + 2 * one_minus_t * t * cx + t * t * x2
            y = one_minus_t * one_minus_t * y1 + 2 * one_minus_t * t * cy + t * t * y2
            points.append((x, y))
        return points

    def _curve_world_to_canvas_points(self, n1, n2, steps=24):
        """Chuyển danh sách điểm đường cong (world) sang chuỗi tọa độ canvas."""
        canvas_points = []
        for x, y in self._edge_curve_points(n1, n2, steps=steps):
            cx, cy = self._world_to_canvas(x, y)
            canvas_points.extend((cx, cy))
        return canvas_points

    @staticmethod
    def _distance_point_to_segment(px, py, x1, y1, x2, y2):
        """Khoảng cách từ điểm đến đoạn thẳng."""
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)

        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return math.hypot(px - closest_x, py - closest_y)

    def animate_edge_connection(self, edge, duration_ms=220, steps=12):
        """Animate drawing of a newly connected edge."""
        if not self.edges:
            return

        n1 = self.nodes[edge["node1_id"]]
        n2 = self.nodes[edge["node2_id"]]
        canvas_points = self._curve_world_to_canvas_points(n1, n2, steps=max(24, steps * 2))

        if len(canvas_points) < 4:
            return

        line = self.canvas.create_line(
            canvas_points[0],
            canvas_points[1],
            canvas_points[2],
            canvas_points[3],
            fill="gray",
            width=2,
            tags="edge",
            smooth=True,
            splinesteps=24,
        )
        edge["line"] = line

        frame_delay = max(1, duration_ms // steps)

        def step(i=2):
            if line not in self.canvas.find_all():
                return

            coords = canvas_points[: i + 2]
            if len(coords) >= 4:
                self.canvas.coords(line, *coords)

            if i < len(canvas_points) - 2:
                self.root.after(frame_delay, lambda: step(i + 2))
            else:
                self.canvas.coords(line, *canvas_points)

        step()

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
        if self.auto_center_pending:
            self._center_view_on_graph()
            self.auto_center_pending = False

        for edge in self.edges:
            edge["line"] = None

        for edge in self.edges:
            n1, n2 = self.nodes[edge["node1_id"]], self.nodes[edge["node2_id"]]
            canvas_points = self._curve_world_to_canvas_points(n1, n2)
            edge["line"] = self.canvas.create_line(
                *canvas_points,
                fill="gray",
                width=2,
                tags="edge",
                smooth=True,
                splinesteps=24,
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

        if hasattr(self, "refresh_relationship_panel") and callable(self.refresh_relationship_panel):
            self.refresh_relationship_panel()

    def get_edge_at(self, x, y, tolerance=5):
        """Tìm cạnh gần điểm click"""
        wx, wy = self._canvas_to_world(x, y)

        tol_sq = (tolerance / self.scale) ** 2
        for edge in self.edges:
            if not edge.get("line"):
                continue

            n1 = self.nodes[edge["node1_id"]]
            n2 = self.nodes[edge["node2_id"]]
            curve_points = self._edge_curve_points(n1, n2, steps=20)
            for start, end in zip(curve_points, curve_points[1:]):
                if self._distance_point_to_segment(wx, wy, start[0], start[1], end[0], end[1]) ** 2 <= tol_sq:
                    return edge
        return None
