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


def record_win(map_id, steps, prompt):
    """通关后记成绩:问名字 -> 找/建玩家 -> 存进 plays 表。"""
    name = input(prompt).strip()
    if name == "":
        name = "无名氏"
    player_id = db.get_or_create_player(name)
    db.save_play(player_id, map_id, steps, True)
    print("已记录:%s 在地图 #%d 用 %d 步通关!" % (name, map_id, steps))
    print("按任意键返回菜单…")
    game.read_key()


def single_game():
    """单人模式:选一张地图,一个人闯关(玩家清单里就 1 个)。通关记成绩。"""
    map_id = choose_map()
    if map_id is None:
        return                      # 玩家按了返回
    grid = db.get_map(map_id)
    winner = game.play(grid, game.make_players(1))   # 清单里 1 个人
    if winner is not None:
        print("\n🎉 通关!你走了 %d 步。" % winner["steps"])
        record_win(map_id, winner["steps"], "输入你的名字记录成绩:")


def show_leaderboard():
    """排行榜:读 plays(交易)表,按地图分组、步数从少到多列出来。"""
    game.clear_screen()
    print("========== 排 行 榜 ==========\n")
    rows = db.leaderboard()
    if len(rows) == 0:
        print("还没有通关记录,快去 Single 玩一局!")
    else:
        current_map = None
        rank = 0
        for row in rows:
            if row["map_id"] != current_map:      # 换到新地图,标题 + 名次归零
                current_map = row["map_id"]
                rank = 0
                print("\n-- 地图 #%d --" % current_map)
            rank = rank + 1
            when = row["time"].strftime("%Y-%m-%d %H:%M")
            print("  %d. %-8s %3d 步   %s" % (rank, row["name"], row["steps"], when))
    print("\n按任意键返回…")
    game.read_key()


def vs_game():
    """双人对战:同一张图,两个人比谁先到出口(玩家清单里 2 个)。赢家记成绩。"""
    map_id = choose_map()
    if map_id is None:
        return
    grid = db.get_map(map_id)
    winner = game.play(grid, game.make_players(2))   # 清单里 2 个人
    if winner is not None:
        print("\n🏆 %s 赢了!用了 %d 步。" % (winner["label"], winner["steps"]))
        record_win(map_id, winner["steps"], "赢家输入名字记录成绩:")


def run():
    """主菜单循环:选模式。"""
    while True:
        game.clear_screen()
        print("==============================")
        print("        迷 宫 大 冒 险")
        print("==============================\n")
        print("   1    Single      单人闯关")
        print("   2    VS Mode     双人对战")
        print("   3    Leaderboard 排行榜")
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
        elif key == "3":
            show_leaderboard()
        # 其它键忽略,重画菜单
