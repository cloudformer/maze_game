# mazegen.py —— 只做一件事:生成一张迷宫,返回字符画
# 用的是"递归回溯挖墙"算法:
#   和"递归遍历文件目录"是一模一样的思路——
#   进入一个新格子 = 走进一个子目录;
#   四周都走不通、要退回上一格 = 这个目录看完了、返回上一层。

import random

WALL = "#"   # 墙
PATH = " "   # 路(空白)
EXIT = "E"   # 出口(走到这里就通关)


def generate(width, height):
    """生成一张迷宫,返回字符画(字符串)。
    '#'=墙,空格=路,'E'=出口,行与行之间用换行符隔开。
    小人从左上角那格出发,目标是走到右下角的出口 E。"""
    # 迷宫的格子要落在奇数行奇数列上(偶数位置留给墙),所以宽高强制成奇数
    if width % 2 == 0:
        width = width + 1
    if height % 2 == 0:
        height = height + 1
    if width < 5:
        width = 5
    if height < 5:
        height = 5

    # 一开始整张图全是墙,后面再一格一格把路"挖"出来
    grid = []
    for _ in range(height):
        grid.append(list(WALL * width))

    # 真正的挖墙:从 (x, y) 这一格出发,随机选方向往外挖
    def carve(x, y):
        grid[y][x] = PATH  # 把当前格挖成路(空白)
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

    # 把二维列表拼成字符画字符串
    lines = []
    for row in grid:
        lines.append("".join(row))
    return "\n".join(lines)


def parse(text):
    """把字符画字符串还原成二维列表 grid[y][x],方便一格一格地读。
    注意:这是"读地图"用的,读出来只看不改——小人走动不会动到它。"""
    grid = []
    for line in text.split("\n"):
        grid.append(list(line))
    return grid
