# 迷宫游戏 · 操作手册

> 前提:装了 **Python 3.9+**(`python3 --version` 能看到版本)。

## 四步跑起来

### 1️⃣ 建并进虚拟环境 + 装依赖

```bash
python3 -m venv .venv
```

进入环境(**这一步 Mac / Windows 不同**):

| 系统 | 命令 |
|---|---|
| 🍎 Mac / Linux | `source .venv/bin/activate` |
| 🪟 Windows | `.venv\Scripts\activate` |

看到行首出现 `(.venv)` 就对了,然后装依赖:

```bash
pip install -r requirements.txt
```

### 2️⃣ 建数据库

```bash
python db.py
```
> 出现「数据库已就绪」即成功,硬盘上多出 `maze.db`。

### 3️⃣ 生成 9 关默认地图

```bash
python main.py gen all
```

### 4️⃣ 开玩

```bash
python main.py
```

出现「迷宫大冒险」菜单就成功了 🎉

> 以后每次开玩,只需先做 **第 1 步的「进入环境」**,再 `python main.py`。

---

## 菜单 & 操作(按键即选,不用回车)

| 键 | 模式 | 说明 |
|---|---|---|
| `1` | Single | 单人:`W/A/S/D` 走到出口 `E`,通关记成绩 |
| `2` | VS Mode | 双人:玩家1 `W/A/S/D` vs 玩家2 `方向键`,先到者赢 |
| `3` | Watch Bot | 看机器人自己走(建议小图 map1/map2) |
| `4` | Leaderboard | 排行榜(按地图分组,步数少者靠前) |
| `Q` | — | 退出 |

画面:`██` 墙 · 空白 路 · `E` 出口 · `**`/`()` 玩家 · `><` 机器人。

---

## 命令速查

| 命令 | 作用 |
|---|---|
| `python main.py` | 打开菜单(平时就用这个) |
| `python main.py gen all` | 生成 9 关默认地图 |
| `python main.py gen 21 21` | 生成一张自定义尺寸的图 |
| `python main.py play 3` | 直接玩 3 号地图 |

---

## 改设置(config.py)

| 设置 | 作用 |
|---|---|
| `WALL` `PATH` `EXIT` | 墙 / 路 / 出口 的样子(各 2 字符) |
| `PLAYERS` | 玩家图标清单 |
| `BOT_STEP_DELAY` | 看 bot 时每步停几秒(默认 0.2) |
| `MAP_SIZES` | 9 关的尺寸 |

---

## 写自己的机器人

新建 `bots/my_bot.py`:

```python
from bots.base import Bot

class MyBot(Bot):
    name = "小明1号"
    author = "小明"
    symbol = "@@"

    def next_move(self, pos, walls):
        # 可用:self.open_directions(walls) / self.direction / self.memory
        return self.open_directions(walls)[0]   # ← 换成你的策略
```

再到 `bots/__init__.py` 加一行 `from bots.my_bot import MyBot`。
规矩:只看 `pos`/`walls` 决策,**不碰地图**。

---

## 常见问题

| 现象 | 解决 |
|---|---|
| 行首没有 `(.venv)` | 没激活环境,重跑第 1 步的「进入环境」 |
| `ModuleNotFoundError: sqlalchemy` | 没装依赖:`pip install -r requirements.txt` |
| 选图是空的 / 「没有地图」 | 没生成:`python main.py gen all` |
| 方向键没反应 | 用真正的终端玩(有些 IDE 控制台不传方向键) |
