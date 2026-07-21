# menu.py —— Main menu: choose mode -> choose map -> play
# Maps are stored in the database. Each game (player or bot) is saved in plays.

import game
import db
import bots
import arena
import replay
import config
import mazegen


def list_maps():
    """Return all maps from database: [(id, width, height), ...]."""
    session = db.Session()
    rows = []

    for one_map in session.query(db.Map).order_by(db.Map.id).all():
        rows.append((one_map.id, one_map.width, one_map.height))

    session.close()
    return rows


def ensure_maps():
    """
    Create default maps if the database is empty.

    Maps are generated from config.MAP_SIZES:
    1 -> 5x5
    2 -> 10x10 (automatically becomes 11x11)
    ...
    9 -> 45x45
    """
    if len(list_maps()) == 0:
        print("Creating maps...")

        for map_id, size in config.MAP_SIZES.items():
            grid = mazegen.generate(size, size)
            saved_id = db.save_map(size, size, grid)
            print("Created map:", saved_id)


def choose_map():
    """Display maps and let the player choose one."""
    maps = list_maps()

    while True:
        game.clear_screen()

        print("========== MAP SELECT ==========\n")

        for (map_id, width, height) in maps:
            print("   %d    %dx%d" % (map_id, width, height))

        print("\nPress a number key to select a map, B to go back:")

        key = game.read_key()

        if key == "b":
            return None

        if key.isdigit():
            chosen = int(key)

            for (map_id, width, height) in maps:
                if map_id == chosen:
                    return chosen


def load_selected_map(map_id):
    """Load map from database safely."""
    grid = db.get_map(map_id)

    if grid is None:
        print("Map not found.")
        game.read_key()
        return None

    return grid


def single_game():
    """Single player mode."""
    map_id = choose_map()

    if map_id is None:
        return

    grid = load_selected_map(map_id)

    if grid is None:
        return

    players = game.make_players(1)

    winner = game.play(grid, players)

    me = players[0]

    if winner is None:
        print("\nYou did not reach the exit.")
        print("Press any key to return...")
        game.read_key()
        return

    print("\n🎉 Completed! Steps:", len(me["path"]))

    name = input("Enter your name: ").strip() or "Unknown"

    db.save_play(
        name,
        map_id,
        me["path"],
        me["symbol"]
    )

    print("Saved! Press any key to return...")
    game.read_key()


def vs_game():
    """Two player mode."""
    map_id = choose_map()

    if map_id is None:
        return

    grid = load_selected_map(map_id)

    if grid is None:
        return

    players = game.make_players(2)

    winner = game.play(grid, players)

    if winner is None:
        print("\nNobody reached the exit.")
        game.read_key()
        return

    print(
        "\n🏆 %s wins! Steps: %d"
        % (winner["label"], len(winner["path"]))
    )

    name = input("Winner name: ").strip() or winner["label"]

    db.save_play(
        name,
        map_id,
        winner["path"],
        winner["symbol"]
    )

    print("Saved! Press any key to return...")
    game.read_key()


def arena_game():
    """Bot competition mode."""
    map_id = choose_map()

    if map_id is None:
        return

    grid = load_selected_map(map_id)

    if grid is None:
        return

    game.clear_screen()

    print("========== AVAILABLE BOTS ==========\n")

    for cls in bots.ALL:
        print(
            "   %d   %s %s (author:%s)"
            % (
                cls.bot_id,
                cls.symbol,
                cls.name,
                cls.author
            )
        )

    print()

    raw = input(
        "Enter bot numbers (example: 1 2 3): "
    ).split()

    bot_list = []

    for token in raw:
        if token.isdigit():
            cls = bots.by_id(int(token))

            if cls is not None:
                bot_list.append(cls())

    if len(bot_list) == 0:
        print("No bots selected.")
        game.read_key()
        return

    max_steps = len(grid) * len(grid[0]) * 5

    arena.run(
        grid,
        map_id,
        bot_list,
        config.BOT_STEP_DELAY,
        max_steps
    )


def replay_game():
    """Replay saved games."""
    game.clear_screen()

    print("========== REPLAY ==========\n")

    raw = input(
        "Enter replay IDs: "
    ).split()

    play_ids = []

    for token in raw:
        if token.isdigit():
            play_ids.append(int(token))

    if len(play_ids) == 0:
        return

    replay.replay(play_ids)


def show_leaderboard():
    """Display leaderboard."""
    game.clear_screen()

    print("========== LEADERBOARD ==========\n")

    rows = db.leaderboard()

    if len(rows) == 0:
        print("No records yet.")

    else:
        current_map = None
        rank = 0

        for row in rows:

            if row["map_id"] != current_map:
                current_map = row["map_id"]
                rank = 0
                print("\n-- Map #%d --" % current_map)

            rank += 1

            print(
                " %d. %-10s %3d steps (play #%d)"
                %
                (
                    rank,
                    row["name"],
                    row["steps"],
                    row["id"]
                )
            )

    print("\nPress any key to return...")
    game.read_key()


def run():
    """Main menu loop."""

    # Create maps automatically on first run
    ensure_maps()

    while True:

        game.clear_screen()

        print("==============================")
        print("        MAZE ADVENTURE")
        print("==============================\n")

        print("   1    Single Player")
        print("   2    VS Mode")
        print("   3    Arena")
        print("   4    Replay")
        print("   5    Leaderboard")
        print("   Q    Quit\n")

        print("Select option:")

        key = game.read_key()

        if key == "q":
            print("Bye!")
            return

        try:

            if key == "1":
                single_game()

            elif key == "2":
                vs_game()

            elif key == "3":
                arena_game()

            elif key == "4":
                replay_game()

            elif key == "5":
                show_leaderboard()

        except KeyboardInterrupt:
            print("\nReturned to menu...")