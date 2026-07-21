# replay.py —— 看录像:按 play 的 id 回放走过的轨迹。
# 传进来的是一串 id(列表),如 [3] 或 [3, 5]——多条会一起重播,方便对比。
# 每条 play 里已含 地图、轨迹、图标,所以不用另外传地图。

import time

import game
import db


def replay(play_ids, delay):
    """回放一串 play。play_ids 是列表;delay 是每帧停顿(秒),越小越快。"""
    runs = []                 # 每条:db.get_play 拿到的 {'name','symbol','path',...}
    map_id = None
    for play_id in play_ids:
        one = db.get_play(play_id)
        if one is not None:
            map_id = one["map_id"]     # 假设这些对局在同一张图上
            runs.append(one)

    if len(runs) == 0:
        print("没有可回放的录像。")
        return

    grid = db.get_map(map_id)

    # 总帧数 = 最长的那条轨迹(短的走完就停在原地)
    total = 0
    for one in runs:
        if len(one["path"]) > total:
            total = len(one["path"])

    # 一帧一帧地放。第 0 帧是起点,之后每帧各自往前走一步
    for frame in range(total + 1):
        game.clear_screen()
        drawables = []
        for one in runs:
            path = one["path"]
            if frame == 0:
                x, y = 1, 1                 # 起点
            elif frame <= len(path):
                x, y = path[frame - 1]      # 走到第 frame 步的位置
            else:
                x, y = path[-1]             # 短轨迹走完了,停在终点
            drawables.append({"symbol": one["symbol"], "x": x, "y": y})
        game.draw(grid, drawables)

        labels = []
        for one in runs:
            labels.append("%s %s(%d步)" % (one["symbol"], one["name"], len(one["path"])))
        print("\n回放 第 %d/%d 帧    " % (frame, total) + "   ".join(labels))
        time.sleep(delay)

    print("\n回放结束。按任意键返回…")
    game.read_key()
