# game.py —— 手动玩:在迷宫里放【一个或多个】小人,谁先到出口谁赢。
#
# 通用设计:play(grid, players) 吃一个"玩家清单"。
#   单人 = 清单里 1 个玩家;双人 = 2 个;想几个人都行(受控制方案数量限制)。
#
# 走路不改地图:grid 是只读底图,小人位置各自记着,画的时候才把小人叠上去。
# 人物"透明":两个小人走到同一格不特殊处理,直接叠着画。

import os
import sys
import time
import config  # 小人图标等
import maze     # 迷宫世界规则:MOVES / find_exit / try_step 等

# 控制方案清单:第 i 个玩家用第 i 套键。想加第 3 个人就再加一套(图标也要在 config.PLAYERS 补一个)。
# keys 把"按下的键"映射到"方向名",增量统一去查 MOVES。
CONTROLS = [
    {"name": "W/A/S/D", "keys": {"w": "up", "s": "down", "a": "left", "d": "right"}},
    {"name": "方向键",   "keys": {"up": "up", "down": "down", "left": "left", "right": "right"}},
]


def fit2(symbol):
    """把小人图标弄成正好 2 个字符宽:多了砍掉,少了补空格(和"一格2字符"对齐)。"""
    symbol = symbol[:2]
    if len(symbol) < 2:
        symbol = symbol + " " * (2 - len(symbol))
    return symbol


def make_players(count):
    """按人数造玩家清单:第 i 个玩家配第 i 个图标(config.PLAYERS)和第 i 套控制键。"""
    players = []
    for i in range(count):
        players.append({
            "symbol": fit2(config.PLAYERS[i]),   # 显示用的图标
            "keys": CONTROLS[i]["keys"],         # 这个人的控制键
            "control_name": CONTROLS[i]["name"], # 提示文字
            "label": "玩家" + str(i + 1),         # 名次标签
        })
    return players


def clear_screen():
    """清屏,让每走一步画面像在原地刷新。Windows 用 cls,Mac/Linux 用 clear。"""
    os.system("cls" if os.name == "nt" else "clear")


def read_key():
    """读一个按键,按下就返回,不用回车。
    普通键返回小写字母(如 'w');方向键返回 'up'/'down'/'left'/'right'。
    两套系统读键方式不同,分开处理:
      - Windows:msvcrt.getwch();方向键是两个字符(前缀 + 方向码);
      - Mac/Linux:临时切到"不等回车"模式;方向键是 ESC + '[' + 字母。"""
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):            # 方向键前缀
            code = msvcrt.getwch()
            arrows = {"H": "up", "P": "down", "K": "left", "M": "right"}
            return arrows.get(code, "")
        return ch.lower()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":                  # ESC:可能是方向键
                seq = sys.stdin.read(2)       # 再读两个字符,如 '[A'
                arrows = {"[A": "up", "[B": "down", "[D": "left", "[C": "right"}
                return arrows.get(seq, "")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch.lower()


def wait_key(seconds):
    """最多等 seconds 秒:期间按了键就立刻返回那个键,没按返回 None。
    (回放用:既是"每帧的停顿",又能随时收到调倍速/退出的按键。)"""
    if os.name == "nt":
        import msvcrt
        end = time.time() + seconds
        while time.time() < end:
            if msvcrt.kbhit():
                return read_key()
            time.sleep(0.01)
        return None
    else:
        import select
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ready = select.select([sys.stdin], [], [], seconds)[0]  # 等按键,最多 seconds 秒
            if ready:
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    seq = sys.stdin.read(2)
                    arrows = {"[A": "up", "[B": "down", "[D": "left", "[C": "right"}
                    return arrows.get(seq, "")
                return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return None


def draw(grid, players):
    """打印地图,并把每个小人叠在自己的位置上。
    对 grid 只读不改:每行复制一份再改副本,原地图不动。
    人物透明:多个小人同格就直接后画的盖在上面,不特殊处理。"""
    for y in range(len(grid)):
        row = list(grid[y])                   # 复制这一行(不动原地图)
        for player in players:
            if player["y"] == y:
                row[player["x"]] = player["symbol"]
        print("".join(row))                   # 每格 2 字符宽,拼起来就是正方形


def step(grid, player, direction):
    """走一步 —— 游戏的基本动作,终端和网页共用同一份:
    撞墙不动;走成了就更新位置、把新位置记进 path(轨迹,回放和算步数用)。
    player["moved"] 记这一步的结果:1=走了 0=撞墙(和 bot 的 move() 返回一样)。"""
    dx, dy = maze.MOVES[direction]
    nx, ny, ok = maze.try_step(grid, player["x"], player["y"], dx, dy)
    player["moved"] = 1 if ok else 0
    if ok:
        player["x"] = nx
        player["y"] = ny
        player["path"].append([nx, ny])


def play(grid, players):
    """在迷宫里走小人,谁先到出口谁赢。
    players:玩家清单(用 make_players 造)。
    每个玩家会自动记轨迹到 player["path"](走一步记一个位置),步数 = len(path)。
    返回获胜的那个玩家;中途按 Q 退出则返回 None(轨迹仍在各玩家的 path 里)。"""
    exit_pos = maze.find_exit(grid)
    for player in players:                     # 所有人从左上角起步,轨迹清空
        player["x"] = 1
        player["y"] = 1
        player["path"] = []
        player["moved"] = "-"                  # 上一步:1=走了 0=撞墙 -=还没走过

    while True:
        clear_screen()
        draw(grid, players)
        for player in players:             # 手动也打印 status()(学习用,和写 bot 时拿到的一样)
            state = maze.look(grid, player["x"], player["y"])
            state["pos"] = (player["x"], player["y"])
            print("%s %s status()=%s  moved=%s" % (player["symbol"], player["label"],
                                                   state, player["moved"]))
        # 提示:每个玩家用哪套键
        hints = []
        for player in players:
            hints.append("%s %s:%s" % (player["symbol"], player["label"], player["control_name"]))
        print("\n" + "    ".join(hints) + "    Q:退出(按键即走,不用回车)")

        key = read_key()
        if key == "q":
            return None                        # 没人赢

        # 这个键属于哪个玩家,就动哪个玩家(一个键只属于一个人)
        for player in players:
            if key in player["keys"]:
                step(grid, player, player["keys"][key])   # 走一步(通用逻辑在 step 里)
                if (player["x"], player["y"]) == exit_pos:
                    clear_screen()
                    draw(grid, players)
                    return player              # 这个玩家先到,赢了
                break


def watch_bot(grid, bot, delay, max_steps):
    """看一个 bot 自己走迷宫(动画)。走到出口返回回合数;太多回合没出去返回 None。
    分工:游戏把地图和起点交给 bot(塞进 bot._grid/_x/_y),然后一圈圈喊 bot.go_to_exit();
          bot 在 go_to_exit 里自己用 status()/move() 感知和行走。
          画面、计时、判断到没到出口、回合上限 —— 都是游戏管。bot 不碰地图。"""
    exit_pos = maze.find_exit(grid)
    bot._grid = grid            # 把地图交给 bot 的"遥控器"(它只经 status/move 用)
    bot._x = 1                  # 起点由游戏定
    bot._y = 1
    turns = 0

    while turns < max_steps:
        clear_screen()
        draw(grid, [{"symbol": fit2(bot.symbol), "x": bot._x, "y": bot._y}])
        # 打印 bot 这一步收到的 status()(和写 bot 时 self.status() 拿到的一样)
        print("\n%s(作者:%s) 第 %d 步" % (bot.name, bot.author, turns))
        print("go_to_exit 收到 status() =", bot.status())
        print("(据此决定往哪走;Ctrl+C 退出)")

        if (bot._x, bot._y) == exit_pos:
            print("\n🤖 %s 到达终点!用了 %d 步。" % (bot.name, turns))
            return turns

        time.sleep(delay)       # 停一下,才看得见动画
        bot.go_to_exit()        # bot 自己 status()+move(),会更新 bot._x/_y
        turns = turns + 1

    print("\n😵 %s 走了 %d 步还没出去(超步数上限)。" % (bot.name, turns))
    return None
