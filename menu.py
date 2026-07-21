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
    """机器人比赛(实时):选图,输入要参赛的 bot 编号(可 1 个、几个),各跑一遍再排名。"""
    map_id = choose_map()
    if map_id is None:
        return
    grid = db.get_map(map_id)

    game.clear_screen()
    print("========== 可 参 赛 的 Bot ==========\n")
    for cls in bots.ALL:
        print("   %d   %s %s(作者:%s)" % (cls.bot_id, cls.symbol, cls.name, cls.author))
    print("")
    raw = input("输入参赛 bot 编号(空格分隔,如 1 2):").split()

    bot_list = []
    for token in raw:
        if token.isdigit():
            cls = bots.by_id(int(token))
            if cls is not None:
                bot_list.append(cls())            # 建一个新实例参赛
    if len(bot_list) == 0:
        print("没选到 bot。按任意键返回…")
        game.read_key()
        return

    max_steps = len(grid) * len(grid[0]) * 5
    arena.run(grid, map_id, bot_list, config.BOT_STEP_DELAY, max_steps)


def replay_game():
    """看录像:输入交易 id(可多个)。播放中按 1/2/3/4 调倍速,Q 退出。"""
    game.clear_screen()
    print("========== 看 录 像 ==========\n")
    print("(交易 id 在排行榜、或比赛结束时都能看到)\n")
    raw = input("输入要回放的交易 id(可多个,空格分隔):").split()
    play_ids = []
    for token in raw:
        if token.isdigit():
            play_ids.append(int(token))
    if len(play_ids) == 0:
        return
    replay.replay(play_ids)


def show_leaderboard():
    """排行榜:按地图分组、步数从少到多(每图前 10)。带交易 id,可照着去看录像。"""
    game.clear_screen()
    print("========== 排 行 榜(每图前10)==========\n")
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
            # 交易id=#.. 让你知道去"看录像"输入哪个
            print("  %d. %-8s %3d 步   (交易id #%d)" % (rank, row["name"], row["steps"], row["id"]))
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
        # 任何模式里按 Ctrl+C 都干净地退回菜单(不再报错)
        try:
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
        except KeyboardInterrupt:
            print("\n已中断,回到菜单…")
