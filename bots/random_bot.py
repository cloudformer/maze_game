# bots/random_bot.py —— 直着走,前方撞墙才随机换方向。
# 规则:一直沿"当前方向"走;当前方向前面是墙了,就在能走的方向里随机挑一个新方向。
# 方向(self.direction)在基类里;读墙、挑方向是这个 bot 自己的活。

import random

from bots.base import Bot


class RandomBot(Bot):
    name = "Random"
    author = "老师"   # 示例 bot,署名老师;孩子写自己的 bot 就署自己名字
    symbol = "><"     # 一脸懵的小人

    def next_move(self, pos, walls):
        # 1) 当前方向前面不是墙,就继续沿这个方向直走
        if not walls[self.direction]:
            return self.direction

        # 2) 前面撞墙了:拿到所有能走的方向(基类的 open_directions 帮我们收集)
        choices = self.open_directions(walls)

        # 3) 从能走的方向里随机挑一个,【记下来】,以后就沿这个新方向直走
        if len(choices) == 0:
            return self.direction         # 四面都是墙(几乎不会发生),兜底
        self.direction = random.choice(choices)
        return self.direction
