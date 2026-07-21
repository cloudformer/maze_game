# bots/__init__.py —— 让 bots 成为一个"包",并把所有 bot 汇总到这里。
# 以后加了新 bot,就在这里再 import 一行,别处 `import bots` 就都能用。

from bots.sample1 import Sample1
from bots.sample2 import Sample2
