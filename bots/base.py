# bots/base.py —— 所有 bot 的"基类"(共同的样子)。
# 一个 bot 只需要实现一个方法:next_move(pos, walls)。
# 每回合 bot 只看得到四邻(上下左右是墙还是路),和蒙着眼走的真人一样。

class Bot:
    name = "基类"     # bot 的名字(排行榜/提示里显示)
    author = "无名"   # 作者(谁写的这个 bot,比如孩子的名字)
    symbol = "??"     # 在迷宫里显示成什么(2 个字符宽)

    def __init__(self):
        self.memory = {}   # 想记什么自己往里放(走过的格子、计数器…),笨 bot 可以不用

    def next_move(self, pos, walls):
        """pos = (x, y) 现在在哪;
        walls = {'U':是不是墙, 'D':..., 'L':..., 'R':...},True 表示那边是墙。
        必须返回 'U'/'D'/'L'/'R' 中的一个(上/下/左/右)。
        基类不干活,交给子类去实现。"""
        raise NotImplementedError
