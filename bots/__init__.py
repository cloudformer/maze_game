# bots/__init__.py
# All available bots are imported and listed here.

from bots.sample1 import Sample1
from bots.sample2 import Sample2
from bots.sample3_pro import SmartBot
# SmartBot 暂时下场:它靠直接读整张地图(上帝视角)工作,
# 改成被动式后 bot 手里没有地图了,它需要改造成"边走边自己记地图再 BFS"的合法版。
# from bots.sample3_pro import SmartBot


# All bots available for Arena
ALL = [
    Sample1,
    Sample2,
    SmartBot
]


def by_id(bot_id):
    """Find bot class by its number."""
    for cls in ALL:
        if cls.bot_id == bot_id:
            return cls
    return None
