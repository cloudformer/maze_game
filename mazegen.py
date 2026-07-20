# mazegen.py —— 只做一件事:生成一张迷宫,返回二维表 grid[y][x]
# 用的是"递归回溯挖墙"算法:
#   和"递归遍历文件目录"是一模一样的思路——
#   进入一个新格子 = 走进一个子目录;
#   四周都走不通、要退回上一格 = 这个目录看完了、返回上一层。
#
# 每个格子直接存 config 里的样子(墙 '██'、路 '  ' 等,都是 2 个字符宽)。
# 打印时把每格原样拼起来就是正方形的迷宫,不需要再做任何加宽处理。

import random
import sys
import config  # 墙/路/出口/小人 的样子都在 config.py 里,想改样子改那儿

# 从设置里取符号,下面全用这几个变量,不再直接写死
WALL = config.WALL   # 墙
PATH = config.PATH   # 路
EXIT = config.EXIT   # 出口(走到这里就通关)

# Python 默认最多递归约 1000 层(怕程序无限递归把内存吃光)。
# 我们的"挖墙"是递归的:挖进一格就深一层。100×100 的迷宫最深约 2500 层,
# 会超过 1000 报 RecursionError,所以把上限抬到 5000(留一倍余量,够用又不夸张)。
sys.setrecursionlimit(5000)


def generate(width, height):
    """生成一张迷宫,返回二维表 grid[y][x](每格是墙/路/出口的样子)。
    小人从左上角那格出发,目标是走到右下角的出口。"""
    # 迷宫的格子要落在奇数行奇数列上(偶数位置留给墙),所以宽高强制成奇数
    if width % 2 == 0:
        width = width + 1
    if height % 2 == 0:
        height = height + 1
    if width < 5:
        width = 5
    if height < 5:
        height = 5
    # 最大卡在 99(约 100):再大递归会太深,和上面 5000 的上限配套
    if width > 99:
        width = 99
    if height > 99:
        height = 99

    # 一开始整张图全是墙,后面再一格一格把路"挖"出来
    grid = []
    for _ in range(height):
        row = []
        for _ in range(width):
            row.append(WALL)
        grid.append(row)

    # 真正的挖墙:从 (x, y) 这一格出发,随机选方向往外挖
    def carve(x, y):
        grid[y][x] = PATH  # 把当前格挖成路
        # 四个方向,每次跳两格(隔一堵墙),先打乱顺序 = "随机选方向"
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx = x + dx
            ny = y + dy
            # 目标格必须还在图里,而且还没挖过(仍是墙)
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and grid[ny][nx] == WALL:
                grid[y + dy // 2][x + dx // 2] = PATH  # 打通中间那堵墙
                carve(nx, ny)  # 递归:走进新格子继续挖(挖不动时会自己退回来)

    carve(1, 1)  # 从左上角开始挖

    grid[height - 2][width - 2] = EXIT  # 右下角那格路,标成出口
    print(grid)
    return grid
