# game.py —— 手动玩:在迷宫里放一个小人,用 W/A/S/D 移动
#
# 最重要的设计(你特别要求的):走路不改地图。
#   - 地图 grid 是"只读底图",全程一个字都不改;
#   - 小人的位置只用两个数字 player_x, player_y 记着;
#   - 每次显示 = 底图照抄一遍,只在小人那一格盖上小人符号。
# 这样小人走到哪就显示到哪,底下的墙和路永远不变。

import os
import sys
import config  # 墙/出口/小人 的样子都在 config.py 里

WALL = config.WALL
EXIT = config.EXIT
PLAYER = config.PLAYER

# W/A/S/D 对应的走法(x=列, y=行)
# w=上 y-1;s=下 y+1;a=左 x-1;d=右 x+1
MOVES = {
    "w": (0, -1),
    "s": (0, 1),
    "a": (-1, 0),
    "d": (1, 0),
}


def clear_screen():
    """清屏,让每走一步画面像在原地刷新。Windows 用 cls,Mac/Linux 用 clear。"""
    os.system("cls" if os.name == "nt" else "clear")


def read_key():
    """读一个按键,按下就返回,不用回车。返回小写字母(如 'w')。
    两套系统读键的方式不一样,所以分开处理:
      - Windows:用 msvcrt.getwch() 直接抓一个键;
      - Mac/Linux:临时把终端切到"不等回车"模式,读一个字符,再切回来。"""
    if os.name == "nt":
        import msvcrt
        return msvcrt.getwch().lower()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()               # 键盘输入的编号
        old = termios.tcgetattr(fd)            # 记住原来的终端设置
        try:
            tty.setcbreak(fd)                  # 切到"按键即读、不回显、不等回车"
            ch = sys.stdin.read(1)             # 读一个字符
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)  # 一定切回原设置
        return ch.lower()


def draw(grid, player_x, player_y):
    """把地图打印出来,并在 (player_x, player_y) 那格盖上小人。
    关键:这里对 grid 只读不改——把每一行复制一份再改副本,原地图不动。"""
    for y in range(len(grid)):
        row = list(grid[y])          # 复制这一行(改副本,不动原地图)
        if y == player_y:
            row[player_x] = PLAYER   # 只在小人这一格盖上小人符号
        print("".join(row))          # 每格本来就是 2 字符宽,拼起来就是正方形


def find_exit(grid):
    """在地图里找到出口的坐标 (x, y)。"""
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x] == EXIT:
                return (x, y)
    return None


def play(grid):
    """在一张迷宫(二维表 grid)里走小人,走到出口就通关。"""
    exit_x, exit_y = find_exit(grid)  # 出口在哪
    player_x = 1                      # 小人起点:左上角那格路
    player_y = 1
    steps = 0                         # 走了多少步

    while True:
        clear_screen()
        draw(grid, player_x, player_y)
        print("\nW/A/S/D 移动,Q 退出(按键即走,不用回车)")

        key = read_key()   # 按一下就读一个键,不用回车

        if key == "q":
            print("再见!")
            return
        if key in MOVES:
            dx, dy = MOVES[key]
            target_x = player_x + dx
            target_y = player_y + dy
            # 目标格是墙就不动(撞墙不动);是路才走过去
            if grid[target_y][target_x] != WALL:
                player_x = target_x
                player_y = target_y
                steps = steps + 1
                # 走到出口就通关,结束
                if (player_x, player_y) == (exit_x, exit_y):
                    clear_screen()
                    draw(grid, player_x, player_y)
                    print("\n🎉 通关!你一共走了 " + str(steps) + " 步。")
                    return
