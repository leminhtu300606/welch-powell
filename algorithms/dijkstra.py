"""algorithms/dijkstra.py - Chạy thuật toán Dijkstra, xuất bảng vết và đa đường đi."""

def dijkstra_table_and_paths(nodes, edges, start_id, end_id, is_directed=False):
    node_count = len(nodes)
    if node_count == 0: return None, [], float('inf')
    
    adj = {i: [] for i in range(node_count)}
    for edge in edges:
        u, v, w = edge["node1_id"], edge["node2_id"], edge.get("weight", 1)
        adj[u].append((v, w))
        # Nếu là đồ thị vô hướng, thêm chiều ngược lại v -> u
        if not is_directed:
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