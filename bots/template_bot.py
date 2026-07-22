# bots/template_bot.py —— 机器人模板:复制本文件,改名,写你自己的 go_to_exit。
#
# ①  status —— 每回合游戏递给你的"眼睛"(按你的坐标现算的四邻):
#    {
#      "up":    "wall",     # 上边:  "path"=路(能走)  "wall"=墙(过不去)
#      "down":  "path",     # 下边
#      "left":  "wall",     # 左边
#      "right": "path",     # 右边
#      "pos":   (3, 1)      # 你现在的坐标 (x, y)
#    }
#
# ②  return —— 你的"移动指令"(bot 没有 move 函数,走这步由游戏执行,防止开图):
#    返回 "up" / "down" / "left" / "right" 之一;
#    游戏执行后:走成了 moved=1,撞墙 moved=0(原地不动),会显示在画面上。

from bots.base import Bot


class TemplateBot(Bot):
    bot_id = 99             # 编号:别和已有的重复
    name = "TemplateBot"    # 名字:改成你的 bot 名
    author = "你的名字"      # 作者:签上大名
    symbol = "T "           # 图标:2 个字符宽
    direction = "right"     # (可选)记住当前朝向,想用就用

    def go_to_exit(self, status):
        # ←←← 在这里写你的策略,最后 return 一个方向 →→→
        # 例:if status["right"] == "path": return "right"
        return
