from db import Session, Map

session = Session()

maps = session.query(Map).all()

print("Maps:", len(maps))

for m in maps:
    print(m.id, m.width, m.height)

session.close()