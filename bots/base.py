# bots/base.py —— 所有 bot 的"基类"。
#
# 写一个 bot 只做一件事:实现 next_move(self)。
# 在 next_move 里,用下面两个"遥控器"(游戏做好的):
#   status()       -> {'up':'path'/'wall', 'down':.., 'left':.., 'right':.., 'pos':(x,y)}
#                     想看某个方向,自己取:status()["up"]
#   move("up")     -> 朝这个方向走一步;返回 1=走成功,0=撞墙没动
# 要记朝向、要记事本(memory)之类的,谁用谁自己在子类里建。
#
# 方向都用全词:'up' / 'down' / 'left' / 'right'。
# 重要:bot 只用 status()/move() 决策,【绝不碰地图】——地图是游戏的事。

import game   # 复用游戏现成的读墙(look)、走位(try_step);bot 不直接碰 grid

# bot 说的方向(全词) -> 游戏内部用的方向码
_DIR = {"up": "U", "down": "D", "left": "L", "right": "R"}


class Bot:
    name = "base"       # bot 名字
    author = "unknown"  # 作者
    symbol = "??"       # 迷宫里的图标(2 个字符宽)

    def __init__(self):
        # 这三个由游戏在开跑前塞进来,bot 不用管、也不要直接碰;
        # status() 和 move() 会用到它们。
        self._grid = None
        self._x = 0
        self._y = 0
        # 自动记录走过的每一步位置(回放整局用)。move() 会往里加。
        # 注意:这是"回放专用"的,你的 bot 想记别的(比如每格来过几次),
        #       自己另起一个变量,别占用 memory。
        self.memory = []

    def next_move(self):
        """你的策略:用 status() 看、用 move() 走。子类必须实现。"""
        raise NotImplementedError

    def status(self):
        """看四周,返回一个字典:
        {'up':'path'/'wall', 'down':.., 'left':.., 'right':.., 'pos':(x,y)}
        值:'path'=路(能走),'wall'=墙(过不去);'pos' 是当前坐标(方便记录/回放)。
        想看某个方向,自己取:status()["up"]。"""
        walls = game.look(self._grid, self._x, self._y)   # {'U':bool,...} True=墙
        state = {}
        for name, code in _DIR.items():
            state[name] = "wall" if walls[code] else "path"
        state["pos"] = (self._x, self._y)
        return state

    def move(self, direction):
        """朝 direction 走一步。走成功返回 1;前面是墙、没走成返回 0。
        走成功会自动把新位置记进 self.memory(回放用)。"""
        dx, dy = game.MOVES[_DIR[direction]]
        nx, ny, moved = game.try_step(self._grid, self._x, self._y, dx, dy)
        if moved:
            self._x = nx
            self._y = ny
            self.memory.append((self._x, self._y))   # 自动记下走到的新位置
        return 1 if moved else 0
