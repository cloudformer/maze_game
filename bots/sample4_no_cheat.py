# bots/sample4_no_cheat.py

from bots.base import Bot, DIRECTIONS

STEP = {
    "up": (0,-1),
    "down": (0,1),
    "left": (-1,0),
    "right": (1,0)
}

BACK = {
    "up":"down",
    "down":"up",
    "left":"right",
    "right":"left"
}

class Sample4(Bot):

    bot_id = 4
    name = "Sample4"
    author = "Hulk"
    symbol = "S4"

    def __init__(self):
        super().__init__()
        self.visits = {}
        self.last = None

    def go_to_exit(self):

        s = self.status()
        x, y = s["pos"]

        self.visits[(x,y)] = self.visits.get((x,y),0) + 1

        choices = []

        for d in DIRECTIONS:
            if s[d] == "path":

                dx, dy = STEP[d]
                pos = (x+dx,y+dy)

                if self.visits.get(pos,0) < 3:
                    choices.append(
                        (self.visits.get(pos,0), d)
                    )

        if not choices:
            for d in DIRECTIONS:
                if s[d] == "path":
                    choices.append((99,d))

        choices.sort()

        for _, d in choices:
            if d != BACK.get(self.last):
                self.move(d)
                self.last = d
                return

        self.move(choices[0][1])
        self.last = choices[0][1]