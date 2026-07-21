# 网页版计划(web-ui)

给迷宫游戏加一个**网页外壳**。原则:**核心逻辑全复用,只新写"外壳"。**
终端版(`game/menu/arena/replay`)完全不动,网页是**平行**的另一个入口。

## 架构:一个核心,两个平行外壳

```
              核心(两个外壳都调,一行不改)
        mazegen · maze · db · bots · (run_bot 助手)
                 ↑                        ↑
      终端外壳(已有)               网页外壳(新)
  game/menu/arena/replay        web.py + templates(html/js/css)
       └ 终端里玩 ┘                  └ 浏览器里玩 ┘
```

## 复用 vs 新写

| 层 | 文件 | 状态 |
|---|---|---|
| 核心 | `mazegen`(造图)`maze`(规则)`db`(存取)`bots`(机器人) | ♻️ 复用,不改 |
| 终端外壳 | `game / menu / arena / replay` | ✅ 保持不动 |
| 网页外壳 | `web.py`(薄路由)+ `templates/*.html` + JS/CSS | 🆕 新写 |

## 功能怎么映射到网页

网页里 bot/比赛/回放 归结成同一件事:**服务器用 Python 算出 path,浏览器放动画**。
所以网页不是四套逻辑,而是**一套 JS 动画 + 几个几行的薄路由**。

| 功能 | 终端(现在) | 网页 | 靠哪个核心 |
|---|---|---|---|
| 菜单/导航 | `menu.py` | HTML 页面 + 链接 | —(各写各的) |
| 单人玩 | `game.play` | `/move` 路由 + JS 键盘 | `maze.try_step/find_exit` |
| 看 bot | `game.watch_bot` | `/bot` 跑出 path + JS 动画 | `bots + maze` |
| 比赛 | `arena.py` | `/arena` 多条 path+排名 + JS 动画 | `bots + db` |
| 回放 | `replay.py` | `/replay` 从 db 取 path + JS 动画 | `db` |
| 排行榜 | `menu.show_leaderboard` | `/leaderboard` + HTML 表格 | `db.leaderboard` |

## 关键决定

1. **服务器 Python 说了算**,浏览器只画+收键盘。
   (bot 是 Python,只能在服务器跑;否则规则得用 JS 重写一遍。)
2. **框架用 Flask**(路由代码最短);状态先用**一个全局"当前这局"**(本地一次一人玩)。
3. 顺手抽一个核心助手 **`run_bot(grid, bot) → path`**(现在埋在 `game.watch_bot`),
   让终端动画、网页、arena 三处共用,不重复。

## 终端 vs 网页

| | 终端版 | 网页版 |
|---|---|---|
| 语言 | 只有 Python | Python + HTML + JS |
| 最烦的 | 跨平台读键、清屏 | 学一点前端 |
| 玩起来 | 朴素够用 | 好看、能发链接 |
| 学 Python | ✅ 最专注 | 会分心到前端 |

## 分步(先小后大)

1. **单人在浏览器里走**(方向键,复用 maze/mazegen)← 最小可跑
2. **看 bot 跑**(服务器出 path,浏览器动画)
3. 回放 / 比赛 / 排行榜(都是 "Python 出数据,网页画")

> 网页外壳其实很小:新写的就 `web.py` + 一个画格子/动画的前端页面。
