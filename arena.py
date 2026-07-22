# arena.py —— bot 比赛:传进来一串 bot,同一张图各跑一遍,比谁步数少(谁更聪明)。
# 关键:参数是一个【列表】bot_list,想比几个就放几个,如 [Sample1(), Sample2()]。

import game
import db


def run(grid, map_id, bot_list, delay, max_steps):
    """让 bot_list 里每个 bot 在同一张图上各跑一遍,每局(通关的)存进 plays,
    最后按步数排名。返回本场记录下来的交易 id 列表(用来看录像)。"""
    results = []                              # 收集 (bot, 步数);没走出去记 None
    play_ids = []                             # 本场存下来的交易 id
    for bot in bot_list:
        path = game.watch_bot(grid, bot, delay, max_steps)   # 看它跑,拿回轨迹
        # 只记【跑到终点】的(通关才有成绩);超时没出去的不记
        if path is not None:
            play_ids.append(db.save_play(bot.name, map_id, path, game.fit2(bot.symbol)))
        results.append((bot, None if path is None else len(path)))
        print("\n按任意键看下一个…")
        game.read_key()

    # 排名:步数少的在前;没走出去的(None)排最后
    def key_of(item):
        steps = item[1]
        if steps is None:
            return 10 ** 9                    # 没走出去 = 排最后
        return steps
    results.sort(key=key_of)

    game.clear_screen()
    print("========== 比 赛 结 果 ==========\n")
    place = 1
    for bot, steps in results:
        if steps is None:
            outcome = "没走出去(超步数)"
        else:
            outcome = "%d 步" % steps
        print("  %d. %s %s(作者:%s)  %s" %
              (place, bot.symbol, bot.name, bot.author, outcome))
        place = place + 1
    print("\n本场交易 id:", play_ids, " —— 用「看录像」输入这些 id 就能回放")
    print("按任意键返回…")
    game.read_key()
    return play_ids
