# bots/sample1.py —— 傻瓜 bot 一号:直着走,撞墙就按固定顺序挑方向。
# 和 RandomBot 的区别:RandomBot 撞墙时【随机】转,Sample1 撞墙时按【固定顺序】转。
# 顺序:右 → 下 → 左 → 上(挑第一个能走的)。

from bots.base import Bot


class Sample1(Bot):
    bot_id = 1
    name = "Sample1"
    author = "老师"
    symbol = "S1"
    direction = "right"                       # 开局朝右
    order = ["right", "down", "left", "up"]   # 撞墙时按这个顺序挑(DIRECTIONS 的一个排列)

    def go_to_exit(self):
        s = self.status()
        # 1) 当前方向能直走就直走
        if s[self.direction] == "path":
            self.move(self.direction)
            return
        # 2) 撞墙:按固定顺序挑第一个能走的方向
        for d in self.order:
            if s[d] == "path":
                self.direction = d
                self.move(d)
                return
