# bots/__init__.py
# All available bots are imported and listed here.

from bots.sample1 import Sample1
from bots.sample2 import Sample2
from bots.sample3_pro import SmartBot
from bots.sample4_no_cheat import Sample4

# All bots available for Arena
ALL = [
    Sample1,
    Sample2,
    SmartBot,
    Sample4
]


def by_id(bot_id):
    """Find bot class by its number."""
    for cls in ALL:
        if cls.bot_id == bot_id:
            return cls
    return None
