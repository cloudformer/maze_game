# bots/sample2.py —— 傻瓜 bot 二号:和 Sample1 一样的套路,但挑方向的顺序【反过来】。
# 顺序:左 → 上 → 右 → 下。顺序不同,走出来的路就不同,可以和 Sample1 比谁快。

from bots.base import Bot


class Sample2(Bot):
    bot_id = 2
    name = "Sample2"
    author = "老师"
    symbol = "S2"
    direction = "left"                        # 开局朝左
    order = ["left", "up", "right", "down"]   # 撞墙时按这个顺序挑(和 Sample1 相反)

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
