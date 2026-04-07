import math

def dijkstra(nodes, edges, start_node_id, end_node_id):
    """Tìm đường đi ngắn nhất giữa hai nút dựa trên khoảng cách hình học."""
    node_count = len(nodes)
    if node_count == 0: return None
    
    # Xây dựng danh sách kề với trọng số là khoảng cách x, y
    adj = {i: [] for i in range(node_count)}
    for edge in edges:
        u, v = edge["node1_id"], edge["node2_id"]
        # Tính khoảng cách Euclidean làm trọng số
        dist = math.hypot(nodes[u]["x"] - nodes[v]["x"], nodes[u]["y"] - nodes[v]["y"])
        adj[u].append((v, dist))
        adj[v].append((u, dist))

    # Khởi tạo
    distances = {i: float('inf') for i in range(node_count)}
    predecessors = {i: None for i in range(node_count)}
    distances[start_node_id] = 0
    unvisited = set(range(node_count))

    while unvisited:
        # Chọn nút có khoảng cách nhỏ nhất trong tập chưa thăm
        current = min(unvisited, key=lambda n: distances[n])
        
        if distances[current] == float('inf') or current == end_node_id:
            break
            
        unvisited.remove(current)

        for neighbor, weight in adj[current]:
            new_dist = distances[current] + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = current

    # Truy vết đường đi
    path = []
    curr = end_node_id
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]
    path.reverse()

    return path if path[0] == start_node_id else None

def dijkstra_step_by_step(nodes, edges, start_id, end_id):
    node_count = len(nodes)
    if node_count == 0: return None, []
    
    adj = {i: [] for i in range(node_count)}
    for edge in edges:
        u, v = edge["node1_id"], edge["node2_id"]
        w = edge.get("weight", 1)  # Lấy trọng số, mặc định là 1
        adj[u].append((v, w))
        adj[v].append((u, w))

    distances = {i: float('inf') for i in range(node_count)}
    predecessors = {i: None for i in range(node_count)}
    distances[start_id] = 0
    unvisited = set(range(node_count))
    steps = []

    while unvisited:
        current = min(unvisited, key=lambda n: distances[n])
        
        if distances[current] == float('inf'):
            steps.append({"type": "info", "msg": "Không thể tiếp cận các đỉnh còn lại."})
            break

        node_label = nodes[current]["label"]
        steps.append({"type": "visit", "node": current, "msg": f"[*] Đang xét nút {node_label} (k/c: {distances[current]})"})

        if current == end_id:
            steps.append({"type": "info", "msg": f"[+] Đã đến đích {node_label}!"})
            break

        unvisited.remove(current)

        for neighbor, weight in adj[current]:
            if neighbor in unvisited:
                new_dist = distances[current] + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current
                    steps.append({
                        "type": "update", "u": current, "v": neighbor, 
                        "msg": f"  -> Cập nhật {nodes[neighbor]['label']}: {new_dist}"
                    })

    # Truy vết đường đi
    path = []
    curr = end_id
    while curr is not None:
        path.append({"id": curr, "dist": distances[curr]})
        curr = predecessors[curr]
    path.reverse()

    return (path, steps) if path and path[0]["id"] == start_id else (None, steps)

"""algorithms/dijkstra.py - Chạy thuật toán Dijkstra, xuất bảng vết và đa đường đi."""

def dijkstra_table_and_paths(nodes, edges, start_id, end_id):
    node_count = len(nodes)
    if node_count == 0: return None, [], float('inf')
    
    adj = {i: [] for i in range(node_count)}
    for edge in edges:
        u, v, w = edge["node1_id"], edge["node2_id"], edge.get("weight", 1)
        adj[u].append((v, w))
        adj[v].append((u, w))

    distances = {i: float('inf') for i in range(node_count)}
    predecessors = {i: [] for i in range(node_count)}
    distances[start_id] = 0
    
    unvisited = set(range(node_count))
    finalized = set()
    history_table = []

    while unvisited:
        current = min(unvisited, key=lambda n: distances[n])
        if distances[current] == float('inf'): break
        unvisited.remove(current)

        # Trả về dữ liệu trạng thái thô để UI tự build text
        row_data = {"finalized_node": current, "states": {}}
        for i in range(node_count):
            if i in finalized:
                row_data["states"][i] = {"status": "done"}
            elif i == current:
                row_data["states"][i] = {"status": "finalizing", "dist": distances[i], "preds": list(predecessors[i])}
            else:
                row_data["states"][i] = {"status": "waiting", "dist": distances[i], "preds": list(predecessors[i])}
        
        history_table.append(row_data)
        finalized.add(current)
        if current == end_id: break

        for neighbor, weight in adj[current]:
            if neighbor in unvisited:
                new_dist = distances[current] + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = [current]
                elif new_dist == distances[neighbor]:
                    predecessors[neighbor].append(current) 

    min_dist = distances[end_id]
    if min_dist == float('inf'):
        return history_table, [], float('inf')

    all_paths = []
    def build_paths(curr_node, current_path):
        if curr_node == start_id:
            all_paths.append([start_id] + current_path[::-1])
            return
        for p in predecessors[curr_node]:
            current_path.append(curr_node)
            build_paths(p, current_path)
            current_path.pop()

    build_paths(end_id, [])
    return history_table, all_paths, min_dist