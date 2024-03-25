def robot_to_berth_instruction(robot_id,path):
    instructions = []
    # 生成移动指令
    for move in path:
        instructions.append(f"move {robot_id} {move}")
    # 添加到泊位的拉动指令
    instructions.append(f"pull {robot_id}")
    return instructions

def robot_to_goods_instruction(robot_id,path):
    instructions = []
    # 生成移动指令
    for move in path:
        instructions.append(f"move {robot_id} {move}")
    # 添加获取货物的指令
    instructions.append(f"get {robot_id}")
    return instructions

def ship_instruction(ship_id):
    # 生成离开泊位前往虚拟点的指令
    return f"go {ship_id}"