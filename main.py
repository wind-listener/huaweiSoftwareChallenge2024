import logging, sys
from utils.IO import initialize, process_input_frame, output_actions, Game

DEBUG = True


# 主循环
def main():
    robots, goods, berths, ships, map_data, map_data_without_robots, BPM, GPM = initialize(robot_num=10, berth_num=10,
                                                                                           ship_num=5)
    while not Game().game_over:
        new_goods_list = process_input_frame(robots, berths, goods, ships)
        output_actions(robots, berths, ships, BPM, GPM, map_data_without_robots, new_goods_list)


if __name__ == "__main__":
    # 配置日志系统，日志输出到debug.log文件
    logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
    if not DEBUG:
        # 禁用所有现有的日志记录器
        for logger_name in logging.root.manager.loggerDict:
            logging.getLogger(logger_name).disabled = True

        # 禁用根日志记录器
        logging.disable(logging.CRITICAL)
    # print("这条信息会出现在stderr，不会干扰主输出流", file=sys.stderr)
    # print("这条信息会出现在stderr，不会干扰主输出流", file=sys.stdout)

    main()
