import heapq
import random

def prim(nodes, edges, start_edge=None):
    """
    Thuật toán Prim tìm cây khung nhỏ nhất (MST)
    Trả về danh sách cạnh dạng (u, v)
    """

    n = len(nodes)
    if n == 0 or not edges:
        return []

    # Tạo adjacency list
    adj = [[] for _ in range(n)]
    for e in edges:
        u = e["node1_id"]
        v = e["node2_id"]
        w = e.get("weight", 1)

        adj[u].append((w, v))
        adj[v].append((w, u))

    # Chuẩn hóa cạnh bắt đầu. Nếu không có hoặc không hợp lệ thì chọn ngẫu nhiên.
    valid_edge_pairs = {
        (min(e["node1_id"], e["node2_id"]), max(e["node1_id"], e["node2_id"]))
        for e in edges
    }

    normalized_start = None
    if start_edge is not None and len(start_edge) == 2:
        u, v = int(start_edge[0]), int(start_edge[1])
        if 0 <= u < n and 0 <= v < n and u != v:
            candidate = (min(u, v), max(u, v))
            if candidate in valid_edge_pairs:
                normalized_start = candidate

    if normalized_start is None:
        random_edge = random.choice(edges)
        normalized_start = (
            min(random_edge["node1_id"], random_edge["node2_id"]),
            max(random_edge["node1_id"], random_edge["node2_id"]),
        )

    start_u, start_v = normalized_start

    visited = [False] * n
    min_heap = []  # (weight, from_node, to_node)

    visited[start_u] = True
    visited[start_v] = True
    mst_edges = [(start_u, start_v)]

    def push_frontier(node_id):
        for w, neighbor in adj[node_id]:
            if not visited[neighbor]:
                heapq.heappush(min_heap, (w, node_id, neighbor))

    push_frontier(start_u)
    push_frontier(start_v)

    while min_heap and len(mst_edges) < n - 1:
        _weight, from_node, to_node = heapq.heappop(min_heap)

        if visited[to_node]:
            continue

        visited[to_node] = True
        mst_edges.append((from_node, to_node))
        push_frontier(to_node)

    return mst_edges