# menu.py —— 开始菜单(类似 FC 游戏的选单):选模式 -> 选地图 -> 开玩
# 用的还是 game.read_key(按键即选,不用回车)。所有地图从数据库里列出来。

import game
import db


def list_maps():
    """从数据库取所有地图,返回 [(编号, 宽, 高), ...],按编号从小到大。"""
    session = db.Session()
    rows = []
    for one_map in session.query(db.Map).order_by(db.Map.id).all():
        rows.append((one_map.id, one_map.width, one_map.height))
    session.close()
    return rows


def choose_map():
    """列出所有地图让玩家选一张。返回选中的编号;按 B 返回上一层则返回 None。
    (目前用单个数字键选,支持编号 1~9。)"""
    maps = list_maps()
    while True:
        game.clear_screen()
        print("========== 选 地 图 ==========\n")
        for (map_id, width, height) in maps:
            print("   %d    %dx%d" % (map_id, width, height))
        print("\n按数字键选地图,B 返回:")

        key = game.read_key()
        if key == "b":
            return None
        if key.isdigit():
            chosen = int(key)
            for (map_id, width, height) in maps:
                if map_id == chosen:
                    return chosen
        # 其它键(或不存在的编号)忽略,继续等


def single_game():
    """单人模式:选一张地图,一个人闯关。"""
    map_id = choose_map()
    if map_id is None:
        return                      # 玩家按了返回
    grid = db.get_map(map_id)
    game.play(grid)


def vs_game():
    """双人对战:下一步实现,先占位。"""
    game.clear_screen()
    print("双人对战(VS Mode)还没做好,马上就来!\n")
    print("按任意键返回菜单…")
    game.read_key()


def run():
    """主菜单循环:选模式。"""
    while True:
        game.clear_screen()
        print("==============================")
        print("        迷 宫 大 冒 险")
        print("==============================\n")
        print("   1    Single   单人闯关")
        print("   2    VS Mode  双人对战")
        print("   Q    退出\n")
        print("请按键选择:")

        key = game.read_key()
        if key == "q":
            print("拜拜!")
            return
        if key == "1":
            single_game()
        elif key == "2":
            vs_game()
        # 其它键忽略,重画菜单
