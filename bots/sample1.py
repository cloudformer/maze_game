# bots/sample1.py —— 傻瓜 bot 一号:直着走,撞墙就按固定顺序挑方向。
# 顺序:右 → 下 → 左 → 上(挑第一个能走的)。

from bots.base import Bot


class Sample1(Bot):
    bot_id = 1
    name = "Sample1"
    author = "老师"
    symbol = "S1"
    direction = "right"                       # 当前朝向(开局朝右)
    order = ["right", "down", "left", "up"]   # 撞墙时按这个顺序挑

    def go_to_exit(self, status):
        # 1) 当前方向前面是路,就继续沿这个方向直走
        if status[self.direction] == "path":
            return self.direction
        # 2) 前面是墙:按固定顺序挑第一个能走的方向,记住它
        for d in self.order:
            if status[d] == "path":
                self.direction = d
                return d
