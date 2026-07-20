# bots/base.py —— 所有 bot 的"基类"(共同的样子),只放最基本的东西。
#
# 写一个 bot 的标准约定(照这个填就行):
#   1. 新建一个类继承 Bot:  class 我的Bot(Bot)
#   2. 写上 name / author / symbol(名字/作者/图标)
#   3. 只实现一个方法:  next_move(self, pos, walls)
#        pos   = (x, y) 当前在哪
#        walls = {'U':是不是墙, 'D':..., 'L':..., 'R':...}(四邻小抄,由游戏递进来)
#        返回  = 'U'/'D'/'L'/'R' 中的一个方向
#   可用的现成东西:self.direction(记朝向)、self.open_directions(walls)(拿能走的方向)
#
# 重要:bot 只看 walls 决策,【不碰地图 grid】。walls 是游戏 look() 读好递进来的。

class Bot:
    name = "基类"     # bot 的名字(排行榜/提示里显示)
    author = "无名"   # 作者(谁写的这个 bot,比如孩子的名字)
    symbol = "??"     # 在迷宫里显示成什么(2 个字符宽)

    def __init__(self):
        self.memory = {}       # 想记什么自己往里放(走过的格子、计数器…)
        self.direction = "D"   # 当前朝向,开局默认往下(会走的 bot 可随时改)

    def next_move(self, pos, walls):
        """pos = (x, y) 现在在哪;
        walls = {'U':是不是墙, 'D':..., 'L':..., 'R':...},True 表示那边是墙。
        必须返回 'U'/'D'/'L'/'R' 中的一个(上/下/左/右)。
        基类不干活,交给子类去实现。"""
        raise NotImplementedError

    def open_directions(self, walls):
        """返回所有"不是墙、能走"的方向清单,比如 ['D', 'R']。所有 bot 都能用。"""
        choices = []
        for direction in ["U", "D", "L", "R"]:
            if not walls[direction]:      # 不是墙,就能走
                choices.append(direction)
        return choices
