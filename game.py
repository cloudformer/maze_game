# game.py —— 手动玩:在迷宫里放【一个或多个】小人,谁先到出口谁赢。
#
# 通用设计:play(grid, players) 吃一个"玩家清单"。
#   单人 = 清单里 1 个玩家;双人 = 2 个;想几个人都行(受控制方案数量限制)。
#
# 走路不改地图:grid 是只读底图,小人位置各自记着,画的时候才把小人叠上去。
# 人物"透明":两个小人走到同一格不特殊处理,直接叠着画。

import os
import sys
import config  # 墙/出口/小人图标 都在 config.py 里

WALL = config.WALL
EXIT = config.EXIT

# 控制方案清单:第 i 个玩家用第 i 套键。想加第 4 个人就再加一套。
# 走法 (dx, dy):x=列 y=行;上 y-1、下 y+1、左 x-1、右 x+1。
CONTROLS = [
    {"name": "W/A/S/D", "keys": {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}},
    {"name": "方向键",   "keys": {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}},
    {"name": "I/J/K/L", "keys": {"i": (0, -1), "k": (0, 1), "j": (-1, 0), "l": (1, 0)}},
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


def find_exit(grid):
    """在地图里找到出口的坐标 (x, y)。"""
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x] == EXIT:
                return (x, y)
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


def play(grid, players):
    """在迷宫里走小人,谁先到出口谁赢。
    players:玩家清单(用 make_players 造)。
    返回获胜的那个玩家(里面有 label / steps);中途按 Q 退出则返回 None。"""
    exit_pos = find_exit(grid)
    for player in players:                     # 所有人从左上角起步,步数清零
        player["x"] = 1
        player["y"] = 1
        player["steps"] = 0

    while True:
        clear_screen()
        draw(grid, players)
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
                dx, dy = player["keys"][key]
                target_x = player["x"] + dx
                target_y = player["y"] + dy
                if grid[target_y][target_x] != WALL:   # 撞墙不动
                    player["x"] = target_x
                    player["y"] = target_y
                    player["steps"] = player["steps"] + 1
                    if (player["x"], player["y"]) == exit_pos:
                        clear_screen()
                        draw(grid, players)
                        return player          # 这个玩家先到,赢了
                break
