# maze.py —— 迷宫世界的"规则":哪里是墙、四邻长啥样、能不能走一步、出口在哪。
# 人和 bot 都用这几个函数(bot 只经过它们,绝不直接碰 grid)。
# 注意:mazegen.py 负责"造"迷宫;maze.py 负责迷宫的"规则/查询"。

import config

WALL = config.WALL
EXIT = config.EXIT

# 四个方向 -> 走法 (dx, dy)。x=列 y=行;上 y-1、下 y+1、左 x-1、右 x+1。
# 这是全项目唯一定义方向增量的地方(人和 bot 都用它)。
MOVES = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def find_exit(grid):
    """在地图里找到出口的坐标 (x, y)。"""
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x] == EXIT:
                return (x, y)
    return None


def is_wall(grid, x, y):
    """(x, y) 那格是不是墙?"""
    return grid[y][x] == WALL


def look(grid, x, y):
    """站在 (x, y) 看四邻:返回 {'up':'path'/'wall', 'down':.., 'left':.., 'right':..}。
    'path'=路(能走),'wall'=墙。这就是递给 bot 的"小抄"。"""
    result = {}
    for direction in MOVES:
        dx, dy = MOVES[direction]
        result[direction] = "wall" if is_wall(grid, x + dx, y + dy) else "path"
    return result


def try_step(grid, x, y, dx, dy):
    """从 (x, y) 往 (dx, dy) 走一步:
    是路就返回 (新x, 新y, True);是墙就原地不动、返回 (x, y, False)。
    撞墙的判断只在这一个地方做,人类和 bot 共用。"""
    nx = x + dx
    ny = y + dy
    if is_wall(grid, nx, ny):
        return (x, y, False)
    return (nx, ny, True)
