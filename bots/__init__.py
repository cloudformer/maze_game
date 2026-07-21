# bots/__init__.py —— 让 bots 成为一个"包",并把所有 bot 汇总到这里。
# 加了新 bot 就在这里 import 一行,再加进 ALL,别处就能按编号选它参赛。

from bots.sample1 import Sample1
from bots.sample2 import Sample2

# 所有可参赛的 bot(Arena 列出来、按编号挑)
ALL = [Sample1, Sample2]


def by_id(bot_id):
    """按编号找到对应的 bot 类;没有就返回 None。"""
    for cls in ALL:
        if cls.bot_id == bot_id:
            return cls
    return None
