"""core/app_methods.py - Chứa trạng thái ứng dụng và các phương thức vẽ/zoom đồ thị."""

import math
import tkinter as tk

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
            self.view_offset_x = center_cx - center_wx * self.scale
            self.view_offset_y = center_cy - center_wy * self.scale

        self.render_graph()

    def _world_to_canvas(self, wx, wy):
        return wx * self.scale + self.view_offset_x, wy * self.scale + self.view_offset_y

    def _canvas_to_world(self, cx, cy):
        return (cx - self.view_offset_x) / self.scale, (cy - self.view_offset_y) / self.scale

    def _center_view_on_graph(self):
        if not hasattr(self, "canvas"): return
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

    @staticmethod
    def _distance_point_to_segment(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0: return math.hypot(px - x1, py - y1)
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return math.hypot(px - closest_x, py - closest_y)

    def create_node(self, x, y, label, color):
        radius = 35
        node_data = {
            "id": len(self.nodes), "x": x, "y": y, "radius": radius,
            "label": label, "color": color, "circle": None, "text": None, "degree": 0,
        }
        cx, cy = self._world_to_canvas(x, y)
        node_data["circle"] = self.canvas.create_oval(
            cx - radius * self.scale, cy - radius * self.scale,
            cx + radius * self.scale, cy + radius * self.scale,
            fill=color, outline="black", width=2,
        )
        node_data["text"] = self.canvas.create_text(cx, cy, text=label, fill="black", font=("Arial", 12, "bold"))
        self.nodes.append(node_data)

    def get_node_at(self, x, y):
        wx, wy = self._canvas_to_world(x, y)
        return next((node for node in reversed(self.nodes) if (wx - node["x"]) ** 2 + (wy - node["y"]) ** 2 <= (node["radius"] * self.scale) ** 2), None)

    def get_edge_at(self, x, y, tolerance=5):
        wx, wy = self._canvas_to_world(x, y)
        tol_sq = (tolerance / self.scale) ** 2
        for edge in self.edges:
            n1, n2 = self.nodes[edge["node1_id"]], self.nodes[edge["node2_id"]]
            if self._distance_point_to_segment(wx, wy, n1["x"], n1["y"], n2["x"], n2["y"]) ** 2 <= tol_sq:
                return edge
        return None

    def render_graph(self):
        self.canvas.delete("all")

        if self.auto_center_pending:
            self._center_view_on_graph()
            self.auto_center_pending = False

        h_path = getattr(self, "highlighted_path", [])
        h_edges_list = getattr(self, "highlighted_edges", [])
        h_color = getattr(self, "highlighted_color", "red")
        
        # KIỂM TRA ĐỒ THỊ CÓ HƯỚNG
        is_directed = getattr(self, "is_directed", None) is not None and self.is_directed.get()

        dijkstra_role_by_node_id = {}
        if getattr(self, "algorithm_mode", "") == "dijkstra":
            for idx, selected_node in enumerate(getattr(self, "dijkstra_nodes", [])[:2]):
                if selected_node is None:
                    continue
                role = "BĐ" if idx == 0 else "KT"
                dijkstra_role_by_node_id[selected_node["id"]] = role

        # ================= EDGE SET =================
        path_edges = set()
        for i in range(len(h_path) - 1):
            u, v = h_path[i], h_path[i+1]
            if is_directed:
                path_edges.add((u, v))
            else:
                path_edges.add((min(u, v), max(u, v)))

        mst_edges = set()
        for e in h_edges_list:
            mst_edges.add((min(e["node1_id"], e["node2_id"]), max(e["node1_id"], e["node2_id"])))

        # ================= DRAW EDGES =================
        for edge in self.edges:
            n1 = self.nodes[edge["node1_id"]]
            n2 = self.nodes[edge["node2_id"]]

            cx1, cy1 = self._world_to_canvas(n1["x"], n1["y"])
            cx2, cy2 = self._world_to_canvas(n2["x"], n2["y"])

            u, v = edge["node1_id"], edge["node2_id"]

            if is_directed:
                is_path_highlighted = (u, v) in path_edges
            else:
                is_path_highlighted = (min(u, v), max(u, v)) in path_edges

            is_mst_highlighted = (min(u, v), max(u, v)) in mst_edges
            is_highlighted = is_path_highlighted or is_mst_highlighted

            e_color = h_color if is_highlighted else "gray"
            e_width = 4 if is_highlighted else 2

            if is_directed:
                angle = math.atan2(cy2 - cy1, cx2 - cx1)
                radius_stop = (n2["radius"] * self.scale) + 2
                
                end_x = cx2 - radius_stop * math.cos(angle)
                end_y = cy2 - radius_stop * math.sin(angle)
                
                edge["line"] = self.canvas.create_line(
                    cx1, cy1, end_x, end_y, 
                    fill=e_color, width=e_width, 
                    tags="edge", arrow=tk.LAST, arrowshape=(15, 20, 5)
                )
            else:
                edge["line"] = self.canvas.create_line(cx1, cy1, cx2, cy2, fill=e_color, width=e_width)

            # HIỂN THỊ TRỌNG SỐ
            if edge.get("weight") is not None:
                mx, my = (cx1 + cx2) / 2, (cy1 + cy2) / 2
                self.canvas.create_rectangle(mx-10, my-10, mx+10, my+10, fill="white", outline="white")
                self.canvas.create_text(
                    mx, my,
                    text=str(edge["weight"]),
                    fill="#c0392b",
                    font=("Arial", 10, "bold")
                )

        # ================= DRAW NODES =================
        prim_start_vertex = getattr(self, "prim_start_vertex", None)
        current_row = getattr(self, "current_dijkstra_row", None)
        path_pred = getattr(self, "current_path_pred", {})
        
        for node in self.nodes:
            is_highlighted = node["id"] in h_path

            cx, cy = self._world_to_canvas(node["x"], node["y"])
            radius = node["radius"] * self.scale

            # Đổi màu viền
            if getattr(self, "algorithm_mode", "") == "dijkstra" and current_row and current_row.get("finalized_node") == node["id"]:
                outline_color = "#f39c12"
                outline_width = 4
            elif is_highlighted:
                outline_color = h_color
                outline_width = 4
            elif node["id"] == prim_start_vertex:
                outline_color = "#2980b9"
                outline_width = 4
            elif node["id"] in dijkstra_role_by_node_id:
                outline_color = "#16a085" if dijkstra_role_by_node_id[node["id"]] == "BĐ" else "#8e44ad"
                outline_width = 4
            else:
                outline_color = "black"
                outline_width = 2

            node["circle"] = self.canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                fill=node["color"],
                outline=outline_color,
                width=outline_width
            )

            node["text"] = self.canvas.create_text(
                cx, cy,
                text=node["label"],
                fill="black",
                font=("Arial", 12, "bold")
            )

            if node["id"] in dijkstra_role_by_node_id:
                role = dijkstra_role_by_node_id[node["id"]]
                badge_r = max(10, radius * 0.28)
                badge_cx = cx + radius * 0.55
                badge_cy = cy - radius * 0.55
                badge_fill = "#16a085" if role == "BĐ" else "#8e44ad"

                self.canvas.create_oval(
                    badge_cx - badge_r,
                    badge_cy - badge_r,
                    badge_cx + badge_r,
                    badge_cy + badge_r,
                    fill=badge_fill,
                    outline="white",
                    width=2,
                )
                self.canvas.create_text(
                    badge_cx,
                    badge_cy,
                    text=role,
                    fill="white",
                    font=("Arial", 10, "bold"),
                )

            # ================= VẼ NHÃN DIJKSTRA NỔI (Floating Labels) =================
            show_labels_var = getattr(self, "show_floating_labels", None)
            is_show_labels = show_labels_var.get() if show_labels_var else True

            show_done_var = getattr(self, "show_done_labels", None)
            is_show_done = show_done_var.get() if show_done_var else False

            if getattr(self, "algorithm_mode", "") == "dijkstra" and current_row and is_show_labels:
                state = current_row["states"].get(node["id"])
                if state:
                    lbl_text = ""
                    bg_color = "#ecf0f1"
                    
                    if state["status"] == "done":
                        if is_show_done:
                            history = getattr(self, "dijkstra_history_table", [])
                            for r in history:
                                if r["finalized_node"] == node["id"]:
                                    old_state = r["states"][node["id"]]
                                    dist = old_state["dist"]
                                    preds = old_state["preds"]
                                    
                                    p = None
                                    if node["id"] in path_pred and path_pred[node["id"]] in preds:
                                        p = path_pred[node["id"]]
                                    elif preds:
                                        p = preds[0]
                                        
                                    p_label = self.nodes[p]["label"] if p is not None else "-"
                                    lbl_text = "0" if (dist == 0 and not preds) else f"({dist}, {p_label})"
                                    bg_color = "#bdc3c7"
                                    break
                        else:
                            lbl_text = "-"
                            bg_color = "#bdc3c7"
                    else:
                        dist = state["dist"]
                        preds = state["preds"]
                        if dist == float('inf'):
                            lbl_text = "(∞, -)"
                        else:
                            p = None
                            if node["id"] in path_pred and path_pred[node["id"]] in preds:
                                p = path_pred[node["id"]]
                            elif preds:
                                p = preds[0]
                            p_label = self.nodes[p]["label"] if p is not None else "-"
                            lbl_text = "0" if (dist == 0 and not preds) else f"({dist}, {p_label})"
                            
                            if state["status"] == "finalizing":
                                lbl_text += "*"
                                bg_color = "#f1c40f"

                    if lbl_text:
                        lbl_x = cx
                        lbl_y = cy - radius - 18 * self.scale
                        font_size = max(8, int(10 * self.scale))
                        
                        t_id = self.canvas.create_text(lbl_x, lbl_y, text=lbl_text, fill="#2c3e50", font=("Arial", font_size, "bold"))
                        bbox = self.canvas.bbox(t_id)
                        
                        if bbox:
                            rect_id = self.canvas.create_rectangle(bbox[0]-4, bbox[1]-2, bbox[2]+4, bbox[3]+2, fill=bg_color, outline="#7f8c8d")
                            self.canvas.tag_lower(rect_id, t_id)

        if hasattr(self, "refresh_relationship_panel") and callable(self.refresh_relationship_panel):
            self.refresh_relationship_panel()