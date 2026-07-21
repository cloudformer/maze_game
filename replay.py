# replay.py —— 看录像:按 play 的 id 回放走过的轨迹。
# 传进来的是一串 id(列表),如 [3] 或 [3, 5]——多条会一起重播,方便对比。
# 每条 play 里已含 地图、轨迹、图标,所以不用另外传地图。
# 倍速:每帧停顿 = 标准 0.2 秒(config.BOT_STEP_DELAY)÷ 倍速,播放中按 1/2/3/4 随时切换。

import config
import game
import db

SPEEDS = {"1": 1, "2": 2, "3": 5, "4": 10}   # 按键 -> 倍速


def replay(play_ids):
    """回放一串 play(id 列表)。播放中按 1/2/3/4 调倍速,Q 退出。"""
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

    speed = 1
    frame = 0
    while frame <= total:
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

        # 倍速条:当前选中的标 *,如  [*1x] [ 2x] [ 5x] [ 10x]
        bar = ""
        for key in ["1", "2", "3", "4"]:
            mark = "*" if SPEEDS[key] == speed else " "
            bar += "[%s%dx] " % (mark, SPEEDS[key])
        print("倍速 " + bar + "  按 1/2/3/4 切换,Q 退出")

        # 这一帧的停顿;期间按了键就立刻处理
        key = game.wait_key(config.BOT_STEP_DELAY / speed)
        if key == "q":
            return
        if key in SPEEDS:
            speed = SPEEDS[key]
        frame = frame + 1

    print("\n回放结束。按任意键返回…")
    game.read_key()
