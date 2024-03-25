import logging
from utils.Map import find_min_path_Astar


class GoodsPriorityManager:
    def __init__(self, berths, goods):
        # 因为机器人总会到berth的位置，可以根据berth的位置来更新货物的优先级表，这样只需要更新增加的货物，原来的货物优先级不需要改变
        self.berths = berths
        self.goods = goods
        self.priority_tables = {berth.id: [] for berth in berths}
        self.Manhattan_distances_tables = {berth.id: [] for berth in berths}

    def update(self, map_data, new_goods_list):
        from utils.IO import Game
        current_frame = Game().current_frame
        # 遍历每个泊位
        for berth in self.berths:
            # 获取当前泊位的货物优先级表
            current_priority_table = self.priority_tables[berth.id]
            # 遍历每个新添加的货物, 如果被预定了就不用处理
            for good in [good for good in new_goods_list if good.booked == -1]:  # 新添加的，需要更新
                new_Manhattan_distances_table = []
                Manhattan_distance = abs(berth.x - berth.x) + abs(berth.y - berth.y)
                new_Manhattan_distances_table.append((Manhattan_distance, good))
            self.Manhattan_distances_tables[berth.id] += new_Manhattan_distances_table

            # 只对Manhattan_distance前5小的good计算详细路径
            nearest_goods = sorted(self.Manhattan_distances_tables[berth.id], key=lambda x: x[0], reverse=True)[:5]
            paths = []
            for good in nearest_goods:
                path, path_length = find_min_path_Astar([berth.x, berth.y], [good.x, good.y], map_data, is_derth=False)
                if path is not None and good.remaining_frame >= path_length + 10:  # 确保存在一条路径
                    # 然后计算优先级： 价值越大、路径越短、剩余时间越短，越重要！
                    good.priority = good.value / (1 + path_length) / good.remaining_frame
                    paths.append((good.priority, path, good))
            self.priority_tables[berth.id] += paths
            self.priority_tables[berth.id].sort(key=lambda x: x[0])

    def choose_best_goods(self, berth_id):
        # 选择指定泊位最优先处理的货物
        if self.priority_tables[berth_id]:
            return self.priority_tables[berth_id][1]  # 返回优先级最高的货物路径
        else:
            return None


class BerthPriorityManager:
    def __init__(self, robots, berths):
        self.robots = robots
        self.berths = berths
        self.berths_sorted_by_priority = sorted(berths, key=lambda x: x.priority)[:5]
        self.berth_priorities = {robot.id: [] for robot in robots}

    # def update(self, map_data):
    #     for robot in self.robots:
    #         # 对每个机器人，计算到所有泊位的曼哈顿距离
    #         distances = []
    #         for berth in self.berths_sorted_by_priority:
    #             distance = abs(robot.x - berth.x) + abs(robot.y - berth.y)
    #             distances.append((distance, berth))
    #
    #         # 找到距离最近的3个优选泊位
    #         nearest_berths = sorted(distances, reverse=True, key=lambda x: x[0])[:3]
    #
    #         # 对这3个泊位，使用A*算法找到最短路径
    #         paths = []
    #         for _, berth in nearest_berths:
    #             path, path_length = find_min_path_Astar([robot.x, robot.y], [berth.x, berth.y], map_data, is_derth=True)
    #             if path is not None:  # 确保存在一条路径
    #                 paths.append((path_length, path, berth))
    #
    #         # 根据路径长度排序，确定优先级
    #         sorted_paths = sorted(paths, key=lambda x: x[0])
    #
    #         # 更新优先级表
    #         self.berth_priorities[robot.id] = [(path, berth) for _, path, berth in sorted_paths]

    def update(self, map_data):
        logging.info("开始更新机器人的泊位优先级")
        for robot in self.robots:
            # 对每个机器人，计算到所有泊位的曼哈顿距离
            distances = []
            for berth in self.berths_sorted_by_priority:
                distance = abs(robot.x - berth.x) + abs(robot.y - berth.y)
                distances.append((distance, berth))

            # 找到距离最近的3个优选泊位
            nearest_berths = sorted(distances, reverse=True, key=lambda x: x[0])[:3]

            # 对这3个泊位，使用A*算法找到最短路径
            paths = []
            for _, berth in nearest_berths:
                logging.info(f"对于berth{berth.id},使用A*算法寻路：")
                path, path_length = find_min_path_Astar([robot.x, robot.y], [berth.x, berth.y], map_data, is_derth=True)
                logging.info(f"路径长度{path_length},path：{path}")
                if path is not None:  # 确保存在一条路径
                    paths.append((path_length, path, berth))

            # 根据路径长度排序，确定优先级
            sorted_paths = sorted(paths, key=lambda x: x[0])
            logging.info(f"寻路结果：{sorted_paths}")
            # 更新优先级表
            self.berth_priorities[robot.id] = [(path, berth) for _, path, berth in sorted_paths]

            logging.debug(f"机器人 {robot.id} 的泊位优先级已更新")

        logging.info("机器人的泊位优先级更新完成")

    def choose_best_berth(self, robot):
        path, berth = self.berth_priorities[robot.id][0]
        robot.destination_berth_id = berth.id
        return path
        # 返回的应该是路径

    def choose_best_berth_for_ship(self):
        # 直接返回一个空闲的，优先级最高的泊位
        for berth in self.berths_sorted_by_priority:
            if berth.is_available:
                return berth
        return None  # TODO 这里需要什么处理吗？
