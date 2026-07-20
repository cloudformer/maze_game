# main.py —— 程序入口。命令:
#   python main.py gen [宽 高]    生成一张迷宫,存进数据库(不玩)
#   python main.py play 编号      玩数据库里指定编号的地图
# gen 的宽高不写就默认 15 15。

import sys
import mazegen
import game
import db
import config


def read_size(args):
    """从命令行参数里读宽和高;没给就默认 15 15。"""
    width = 15
    height = 15
    if len(args) >= 3:
        width = int(args[1])
        height = int(args[2])
    return width, height


def do_gen(args):
    """生成一张迷宫,存进数据库,并打印出来。gen 只负责"生成 + 存",不玩。
    特例:gen all —— 按关卡表(config.MAP_SIZES)把 9 关默认地图都生成一遍。"""
    if len(args) >= 2 and args[1] == "all":
        gen_all()
        return
    width, height = read_size(args)
    grid = mazegen.generate(width, height)
    map_id = db.save_map(width, height, grid)   # 存进 maps 表,拿到编号
    print("已生成地图 #" + str(map_id) + "(" + str(width) + "x" + str(height) + ")")
    for row in grid:
        print("".join(row))
    print("玩它:python main.py play " + str(map_id))


def gen_all():
    """按关卡表把 9 关默认地图都生成并存库,只打印每关存成了几号。"""
    for level in sorted(config.MAP_SIZES):        # 关卡编号 1~9,从小到大
        size = config.MAP_SIZES[level]
        grid = mazegen.generate(size, size)
        map_id = db.save_map(size, size, grid)
        print("关卡 %d(%dx%d)-> 已存为地图 #%d" % (level, size, size, map_id))
    print("完成:9 关默认地图都生成好了。用 python main.py play 编号 开玩")


def do_play(args):
    """玩数据库里指定编号的地图。play 只负责"玩",不生成。
    没指定编号、或那张图不存在,就直接告诉你。"""
    if len(args) < 2:
        print("请指定要玩哪张地图,例如:python main.py play 1")
        return
    map_id = int(args[1])
    grid = db.get_map(map_id)                    # 从库里按编号取
    if grid is None:
        print("没有地图 #" + str(map_id) + ",先用 python main.py gen 生成一张")
        return
    game.play(grid)


def main():
    db.init_db()  # 确保数据库和三张表都在(已存在就什么都不做)

    # sys.argv 是命令行里敲的一串词:['main.py', 'gen', '15', '15']
    args = sys.argv[1:]  # 去掉第一个(文件名本身)

    if len(args) >= 1 and args[0] == "gen":
        do_gen(args)
    elif len(args) >= 1 and args[0] == "play":
        do_play(args)
    else:
        print("用法:")
        print("  python main.py gen [宽 高]    生成一张迷宫并存进数据库")
        print("  python main.py gen all       按关卡表生成 9 关默认地图")
        print("  python main.py play 编号      玩指定编号的地图")


main()
