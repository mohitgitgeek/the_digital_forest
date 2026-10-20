import random

GRID_SIZE = 15
VISIBILITY = 3
ROUNDS = 20
HEALTH_THRESHOLD = 50
ENERGY_THRESHOLD = 50
TERRAIN_SHIFT_MOVES = 5

TILE_EFFECTS = {
    "G": {"health": 0, "energy": 0, "name": "Grass"},
    "W": {"health": 0, "energy": 10, "name": "Water"},
    "T": {"health": 0, "energy": 0, "name": "Tree"},
    "DZ": {"health": -20, "energy": -10, "name": "Danger Zone"},
    "O": {"health": -5, "energy": -5, "name": "Obstacle"},
    "F": {"health": 15, "energy": 15, "name": "Fruit"},
}


class DigitalForestGame:
    def __init__(self):
        self.player_health = 100
        self.player_energy = 100
        self.player_position = [7, 7]
        self.moves_counter = 0
        self.round_num = 1
        self.grid = self.create_grid()
        self.game_over = False
        self.message_log = [
            "Welcome to The Digital Forest!",
            "Navigate through the forest while maintaining at least 50% health and energy.",
            "Special tiles (Water/Tree/Fruit/Danger Zone) will shift positions every five moves!",
        ]

    def create_grid(self):
        tiles = list(TILE_EFFECTS.keys())
        weights = [0.4, 0.15, 0.1, 0.1, 0.1, 0.15]
        return [[random.choices(tiles, weights)[0] for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def shift_terrain(self):
        special_tiles = ["W", "T", "F", "DZ"]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] in special_tiles:
                    self.grid[i][j] = "G"

        for tile in special_tiles:
            for _ in range(random.randint(5, 10)):
                x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                self.grid[x][y] = tile

        self.message_log.append("Terrain has shifted! Special tiles have moved.")

    def get_visible_area(self):
        visible_area = []
        for i in range(max(0, self.player_position[0] - VISIBILITY // 2), min(GRID_SIZE, self.player_position[0] + VISIBILITY // 2 + 1)):
            row = []
            for j in range(max(0, self.player_position[1] - VISIBILITY // 2), min(GRID_SIZE, self.player_position[1] + VISIBILITY // 2 + 1)):
                if i == self.player_position[0] and j == self.player_position[1]:
                    row.append("P")
                else:
                    row.append(self.grid[i][j])
            visible_area.append(row)
        return visible_area

    def display_game_state(self):
        print(f"\n--- Round {self.round_num}/{ROUNDS} ---")
        print(f"Health: {self.player_health}, Energy: {self.player_energy}")

        visible_area = self.get_visible_area()
        print("\nVisible Area (3x3):")
        for row in visible_area:
            print(" ".join(row))

        print("\nLegend:")
        print("P: Player")
        for key, value in TILE_EFFECTS.items():
            print(f"{key}: {value['name']}")

    def interact_with_tile(self):
        current_tile = self.grid[self.player_position[0]][self.player_position[1]]
        effects = TILE_EFFECTS[current_tile]

        self.player_health += effects["health"]
        self.player_energy += effects["energy"]

        message = f"You stepped on a '{effects['name']}' tile."
        if effects["health"] < 0 or effects["energy"] < 0:
            message += f" Lost {abs(effects['health'])} health and {abs(effects['energy'])} energy."
        if effects["health"] > 0 or effects["energy"] > 0:
            message += f" Gained {effects['health']} health and {effects['energy']} energy."

        self.player_health = min(max(self.player_health, 0), 100)
        self.player_energy = min(max(self.player_energy, 0), 100)
        self.message_log.append(message)

    def move_player(self, direction):
        direction = (direction or "").lower()

        moves = {
            "up": [-1, 0],
            "down": [1, 0],
            "left": [0, -1],
            "right": [0, 1],
        }

        if direction not in moves:
            return {"ok": False, "message": "Invalid direction! Please choose up/down/left/right."}

        new_position = [
            self.player_position[0] + moves[direction][0],
            self.player_position[1] + moves[direction][1],
        ]

        if not (0 <= new_position[0] < GRID_SIZE and 0 <= new_position[1] < GRID_SIZE):
            return {"ok": False, "message": "Cannot move outside the forest boundaries!"}

        if self.grid[new_position[0]][new_position[1]] == "T":
            return {"ok": False, "message": "Movement blocked by a tree!"}

        self.player_position = new_position
        self.moves_counter += 1

        if self.moves_counter % TERRAIN_SHIFT_MOVES == 0:
            self.shift_terrain()

        self.round_num += 1
        self.interact_with_tile()

        if self.player_health < HEALTH_THRESHOLD or self.player_energy < ENERGY_THRESHOLD:
            self.game_over = True
            self.message_log.append("Game Over! You failed to maintain sufficient health or energy.")
            return {"ok": True, "message": "Game Over! You failed to maintain sufficient health or energy.", "turn_result": "lost"}

        if self.round_num > ROUNDS:
            self.game_over = True
            self.message_log.append("Congratulations! You survived The Digital Forest!")
            return {"ok": True, "message": "Congratulations! You survived The Digital Forest!", "turn_result": "won"}

        return {"ok": True, "message": "Move accepted.", "turn_result": "continue"}

    def reset(self):
        self.__init__()

    def get_state(self):
        return {
            "round": self.round_num,
            "health": self.player_health,
            "energy": self.player_energy,
            "player_position": self.player_position,
            "visible_area": self.get_visible_area(),
            "moves_counter": self.moves_counter,
            "game_over": self.game_over,
            "message_log": self.message_log,
        }


def main():
    game = DigitalForestGame()
    print("Welcome to The Digital Forest!")
    print("Navigate through the forest while maintaining at least 50% health and energy.")
    print("Special tiles (Water/Tree/Fruit/Danger Zone) will shift positions every five moves!")

    while not game.game_over and game.round_num <= ROUNDS:
        game.display_game_state()
        game.interact_with_tile()

        if game.player_health < HEALTH_THRESHOLD or game.player_energy < ENERGY_THRESHOLD:
            print("\nGame Over! You failed to maintain sufficient health or energy.")
            break

        valid_move = False
        while not valid_move:
            direction = input("\nChoose your move (up/down/left/right): ").lower()
            if direction in ["up", "down", "left", "right"]:
                valid_move = game.move_player(direction)["ok"]
            else:
                print("Invalid direction! Please choose up/down/left/right.")

    if game.player_health >= HEALTH_THRESHOLD and game.player_energy >= ENERGY_THRESHOLD and not game.game_over:
        print("\nCongratulations! You survived The Digital Forest!")


if __name__ == "__main__":
    main()
