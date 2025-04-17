import random

# Constants
GRID_SIZE = 15  # 15x15 grid
VISIBILITY = 3  # 3x3 visibility
ROUNDS = 20  # Total rounds to play
HEALTH_THRESHOLD = 50
ENERGY_THRESHOLD = 50
TERRAIN_SHIFT_MOVES = 5  # Terrain changes every 5 moves

# Initialize player attributes
player_health = 100
player_energy = 100
player_position = [7, 7]  # Start at the center of the grid
moves_counter = 0

# Tile effects
TILE_EFFECTS = {
    "G": {"health": 0, "energy": 0, "name": "Grass"},      # Grass: No effect
    "W": {"health": 0, "energy": +10, "name": "Water"},    # Water: Restore energy
    "T": {"health": 0, "energy": 0, "name": "Tree"},       # Tree: Block movement
    "DZ": {"health": -20, "energy": -10, "name": "Danger Zone"}, # Danger Zone: Lose health & energy
    "O": {"health": -5, "energy": -5, "name": "Obstacle"}, # Obstacle: Minor loss of health & energy
    "F": {"health": +15, "energy": +15, "name": "Fruit"}   # Fruit: Restore health & energy
}

# Generate a random grid with tiles
def create_grid():
    tiles = list(TILE_EFFECTS.keys())
    weights = [0.4, 0.15, 0.1, 0.1, 0.1, 0.15]  # Weighted distribution of tiles
    return [[random.choices(tiles, weights)[0] for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

grid = create_grid()

# Shift terrain positions every TERRAIN_SHIFT_MOVES moves
def shift_terrain():
    global grid
    
    special_tiles = ["W", "T", "F", "DZ"]  # Tiles to shift positions
    
    # Find current positions of special tiles and clear them from the grid (replace with grass)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] in special_tiles:
                grid[i][j] = "G"
    
    # Randomly place special tiles in new positions on the grid
    for tile in special_tiles:
        for _ in range(random.randint(5, 10)):  # Random number of each tile type
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            grid[x][y] = tile
    
    print("\n🌲 Terrain has shifted! Special tiles have moved.")

# Get visible area (3x3 around player)
def get_visible_area():
    visible_area = []
    for i in range(max(0, player_position[0] - VISIBILITY // 2), min(GRID_SIZE, player_position[0] + VISIBILITY // 2 + 1)):
        row = []
        for j in range(max(0, player_position[1] - VISIBILITY // 2), min(GRID_SIZE, player_position[1] + VISIBILITY // 2 + 1)):
            if i == player_position[0] and j == player_position[1]:
                row.append("P")  # Mark player position with 'P'
            else:
                row.append(grid[i][j])
        visible_area.append(row)
    return visible_area

# Display game state (visible area and stats)
def display_game_state(round_num):
    print(f"\n--- Round {round_num}/{ROUNDS} ---")
    print(f"Health: {player_health}, Energy: {player_energy}")
    
    visible_area = get_visible_area()
    print("\nVisible Area (3x3):")
    for row in visible_area:
        print(" ".join(row))
    
    print("\nLegend:")
    print("P: Player")
    for key, value in TILE_EFFECTS.items():
        print(f"{key}: {value['name']}")

# Apply tile effects based on current position
def interact_with_tile():
    global player_health, player_energy
    
    current_tile = grid[player_position[0]][player_position[1]]
    effects = TILE_EFFECTS[current_tile]
    
    player_health += effects["health"]
    player_energy += effects["energy"]
    
    print(f"You stepped on a '{TILE_EFFECTS[current_tile]['name']}' tile.")
    
    if effects["health"] < 0 or effects["energy"] < 0:
        print(f"Lost {abs(effects['health'])} health and {abs(effects['energy'])} energy.")
    
    if effects["health"] > 0 or effects["energy"] > 0:
        print(f"Gained {effects['health']} health and {effects['energy']} energy.")
    
    # Cap health and energy at max value of 100 and min value of zero
    player_health = min(max(player_health, 0), 100)
    player_energy = min(max(player_energy, 0), 100)

# Move the player in a direction
def move_player(direction):
    global player_position, moves_counter
    
    moves = {
        "up": [-1, 0],
        "down": [1, 0],
        "left": [0, -1],
        "right": [0, +1]
    }
    
    new_position = [
        player_position[0] + moves[direction][0],
        player_position[1] + moves[direction][1]
    ]
    
    if (0 <= new_position[0] < GRID_SIZE and 
        0 <= new_position[1] < GRID_SIZE):
        
        if grid[new_position[0]][new_position[1]] != "T":
            player_position = new_position
            moves_counter += 1
            
            if moves_counter % TERRAIN_SHIFT_MOVES == 0:
                shift_terrain()
            
            return True
        
        print("Movement blocked by a tree!")
        return False
    
    print("Cannot move outside the forest boundaries!")
    return False

# Main game loop
print("Welcome to The Digital Forest!")
print("Navigate through the forest while maintaining at least 50% health and energy.")
print("Special tiles (Water/Tree/Fruit/Danger Zone) will shift positions every five moves!")

for round_num in range(1, ROUNDS + 1):
    display_game_state(round_num)
    
    interact_with_tile()
    
    if player_health < HEALTH_THRESHOLD or player_energy < ENERGY_THRESHOLD:
        print("\nGame Over! You failed to maintain sufficient health or energy.")
        break
    
    valid_move = False
    while not valid_move:
        direction = input("\nChoose your move (up/down/left/right): ").lower()
        if direction in ["up", "down", "left", "right"]:
            valid_move = move_player(direction)
        else:
            print("Invalid direction! Please choose up/down/left/right.")

if player_health >= HEALTH_THRESHOLD and player_energy >= ENERGY_THRESHOLD:
    print("\nCongratulations! You survived The Digital Forest!")