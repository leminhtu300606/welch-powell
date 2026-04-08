import heapq
import random

def prim(nodes, edges, start_vertex=None):
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

    # Chuẩn hóa đỉnh bắt đầu. Nếu không có hoặc không hợp lệ thì chọn ngẫu nhiên.
    start_node = None
    if start_vertex is not None:
        if isinstance(start_vertex, int) and 0 <= start_vertex < n:
            start_node = start_vertex

    if start_node is None:
        start_node = random.randint(0, n - 1)

    visited = [False] * n
    min_heap = []  # (weight, from_node, to_node)

    visited[start_node] = True
    mst_edges = []

    def push_frontier(node_id):
        for w, neighbor in adj[node_id]:
            if not visited[neighbor]:
                heapq.heappush(min_heap, (w, node_id, neighbor))

    push_frontier(start_node)

    while min_heap and len(mst_edges) < n - 1:
        _weight, from_node, to_node = heapq.heappop(min_heap)

        if visited[to_node]:
            continue

        visited[to_node] = True
        mst_edges.append((from_node, to_node))
        push_frontier(to_node)

    return mst_edges