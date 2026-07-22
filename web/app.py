# web/app.py —— 网页外壳(Flask),坦克大战风格。独立于终端版,只复用核心。
# 跑:  项目根目录下  python web/app.py   浏览器开 http://127.0.0.1:5000
#
# 菜单:单人 / 多人 / Bot / 录像。逻辑全在核心,这里只是薄路由 + 一点前端。

import os
import sys

# 让 web/ 能 import 到项目根的核心模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request

import mazegen
import maze
import db
import bots
import game     # 通用游戏逻辑:step(走一步/moved/记轨迹)、fit2
import config   # BOT_STEP_DELAY / PLAYERS 图标

app = Flask(__name__)
db.init_db()          # 确保表在(只建不改,和终端共用同一个 maze.db)

state = {}            # 单人/多人:当前这一局(grid / 两人位置 / 出口)


def chosen_size():
    """从 ?level=N 读关卡号,查共同的关卡表 config.MAP_SIZES(和终端同一张表)。"""
    level = request.args.get("level", "3")
    if level.isdigit() and int(level) in config.MAP_SIZES:
        return config.MAP_SIZES[int(level)]
    return 15


def cell_types(grid):
    """把 grid 转成 'wall'/'path'/'exit' 给前端上色。"""
    rows = []
    for row in grid:
        line = []
        for c in row:
            if c == maze.WALL:
                line.append("wall")
            elif c == maze.EXIT:
                line.append("exit")
            else:
                line.append("path")
        rows.append(line)
    return rows


def frames_of(grid, path):
    """把一条轨迹 path 变成"每一步的画面数据":每帧含方向 + 那一格的 status()。
    回放时前端照着一帧帧放、并显示 status(和单人页那行 JSON 一样)。"""
    frames = []
    prev = (1, 1)                        # 起点
    for cur in path:
        cx, cy = cur[0], cur[1]
        if cx > prev[0]:
            direction = "right"
        elif cx < prev[0]:
            direction = "left"
        elif cy > prev[1]:
            direction = "down"
        else:
            direction = "up"
        status = maze.look(grid, cx, cy)
        status["pos"] = [cx, cy]
        frames.append({"dir": direction, "moved": 1, "status": status})
        prev = (cx, cy)
    return frames


def run_bot(grid, bot):
    """在 web 里把一个 bot 跑完(被动式),返回轨迹 path(只跑不画,画交给浏览器)。
    和终端同一套:游戏算 status 递给 bot,bot 还方向,game.step 执行。"""
    runner = {"x": 1, "y": 1, "path": [], "moved": "-"}
    exit_pos = maze.find_exit(grid)
    limit = len(grid) * len(grid[0]) * 5
    turns = 0
    while turns < limit and (runner["x"], runner["y"]) != exit_pos:
        status = maze.look(grid, runner["x"], runner["y"])
        status["pos"] = (runner["x"], runner["y"])
        status["moved"] = runner["moved"]    # 上一步走没走成:1走了 0撞墙 -还没走过
        direction = bot.go_to_exit(status)
        if direction in maze.MOVES:
            game.step(grid, runner, direction)
        turns = turns + 1
    return runner["path"]


# ---------------- 菜单 ----------------
@app.route("/")
def menu():
    bot_list = [{"id": c.bot_id, "name": c.name, "author": c.author} for c in bots.ALL]
    return render_template("menu.html", bots=bot_list, plays=db.leaderboard(),
                           sizes=config.MAP_SIZES)


# ---------------- 单人 / 多人(可交互) ----------------
@app.route("/play")
def play():
    mode = request.args.get("mode", "single")     # single | vs
    size = chosen_size()
    grid = mazegen.generate(size, size)
    state["grid"] = grid
    state["exit"] = maze.find_exit(grid)
    # 玩家和终端里同一个形状:位置 + 轨迹 + moved(game.step 会维护它们)
    state["p1"] = {"x": 1, "y": 1, "path": [], "moved": "-"}
    state["p2"] = {"x": 1, "y": 1, "path": [], "moved": "-"}
    return render_template("play.html", cells=cell_types(grid), mode=mode,
                           p1=[1, 1], p2=[1, 1])


@app.route("/move")
def move():
    """走一步:和终端用的是同一个 game.step(撞墙不动、记 moved、记轨迹)。"""
    key = "p1" if request.args.get("p") == "1" else "p2"
    direction = request.args.get("dir")
    player = state[key]
    if direction in maze.MOVES:
        game.step(state["grid"], player, direction)

    winner = 0
    if (state["p1"]["x"], state["p1"]["y"]) == state["exit"]:
        winner = 1
    elif (state["p2"]["x"], state["p2"]["y"]) == state["exit"]:
        winner = 2

    status = maze.look(state["grid"], player["x"], player["y"])
    status["pos"] = [player["x"], player["y"]]
    return jsonify(player=key, dir=direction, moved=player["moved"],
                   p1=[state["p1"]["x"], state["p1"]["y"]],
                   p2=[state["p2"]["x"], state["p2"]["y"]],
                   status=status, winner=winner)


@app.route("/save")
def save():
    """赢了签名进 db(和终端同一条街机规矩:通关才有名字)。返回交易 id。"""
    key = "p1" if request.args.get("p") == "1" else "p2"
    name = request.args.get("name", "").strip() or "无名氏"
    grid = state["grid"]
    map_id = db.save_map(len(grid[0]), len(grid), grid)      # 这局的图也入库,回放要用
    symbol = config.PLAYERS[0] if key == "p1" else config.PLAYERS[1]
    play_id = db.save_play(name, map_id, state[key]["path"], game.fit2(symbol))
    return jsonify(play_id=play_id)


# ---------------- Bot:现场跑一个 bot,浏览器动画 ----------------
@app.route("/bot")
def bot_page():
    """只跑勾选的 bot(?ids=1,3):同一张新图上各跑一遍,一起动画、比步数。"""
    size = chosen_size()
    grid = mazegen.generate(size, size)

    runs = []
    for token in request.args.get("ids", "").split(","):
        if token.isdigit() and bots.by_id(int(token)) is not None:
            cls = bots.by_id(int(token))
            path = run_bot(grid, cls())
            runs.append({"name": cls.name, "author": cls.author,
                         "steps": len(path), "frames": frames_of(grid, path)})

    if len(runs) == 1:
        title = "%s(作者:%s)—— %d 步" % (runs[0]["name"], runs[0]["author"], runs[0]["steps"])
    else:
        title = "机器人比赛(%d 名选手)" % len(runs)
    return render_template("watch.html", cells=cell_types(grid), title=title,
                           runs=runs, base=int(config.BOT_STEP_DELAY * 1000))


# ---------------- 录像:回放数据库里存的一局 ----------------
@app.route("/replay")
def replay_page():
    play_id = int(request.args.get("id"))
    one = db.get_play(play_id)
    grid = db.get_map(one["map_id"])
    title = "回放 #%d —— %s,%d 步" % (play_id, one["name"], len(one["path"]))
    runs = [{"name": one["name"], "author": "", "steps": len(one["path"]),
             "frames": frames_of(grid, one["path"])}]
    return render_template("watch.html", cells=cell_types(grid), title=title,
                           runs=runs, base=int(config.BOT_STEP_DELAY * 1000))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
