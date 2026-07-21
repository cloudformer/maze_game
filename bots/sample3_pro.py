# bots/smartbot.py
# Hulk's Bot:
# Uses BFS (Breadth First Search) to calculate the shortest path
# from the start position to the exit.
#
# It does not guess.
# It explores the maze mathematically and follows the shortest route.


from collections import deque

from bots.base import Bot
import maze


class SmartBot(Bot):

    bot_id = 3
    name = "Hulk's Bot"
    author = "Hulk"
    symbol = "💪"

    def __init__(self):
        super().__init__()

        # shortest route calculated by BFS
        self.route = None

        # current step in the route
        self.step_index = 0


    def find_route(self):
        """
        BFS search.
        Returns a list of coordinates:
        [(x1,y1), (x2,y2), ...]
        """

        start = (self._x, self._y)
        exit_pos = maze.find_exit(self._grid)

        queue = deque()

        queue.append(start)

        # remembers where every position came from
        parent = {
            start: None
        }


        while queue:

            current = queue.popleft()

            # reached exit
            if current == exit_pos:
                break


            x, y = current


            # check four directions
            for direction, (dx, dy) in maze.MOVES.items():

                nx = x + dx
                ny = y + dy

                # wall = cannot enter
                if maze.is_wall(self._grid, nx, ny):
                    continue


                next_pos = (nx, ny)


                # not visited yet
                if next_pos not in parent:

                    parent[next_pos] = current
                    queue.append(next_pos)



        # rebuild shortest path
        route = []

        current = exit_pos


        while current != start:

            route.append(current)

            current = parent[current]


        # BFS gives reverse order
        route.reverse()


        return route



    def go_to_exit(self):
        """
        Called by game.py every turn.
        Moves one step along the calculated shortest path.
        """


        # First turn: calculate the route
        if self.route is None:

            self.route = self.find_route()



        # already reached exit
        if self.step_index >= len(self.route):

            return



        # next target position
        next_x, next_y = self.route[self.step_index]


        dx = next_x - self._x
        dy = next_y - self._y



        # convert coordinate change into a direction
        for direction, (mx, my) in maze.MOVES.items():

            if (dx, dy) == (mx, my):

                self.move(direction)

                break



        self.step_index += 1