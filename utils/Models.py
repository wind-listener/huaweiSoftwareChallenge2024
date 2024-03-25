class Robot:
    def __init__(self, id=0, startX=0, startY=0, goods=0, status=1, mbx=0, mby=0):
        self.id = id
        self.x = startX
        self.y = startY
        self.is_carry_goods = goods
        self.is_normal_status = status
        self.mbx = mbx
        self.mby = mby
        self.instructions_queue = []  # 存放路径或指令序列
        self.destination_berth_id = -1

    def add_instruction(self, instruction):
        """向指令队列中添加一条指令"""
        self.instructions_queue.append(instruction)

    def get_next_instruction(self):
        """
        获取并移除指令队列中的第一条指令，
        如果获得的是队列中的最后一条指令，则根据 self.is_carry_goods 判断添加 get 指令或者 pull 指令
        """
        instruction = []
        if self.instructions_queue:
            instruction.append(self.instructions_queue.pop(0))
            if len(self.instructions_queue) == 0:  # 如果队列中只剩下最后一条指令
                if self.is_carry_goods:
                    instruction.append(f"pull {self.id}")
                else:
                    instruction.append(f"get {self.id}")
            return instruction
        else:
            return None

    def clear_instructions(self):
        """清空指令队列"""
        self.instructions_queue.clear()


class Berth:
    def __init__(self, id=0, x=0, y=0, transport_time=1, loading_speed=0):
        self.id = id
        self.x = x
        self.y = y
        self.transport_time = transport_time
        self.loading_speed = loading_speed
        self.priority = self.loading_speed / self.transport_time  # 装载越快，运输时间越短，说明这个泊位越优质
        self.goods_num = 0  # 记录当前待转载到船上的货物数量
        self.is_available = True


class Ship:
    def __init__(self, num=0, pos=0, status=0, capacity=0):
        self.num = num
        self.berth_id = pos
        self.status = status
        self.capacity = capacity
        self.goods_num = 0  # 船当前载入的货物数量


class Goods:
    def __init__(self, x=0, y=0, value=0, created_frame=0):
        self.x = x
        self.y = y
        self.value = value
        self.created_frame = created_frame
        self.remaining_frame = 0
        self.booked = -1  # -1 表示没有机器人预定这个货物，0-9表示机器人id
        self.new_add = True  # True表示新生成的货物，update时需要考虑
        self.priority = 0

    def update_remaining_frame(self):
        from utils.IO import Game
        self.remaining_frame = 1000 - (Game().current_frame - self.created_frame)
