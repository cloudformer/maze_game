# bots/random_bot.py —— 最笨的 bot:在"不是墙"的方向里随便挑一个。
# 几行就能跑通整个流程,但很笨,常常绕圈、走回头路。
# 教学点:用【循环】遍历四个方向,用【if】挑出能走的,再随机选一个。

import random

from bots.base import Bot


class RandomBot(Bot):
    name = "Random"
    author = "老师"   # 示例 bot,署名老师;孩子写自己的 bot 就署自己名字
    symbol = "><"     # 一脸懵的小人

    def next_move(self, pos, walls):
        # 1) 用循环走一遍四个方向,把"不是墙"的收进 choices
        choices = []
        for direction in ["U", "D", "L", "R"]:
            if not walls[direction]:      # if:这个方向不是墙,就能走
                choices.append(direction)

        # 2) 从能走的方向里随便选一个
        if len(choices) == 0:
            return "U"                    # 四面都是墙(几乎不会发生),兜底
        return random.choice(choices)
