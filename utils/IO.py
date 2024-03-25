import logging

from utils.Models import Robot, Berth, Ship, Goods
from utils.Strategy import decide_robot_action, decide_ship_action, collision_detection
from utils.PriorityManager import BerthPriorityManager, GoodsPriorityManager
import sys


def remove_robots_from_map(map_data):
    # 创建一个新的地图数组，以避免修改原始地图数据
    new_map_data = [row[:] for row in map_data]

    # 遍历地图的每个位置
    for i, row in enumerate(new_map_data):
        for j, cell in enumerate(row):
            if cell == 'A':  # 如果当前位置是机器人
                new_map_data[i][j] = '.'  # 将其替换为'.'

    return new_map_data


def initialize(robot_num, berth_num, ship_num):
    # initial Game
    game = Game()
    # Parse initial data
    robots = [Robot() for _ in range(robot_num)]
    berths = [Berth() for _ in range(berth_num)]
    ships = [Ship() for _ in range(ship_num)]
    goods = []
    # 解析地图数据
    map_data = []
    for _ in range(200):  # 假设地图大小为200x200
        line = input().strip()
        map_data.append(list(line))

    # 解析泊位数据
    for _ in range(berth_num):
        id, x, y, transport_time, loading_speed = map(int, input().strip().split())
        berths[id].x = x
        berths[id].y = y
        berths[id].transport_time = transport_time
        berths[id].loading_speed = loading_speed
    # berths_sorted_by_priority = sorted(berths, key=lambda x: x.priority)

    # 解析船只容积
    capacity = int(input().strip())
    for i in range(ship_num):
        ships[i].capacity = capacity

    # 最后，确认初始化完成
    okk = input().strip()
    if okk != "OK":
        print("Initialization failed.", file=sys.stderr)

    BPM = BerthPriorityManager(robots, berths)
    GPM = GoodsPriorityManager(berths, goods)

    map_data_without_robots = remove_robots_from_map(map_data)

    print("OK")
    sys.stdout.flush()
    result = robots, goods, berths, ships, map_data, map_data_without_robots, BPM, GPM

    logging.info("Success initialize")
    return result


def process_input_frame(robots, berths, goods, ships):
    former_frame = Game().current_frame
    # 读取帧序号和当前金钱数
    Game().current_frame, current_money = map(int, input().split())

    # 根据每个berth的装载速度和每个ship的容量更新泊位和船的货物数量
    interval_frames = Game().current_frame - former_frame
    for ship in [ship for ship in ships if ship.status == 1]:
        # 假设货物的转移发生在每个时间帧
        # 计算在interval_frames时间内，该泊位可以装载的货物数量
        goods_to_load = min(interval_frames * berths[ship.berth_id].loading_speed, berths[ship.berth_id].goods_num)
        berths[ship.berth_id].goods_num -= goods_to_load
        ship.goods_num += goods_to_load

    # 更新goods    # TODO 改成一个循环？性能会提升吗？
    for good in goods:
        good.update_remaining_frame()
    goods = [good for good in goods if good.remaining_frame > 0]

    # 读取新增货物的数量
    goods_count = int(input())
    new_goods_list = []
    for _ in range(goods_count):
        # 对于每个新增货物，读取其坐标和价值
        x, y, value = map(int, input().split())
        new_goods = Goods(x, y, value, Game().current_frame)
        new_goods_list.append(new_goods)
    goods += new_goods_list

    # 读取每个机器人的状态
    for i in range(10):  # 假设总共有10个机器人
        robots[i].id = i
        robots[i].is_carry_goods, robots[i].is_normal_status, robots[i].x, robots[i].y = map(int, input().split())

    # 读取每艘船的状态
    for i in range(5):  # 假设总共有5艘船
        ships[i].status, ships[i].berth_id = map(int, input().split())

    # 确认所有数据已经读入完毕
    ok = input().strip()
    assert ok == "OK", "Input frame data is not completed!"
    logging.info("Success process_input_frame")
    return new_goods_list


def output_actions(robots, berths, ships, BPM, GPM, map_data_without_robots, new_goods_list):
    # Format and print actions
    actions = []

    # 更新泊位优先级管理器和货物优先级管理器
    logging.info("Start BPM.update, GPM.updata")
    BPM.update(map_data_without_robots)
    GPM.updata(map_data_without_robots, new_goods_list)
    logging.info("Success BPM.update, GPM.updata!\n")
    # 假设我们已经有了一个函数来为机器人计算下一个目标
    robot_actions = []
    for robot in robots:
        action = decide_robot_action(robot, BPM, GPM)
        if action:  # 返回的action是一个list！
            robot_actions.append(action)  # robot_actions是一个二维的list
    robot_actions = collision_detection(robots, robot_actions)
    actions += robot_actions

    # TODO 假设robot_actions正确执行了，更新berth.goods_num, 执行失败了怎么办？
    for action in robot_actions:
        expression, robot_id, *param = action.split()
        if expression == 'pull':
            berths[robots[robot_id].destination_berth_id].goods_num += 1
            robots[robot_id].destination_berth_id = -1  # 清楚目标

    # 同样，假设有一个函数来决定船的下一步行动
    for ship in ships:
        action = decide_ship_action(ship, berths, BPM)
        if action:
            actions.append(action)

    # 格式化并打印所有行动
    for action in actions:
        print(action)
        sys.stdout.flush()
    print("OK")
    sys.stdout.flush()

    logging.info("Success output_actions:")
    logging.info(actions)

class Game:
    _instance = None  # 类变量，用于存储单例对象

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Game, cls).__new__(cls)
            cls._instance.current_frame = 0  # 初始化实例变量
            cls._instance.game_over = False
        return cls._instance

    def update(self):
        self.current_frame += 1
        # 执行每帧的逻辑...
        print(f"Current frame: {self.current_frame}")

    def run(self):
        while True:
            self.update()
            if self.current_frame >= 15000:  # 示例退出条件
                break
