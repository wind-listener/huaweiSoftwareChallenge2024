from utils.fomatter import robot_to_berth_instruction, robot_to_goods_instruction, ship_instruction

def collision_detection(robots, robot_actions):
    current_positions = []
    for robot in robots:
        current_position = [robot.x, robot.y]
        current_positions.append(current_position)

    # 基于机器人的动作计划，计算它们的下一步位置
    next_positions = []
    delete_index = []
    for i, action in enumerate(robot_actions):
        for sigle_action in action:
            expression, robot_id, *param = sigle_action.split()
            next_position = calculate_next_position(expression, param, current_positions[robot_id])
            # 然后，检测是否会有碰撞发生
            if next_position not in next_positions:
                next_positions[robot_id] = next_position
            else:  # 会发生碰撞,从robot_actions中移除这个机器人的动作，使其本轮不执行动作,并且写回指令
                robots[robot_id].instructions_queue.insert(0, robot_actions[i][0])
                delete_index.append(i)
                break  # TODO 目前这样写可能导致死锁
    robot_actions = [value for index, value in enumerate(robot_actions) if index not in delete_index]

    # 把robot_actions转成一维的list，输出最后的结果
    final_actions = []
    for action in robot_actions:
        final_actions.extend(action)
    return final_actions


def calculate_next_position(expression, param, position):
    if expression == 'move':
        # 根据action计算下一步的位置，这里假设action对应的移动如下：
        # 0: 右移，1: 左移，2: 上移，3: 下移
        if param == 0:
            return (position[0], position[1] + 1)
        elif param == 1:
            return (position[0], position[1] - 1)
        elif param == 2:
            return (position[0] - 1, position[1])
        elif param == 3:
            return (position[0] + 1, position[1])

    elif expression == 'pull' or expression == 'get':
        return position
    else:
        raise SyntaxError(f"{expression} is illegal")


def decide_robot_action(robot, BPM, GPM):
    if robot.is_normal_status:  # 正常状态
        if not robot.instructions_queue:
            # 指令队列执行完了，表示要去寻找新的货物或者泊位
            if robot.is_carry_goods:  # 携带了货物，应该寻找泊位
                # path是由0-3的整数组成的，0 表示右移一格  1 表示左移一格  2 表示上移一格  3 表示下移一格
                path_to_berth = BPM.choose_best_berth(robot)
                robot.add_instruction(robot_to_berth_instruction(robot.id, path_to_berth))
            else:  # 没带货物，应该去找货物
                path_to_goods = GPM.choose_best_goods(robot)
                robot.add_instruction(robot_to_goods_instruction(robot.id, path_to_goods))
        # 执行指令 #TODO 如何检查上一条指令的执行效果？
        return robot.get_next_instruction()
    else:
        return None


def decide_ship_action(ship, berths, BPM):
    # 如果船在泊位并且装载了货物，决定离开
    # 游戏快要结束时，最后运输一次
    from utils.IO import Game
    is_last_trans = 15000 - Game().current_frame <= berths[ship.berth_id].transport_time + 2
    if ship.status == 1:  # 表示正常运行状态(即装货状态或运输完成状态)
        if ship.goods_num >= ship.capacity or is_last_trans:
            ship.goods_num = 0  # 清空船的货物
            berths[ship.berth_id].is_available = True
            return f"go {ship.id}"
        if ship.berth_id == -1:  # 要去寻找目标泊位了
            berth = BPM.choose_best_berth_for_ship()
            berth.is_available = False
            return f"ship {ship.id}, {berth.id}"
    return None
