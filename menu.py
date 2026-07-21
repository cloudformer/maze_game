# menu.py —— 开始菜单(类似 FC 游戏的选单):选模式 -> 选地图 -> 开玩
# 按键即选,不用回车。地图从数据库列出;每一局(人或 bot)都会存进 plays,可回放。

import game
import db
import bots
import arena
import replay
import config


def list_maps():
    """从数据库取所有地图,返回 [(编号, 宽, 高), ...],按编号从小到大。"""
    session = db.Session()
    rows = []
    for one_map in session.query(db.Map).order_by(db.Map.id).all():
        rows.append((one_map.id, one_map.width, one_map.height))
    session.close()
    return rows


def choose_map():
    """列出所有地图让玩家选一张。返回选中的编号;按 B 返回则返回 None。
    (用单个数字键选,支持编号 1~9。)"""
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


def choose_speed():
    """选回放倍速,返回每帧停顿(秒)= BOT_STEP_DELAY / 倍数。"""
    game.clear_screen()
    print("========== 选 倍 速 ==========\n")
    print("   1    正常 (1x)")
    print("   2    2 倍速")
    print("   3    5 倍速")
    print("   4    10 倍速\n")
    print("按键选择:")
    factor = {"1": 1, "2": 2, "3": 5, "4": 10}.get(game.read_key(), 1)
    return config.BOT_STEP_DELAY / factor


def single_game():
    """单人:选图闯关。走完(通关或中途退)都把这局存进 plays。"""
    map_id = choose_map()
    if map_id is None:
        return
    grid = db.get_map(map_id)
    players = game.make_players(1)
    winner = game.play(grid, players)
    me = players[0]
    if winner is None:                          # 没通关:不记名、不进榜(街机规矩)
        print("\n没走到终点,下次加油!按任意键返回…")
        game.read_key()
        return
    # 通关了才让你输名字 —— 有名字 = 通关
    print("\n🎉 通关!你走了 %d 步。" % len(me["path"]))
    name = input("输入名字:").strip() or "无名氏"
    db.save_play(name, map_id, me["path"], me["symbol"])
    print("已记录!按任意键返回…")
    game.read_key()


def vs_game():
    """双人对战:同图比谁先到出口。两个人的轨迹都存进 plays。"""
    map_id = choose_map()
    if map_id is None:
        return
    grid = db.get_map(map_id)
    players = game.make_players(2)
    winner = game.play(grid, players)
    if winner is None:                           # 没人到终点:不记
        print("\n没人到终点。按任意键返回…")
        game.read_key()
        return
    # 只有赢家(先到出口)通关,让赢家输名字并记录
    print("\n🏆 %s 赢了!用了 %d 步。" % (winner["label"], len(winner["path"])))
    name = input("赢家输入名字:").strip() or winner["label"]
    db.save_play(name, map_id, winner["path"], winner["symbol"])
    print("已记录!按任意键返回…")
    game.read_key()


def arena_game():
    """机器人比赛(实时):选图,几个 bot 各跑一遍,每局存进 plays,再排名。"""
    map_id = choose_map()
    if map_id is None:
        return
    grid = db.get_map(map_id)
    bot_list = [bots.Sample1(), bots.Sample2()]   # 参赛名单(列表)
    max_steps = len(grid) * len(grid[0]) * 5
    arena.run(grid, map_id, bot_list, config.BOT_STEP_DELAY, max_steps)


def replay_game():
    """看录像:选一张图,把这张图上所有 play 一起回放(可对比)。可选倍速。"""
    map_id = choose_map()
    if map_id is None:
        return
    play_ids = db.play_ids_on_map(map_id)
    if len(play_ids) == 0:
        game.clear_screen()
        print("这张图还没有录像,先玩一局或让 bot 比一场吧。")
        print("按任意键返回…")
        game.read_key()
        return
    delay = choose_speed()
    replay.replay(play_ids, delay)


def show_leaderboard():
    """排行榜:读 plays,按地图分组、步数(=len(path))从少到多列出来。"""
    game.clear_screen()
    print("========== 排 行 榜 ==========\n")
    rows = db.leaderboard()
    if len(rows) == 0:
        print("还没有记录,快去玩一局!")
    else:
        current_map = None
        rank = 0
        for row in rows:
            if row["map_id"] != current_map:
                current_map = row["map_id"]
                rank = 0
                print("\n-- 地图 #%d --" % current_map)
            rank = rank + 1
            when = row["time"].strftime("%Y-%m-%d %H:%M")
            print("  %d. %-8s %3d 步   %s" % (rank, row["name"], row["steps"], when))
    print("\n按任意键返回…")
    game.read_key()


def run():
    """主菜单循环:选模式。"""
    while True:
        game.clear_screen()
        print("==============================")
        print("        迷 宫 大 冒 险")
        print("==============================\n")
        print("   1    Single      单人闯关")
        print("   2    VS Mode     双人对战")
        print("   3    Arena       机器人比赛")
        print("   4    Replay      看录像")
        print("   5    Leaderboard 排行榜")
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
            arena_game()
        elif key == "4":
            replay_game()
        elif key == "5":
            show_leaderboard()
        # 其它键忽略,重画菜单
