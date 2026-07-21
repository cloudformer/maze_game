# db.py —— 所有数据库相关代码都集中在这一个文件,用 SQLAlchemy(专业 ORM)。
#
# 什么是 ORM?
#   ORM = 对象关系映射。让我们用"写 Python 类"的方式描述数据库表,
#   用"操作 Python 对象"的方式读写数据,不用手写 SQL 语句。
#   一个类 = 一张表;类的一个实例 = 表里的一行;类的属性 = 表的列。
#
# 三张表,互相关联:
#   maps    地图:每生成一张迷宫存一行(编号、生成参数、地图内容)
#   players 玩家:谁在玩(名字);战绩不单独存,从对局里现算
#   plays   对局:谁 在哪张图上 玩了一局、走了多少步、什么时间
#           —— plays 用两个外键把 players 和 maps 连起来,是三张表的关联点。

import json
from datetime import datetime

from sqlalchemy import (create_engine, Column, Integer, String, Text,
                        DateTime, ForeignKey)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_FILE = "maze.db"

# engine = 通往数据库文件的"连接"。sqlite 的数据库就是硬盘上一个文件。
engine = create_engine("sqlite:///" + DB_FILE)

# Base = 所有表类的"祖宗",继承它就变成一张表。
Base = declarative_base()

# Session = 会话,用来读写数据(下面每个操作都会开一个)。
Session = sessionmaker(bind=engine)


class Map(Base):
    """地图表:每生成一张迷宫,就在这里存一行。"""
    __tablename__ = "maps"

    id = Column(Integer, primary_key=True)               # 编号(自动 1,2,3…)
    width = Column(Integer, nullable=False)              # 生成参数:宽
    height = Column(Integer, nullable=False)             # 生成参数:高
    grid = Column(Text, nullable=False)                  # 地图内容(二维 list 转成文字存)
    created_at = Column(DateTime, default=datetime.now)  # 生成时间

    # 反向关联:通过 map.plays 能拿到"这张图被玩过的所有对局"
    plays = relationship("Play", back_populates="map")

    # 数据库列只能存文字,不能直接存 Python 的 list;
    # 所以存进去前用 json 把二维表变成一串文字,读出来时再变回二维表。
    def set_grid(self, grid_list):
        self.grid = json.dumps(grid_list)

    def get_grid(self):
        return json.loads(self.grid)


class Player(Base):
    """玩家表:每个玩家一行。
    注意:战绩【不】单独存一列,而是从这个玩家的所有对局里现算(见 stats),
    这样数据只有一份,不会"战绩和对局对不上"。"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)   # 名字,不能重名
    created_at = Column(DateTime, default=datetime.now)

    # 反向关联:通过 player.plays 拿到"这个人玩过的所有 plays"
    plays = relationship("Play", back_populates="player")


class Play(Base):
    """plays 表(关联表):记录"某人在某张图上玩的一局"。人和 bot 都记在这里。
    两个外键 player_id / map_id 把 玩家 和 地图 连起来 —— 这是三张表的关联核心。
    只要有一个 play 的 id,就能拿到:谁玩的、哪张图、完整轨迹、用什么图标画。"""
    __tablename__ = "plays"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)  # 谁玩的
    map_id = Column(Integer, ForeignKey("maps.id"), nullable=False)        # 哪张图
    path = Column(Text, nullable=False)                    # 完整轨迹(位置清单的文字)
    symbol = Column(String, nullable=False)                # 回放时用什么图标画这条轨迹
    created_at = Column(DateTime, default=datetime.now)    # 什么时间玩的

    # 正向关联:通过 play.player / play.map 直接拿到对应的人和图
    player = relationship("Player", back_populates="plays")
    map = relationship("Map", back_populates="plays")

    # 轨迹是一串位置,数据库只能存文字,所以用 json 互转
    def set_path(self, path_list):
        self.path = json.dumps(path_list)

    def get_path(self):
        return json.loads(self.path)

    def steps(self):
        """步数 = 轨迹长度(走了几步)。"""
        return len(self.get_path())


def save_map(width, height, grid_list):
    """存一张新生成的地图,返回它的编号 id。"""
    session = Session()
    new_map = Map(width=width, height=height)
    new_map.set_grid(grid_list)     # 二维 list -> 存成文字
    session.add(new_map)
    session.commit()
    map_id = new_map.id             # 提交后才有自增 id,趁会话没关先取出来
    session.close()
    return map_id


def get_map(map_id):
    """按编号取一张地图,返回它的二维表 grid;没有这张图就返回 None。"""
    session = Session()
    found = session.get(Map, map_id)
    grid_list = None
    if found is not None:
        grid_list = found.get_grid()   # 文字 -> 二维 list
    session.close()
    return grid_list


def get_or_create_player(name):
    """按名字找玩家,没有就新建一个。返回玩家的 id。
    (这样同一个名字永远对应同一个玩家,战绩能累计。)"""
    session = Session()
    player = session.query(Player).filter_by(name=name).first()
    if player is None:
        player = Player(name=name)
        session.add(player)
        session.commit()
    player_id = player.id
    session.close()
    return player_id


def save_play(player_name, map_id, path_list, symbol):
    """存一局到 plays 表:谁(名字)、哪张图、完整轨迹、用什么图标画。
    人和 bot 都调这一个函数 —— 区别只是名字/轨迹从哪来,存法一样。
    步数不单独存,要用时 len(path) 就是步数。返回这条 play 的 id。"""
    player_id = get_or_create_player(player_name)   # 人和 bot 都当"玩家"存
    session = Session()
    play = Play(player_id=player_id, map_id=map_id, symbol=symbol)
    play.set_path(path_list)
    session.add(play)
    session.commit()
    play_id = play.id
    session.close()
    return play_id


def get_play(play_id):
    """按 id 取一局的全部信息,回放要用。返回字典;没有就返回 None。
    {'id', 'name', 'map_id', 'path'(位置清单), 'symbol'}"""
    session = Session()
    play = session.get(Play, play_id)
    result = None
    if play is not None:
        result = {
            "id": play.id,
            "name": play.player.name,
            "map_id": play.map_id,
            "path": play.get_path(),
            "symbol": play.symbol,
        }
    session.close()
    return result


def leaderboard(top=10):
    """读排行榜:按 地图、再按 步数(少的在前)排;每张图只取前 top 名(默认10)。
    步数 = len(path)。返回 [{'id', 'map_id', 'name', 'steps'}, ...]。
    带上 play 的 id,方便照着去"看录像"。"""
    session = Session()
    rows = []
    for play in session.query(Play).all():
        rows.append({
            "id": play.id,
            "map_id": play.map_id,
            "name": play.player.name,
            "size": "%dx%d" % (play.map.width, play.map.height),   # 地图大小(列表显示用)
            "steps": play.steps(),
        })
    session.close()
    rows.sort(key=lambda r: (r["map_id"], r["steps"]))

    # 每张图只留前 top 名
    result = []
    seen = {}
    for row in rows:
        count = seen.get(row["map_id"], 0)
        if count < top:
            result.append(row)
            seen[row["map_id"]] = count + 1
    return result


def init_db():
    """建表:把上面三张表在数据库文件里创建出来(已存在的表不会动)。
    每次程序启动调一次很安全,重复调不会重建、也不会丢数据。"""
    Base.metadata.create_all(engine)


def reset_db():
    """重置:先删掉三张表再重建 —— 会清空所有数据!
    开发阶段改了表结构(schema)时用它,让新结构生效。慎用。"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


# 直接运行 `python db.py` 时,建好库和表,方便第一次初始化。
if __name__ == "__main__":
    init_db()
    print("数据库已就绪:" + DB_FILE + "(表:maps / players / plays)")
