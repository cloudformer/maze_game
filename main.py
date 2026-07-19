# main.py —— 程序入口。命令:
#   python main.py gen 15 15     生成并打印一张迷宫
#   python main.py play 15 15    生成一张迷宫,用 W/A/S/D 走小人
# 15 15 是迷宫的宽和高(不写就用默认 15 15)

import sys
import mazegen
import game


def read_size(args):
    """从命令行参数里读宽和高;没给就默认 15 15。"""
    width = 15
    height = 15
    if len(args) >= 3:
        width = int(args[1])
        height = int(args[2])
    return width, height


def do_gen(args):
    """生成一张迷宫,打印出来看。"""
    width, height = read_size(args)
    text = mazegen.generate(width, height)
    print(text)


def do_play(args):
    """生成一张迷宫,放小人进去用 W/A/S/D 走。"""
    width, height = read_size(args)
    text = mazegen.generate(width, height)
    game.play(text)


def main():
    # sys.argv 是命令行里敲的一串词:['main.py', 'gen', '15', '15']
    args = sys.argv[1:]  # 去掉第一个(文件名本身)

    if len(args) >= 1 and args[0] == "gen":
        do_gen(args)
    elif len(args) >= 1 and args[0] == "play":
        do_play(args)
    else:
        print("用法:")
        print("  python main.py gen 15 15     生成并打印迷宫")
        print("  python main.py play 15 15    放小人用 W/A/S/D 走")


main()
