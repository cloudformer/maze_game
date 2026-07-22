# bots/base.py —— 所有 bot 的"基类"(被动式)。
#
# 每回合,游戏根据你的坐标现算四邻,递给你一份 status:
#   {'up':'path'/'wall', 'down':.., 'left':.., 'right':.., 'pos':(x,y)}
# 你只需要实现 go_to_exit(self, status):看一眼 status,返回要走的方向
# ('up'/'down'/'left'/'right')。走这一步(包括撞墙不动)由游戏执行。
#
# 被动式的意义:bot 手里【没有地图】,只有游戏递来的这一小份 status——
# 想开上帝视角也没东西可看,公平是结构保证的,不靠自觉。
# 想记东西(朝向、走过的格子…),自己在子类里建变量。

import maze   # 只为拿方向清单;maze 的函数都要传地图,而 bot 手里没有地图

# 四个方向(权威清单,写 bot 想遍历方向就用它)
DIRECTIONS = list(maze.MOVES)   # ['up', 'down', 'left', 'right']


class Bot:
    bot_id = 0          # 编号(比赛里按编号选谁参赛)
    name = "base"       # bot 名字
    author = "unknown"  # 作者
    symbol = "??"       # 迷宫里的图标(2 个字符宽)

    def go_to_exit(self, status):
        """看一眼 status(游戏按你的坐标现算的四邻),返回要走的方向。
        子类必须实现(抽象方法:基类只规定"要有",怎么走由每个 bot 自己写)。"""
        raise NotImplementedError
