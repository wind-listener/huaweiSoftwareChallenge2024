import logging
from collections import deque


def is_valid_move(x, y, map_data):
    # 检查坐标是否在地图范围内，并且不是障碍物或海洋
    return 0 <= x < len(map_data) and 0 <= y < len(map_data[0]) and map_data[x][y] == '.'


# def get_neighbors(x, y):
#     # 返回上下左右四个方向的坐标
#     return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
#
#
# def find_min_path(start, end, map_data):
#     # 使用广度优先搜索找到最短路径
#     queue = deque([(start, [start])])  # 存储坐标和到该点的路径
#     visited = set([start])  # 记录已访问的坐标
#
#     while queue:
#         (x, y), path = queue.popleft()
#
#         # 如果到达终点，返回路径
#         if (x, y) == end:
#             return path
#
#         # 遍历所有可能的移动
#         for nx, ny in get_neighbors(x, y):
#             if is_valid_move(nx, ny, map_data) and (nx, ny) not in visited:
#                 visited.add((nx, ny))
#                 queue.append(((nx, ny), path + [(nx, ny)]))
#
#     # 如果没有找到路径，返回空列表
#     return []


class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # 从起点到当前点的成本
        self.h = 0  # 启发式成本
        self.f = 0  # 总成本
        self.move = 0

    def __eq__(self, other):
        return self.position == other.position


def heuristic(a, b):
    # 使用曼哈顿距离作为启发式函数
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(node, map_data):
    neighbors = []
    directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # 右 左 上 下
    for idx, direction in enumerate(directions):
        neighbor_pos = (node.position[0] + direction[0], node.position[1] + direction[1])
        if 0 <= neighbor_pos[0] < len(map_data) and 0 <= neighbor_pos[1] < len(map_data[0]) and \
                map_data[neighbor_pos[0]][neighbor_pos[1]] == '.':
            new_node = Node(neighbor_pos, node)
            new_node.move = idx  # 存储移动方向
            neighbors.append(new_node)
    return neighbors

def find_min_path_Astar(start, end, map_data, is_derth=False):
    def is_within_rectangle(current_position, end_position):
        # 获取矩形左上角顶点的坐标
        rect_top_left_x, rect_top_left_y = end_position

        # 计算矩形的右下角顶点的坐标
        rect_bottom_right_x = rect_top_left_x + 3
        rect_bottom_right_y = rect_top_left_y + 3

        # 检查当前位置是否在矩形范围内
        if rect_top_left_x <= current_position[0] <= rect_bottom_right_x and \
                rect_top_left_y <= current_position[1] <= rect_bottom_right_y:
            return True
        else:
            return False

    start_node = Node(start)
    end_node = Node(end)

    open_list = []
    closed_list = []

    open_list.append(start_node)

    logging.info("1")

    while open_list:
        current_node = min(open_list, key=lambda o: o.f)
        open_list.remove(current_node)
        closed_list.append(current_node)
        #  对于derth而言，只要是范围内就算寻找成功
        if (current_node == end_node and not is_derth) or (
                is_within_rectangle(current_node.position, end_node.position) and is_derth):
            moves = []
            path_length = current_node.g  # 路径长度
            while current_node and current_node.parent:
                moves.append(current_node.move)
                current_node = current_node.parent
            return moves[::-1], path_length  # 返回反转的移动指令列表和路径长度

        logging.info("2")

        neighbors = get_neighbors(current_node, map_data)
        logging.info(f"{neighbors}")
        for neighbor in neighbors:
            if neighbor in closed_list:
                continue

            neighbor.g = current_node.g + 1
            neighbor.h = heuristic(neighbor.position, end_node.position)
            neighbor.f = neighbor.g + neighbor.h

            logging.info("neighbor.f = neighbor.g + neighbor.h")

            if any(open_node.position == neighbor.position for open_node in open_list):
                existing_node = next(open_node for open_node in open_list if open_node.position == neighbor.position)
                if neighbor.g > existing_node.g:
                    continue

            open_list.append(neighbor)

    return None, 0  # 如果没有路径，则返回None和路径长度0
