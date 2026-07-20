# bots/__init__.py —— 让 bots 成为一个"包",并把所有 bot 汇总到这里。
# 以后加了新 bot,就在这里再 import 一行,别处 `import bots` 就都能用。

from bots.base import Bot
from bots.random_bot import RandomBot

# 所有可用的 bot(将来竞技场会用到这份清单)
ALL_BOTS = [RandomBot]
