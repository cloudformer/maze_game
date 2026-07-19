# maze_game · 迷宫游戏(Python 亲子学习项目)

带孩子学 Python:自动生成迷宫 → 手动玩 → 各自写 bot 比赛。
开发原则:**一步一功能,做完验收,不破坏已验收的功能**。详见 [`v9999.md`](v9999.md)。

## 环境准备(只做一次)

用虚拟环境 venv,把依赖装在项目自己家里,不污染系统 Python。

```bash
# 1. 创建虚拟环境(生成一个 .venv/ 目录,不进 git)
python3 -m venv .venv

# 2. 进入虚拟环境
source .venv/bin/activate        # Mac / Linux
# .venv\Scripts\activate          # Windows(PowerShell / CMD)
```

命令行前面出现 `(.venv)` 就说明进对了。目前这一步是纯 Python 标准库,**还没有第三方依赖**;等做到 pygame 手动玩时,再 `pip install pygame` 并生成 `requirements.txt`。

## 怎么运行

```bash
python main.py gen 15 15      # 生成一张 15×15 的迷宫并打印
python main.py gen 25 25      # 换个尺寸;宽高可任意改,不写默认 15 15

python main.py play 15 15     # 放一个小人 '*',用 W/A/S/D 走
```

字符含义:`#` = 墙,空白 = 路,`*` = 你的小人,`E` = 出口。
`play` 里小人从左上角出发,走到右下角出口 `E` 即通关(会显示步数);
可一次输入多个键(如 `wwd`),按 `q` 退出。

## 项目结构

```
maze_game/
├── README.md      # 本文件:怎么装、怎么运行
├── v9999.md       # 设计文档:完整规划与开发纪律
├── main.py        # 程序入口:解析命令行,分发到各功能
├── mazegen.py     # 生成迷宫(递归回溯挖墙)
├── game.py        # 手动玩:放小人 '*',W/A/S/D 移动(地图只读)
├── .gitignore     # .venv/ __pycache__/ maze.db 不进 git
└── .venv/         # 虚拟环境(不进 git)
```

每个文件只管一件事,改哪个功能就只碰对应文件。

## 进度与路线图

- [x] **第 1 步** 生成并打印迷宫(`mazegen.py` + `main.py gen`)
- [x] **第 2 步** 放小人 `*`,W/A/S/D 走(地图只读,走动不改地图)
- [x] **第 3 步** 右下角出口 `E`,走到就通关(显示步数)
- [ ] 第 4 步 验证有路(BFS)+ 最短步数
- [ ] 第 5 步 难度评分
- [ ] 第 6 步 存进数据库(SQLite),同一张图可反复玩
- [ ] 第 7 步 pygame 窗口手动玩
- [ ] 第 8 步 bot 与竞技场

> 每完成一步就把上面打勾,并把「怎么运行」里的命令重跑一遍确认没弄坏旧功能。
