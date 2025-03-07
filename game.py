import pygame
import random
import sys
import math
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Treasure Hunter Adventure")

# Colors
BLUE = (100, 149, 237)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SAND = (244, 215, 177)
WATER = (65, 105, 225)
GRASS = (124, 252, 0)
ROCK = (128, 128, 128)
DARK_GREEN = (0, 100, 0)

# Game states
MENU = 0
PLAYING = 1
CHALLENGE = 2
GAME_OVER = 3

# Challenge types
COLLECTING = 0
SPENDING = 1
TREASURES = 2
SHARING = 3
MAPPING = 4
CODES = 5
SECRETS = 6

# Fonts
font_large = pygame.font.SysFont('comicsansms', 48)
font_medium = pygame.font.SysFont('comicsansms', 32)
font_small = pygame.font.SysFont('comicsansms', 24)

# Map generation
class Tile:
    def __init__(self, type, x, y, size):
        self.type = type
        self.x = x
        self.y = y
        self.size = size
        
    def draw(self, camera_x, camera_y):
        # Only draw tiles that are visible on screen
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        if -self.size <= screen_x <= WIDTH and -self.size <= screen_y <= HEIGHT:
            if self.type == "water":
                pygame.draw.rect(screen, WATER, (screen_x, screen_y, self.size, self.size))
            elif self.type == "sand":
                pygame.draw.rect(screen, SAND, (screen_x, screen_y, self.size, self.size))
            elif self.type == "grass":
                pygame.draw.rect(screen, GRASS, (screen_x, screen_y, self.size, self.size))
            elif self.type == "forest":
                pygame.draw.rect(screen, DARK_GREEN, (screen_x, screen_y, self.size, self.size))
            elif self.type == "rock":
                pygame.draw.rect(screen, ROCK, (screen_x, screen_y, self.size, self.size))

class Map:
    def __init__(self, width, height, tile_size):
        # Make the map 3 times bigger than the screen
        self.width = width * 3
        self.height = height * 3
        self.tile_size = tile_size
        self.tiles = []
        self.generate_map()
        
    def generate_map(self):
        # Generate a more realistic island map
        self.tiles = []
        num_tiles_x = self.width // self.tile_size
        num_tiles_y = self.height // self.tile_size
        
        # Start with all water
        for y in range(num_tiles_y):
            for x in range(num_tiles_x):
                self.tiles.append(Tile("water", x * self.tile_size, y * self.tile_size, self.tile_size))
        
        # Create multiple islands with Perlin noise (simplified)
        num_islands = random.randint(2, 4)
        
        for island in range(num_islands):
            center_x = random.randint(num_tiles_x // 4, num_tiles_x * 3 // 4)
            center_y = random.randint(num_tiles_y // 4, num_tiles_y * 3 // 4)
            island_radius = min(num_tiles_x, num_tiles_y) // random.randint(4, 6)
            
            for i, tile in enumerate(self.tiles):
                tile_x = i % num_tiles_x
                tile_y = i // num_tiles_x
                
                # Distance from center
                distance = math.sqrt((tile_x - center_x)**2 + (tile_y - center_y)**2)
                
                # Add some noise to make the coastline irregular
                noise = random.uniform(-0.2, 0.2)
                
                if distance < island_radius * (0.8 + noise):
                    # Inner island is grass
                    if distance < island_radius * 0.5:
                        if random.random() < 0.2:
                            self.tiles[i].type = "forest"  # Some forest patches
                        else:
                            self.tiles[i].type = "grass"
                            
                    # Edge of island is sand
                    else:
                        self.tiles[i].type = "sand"
                        
                    # Add some rocky areas
                    if random.random() < 0.05:
                        self.tiles[i].type = "rock"
                        
        # Add some random rock formations in water
        for _ in range(num_tiles_x * num_tiles_y // 100):
            x = random.randint(0, num_tiles_x - 1)
            y = random.randint(0, num_tiles_y - 1)
            index = y * num_tiles_x + x
            if index < len(self.tiles) and self.tiles[index].type == "water":
                self.tiles[index].type = "rock"
    
    def get_valid_position(self, size, exclude_tiles=None):
        if exclude_tiles is None:
            exclude_tiles = ["water", "rock"]
            
        valid_tiles = [tile for tile in self.tiles if tile.type not in exclude_tiles]
        
        if not valid_tiles:
            return (self.width // 2, self.height // 2)
            
        chosen_tile = random.choice(valid_tiles)
        return (chosen_tile.x + self.tile_size // 2, chosen_tile.y + self.tile_size // 2)
    
    def draw(self, camera_x, camera_y):
        for tile in self.tiles:
            tile.draw(camera_x, camera_y)

class Explorer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.size = 20
        self.treasures = 0
        self.keys = 0
        self.hearts = 3
        
    def draw(self, camera_x, camera_y):
        # Calculate screen position
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw explorer as a small person
        # Body
        pygame.draw.circle(screen, BLUE, (screen_x, screen_y), self.size)
        # Head
        pygame.draw.circle(screen, (255, 213, 170), (screen_x, screen_y - self.size - 5), self.size // 2)
        # Eyes
        pygame.draw.circle(screen, BLACK, (screen_x - 5, screen_y - self.size - 5), 3)
        pygame.draw.circle(screen, BLACK, (screen_x + 5, screen_y - self.size - 5), 3)
        
    def move(self, keys, game_map, camera_x, camera_y):
        new_x, new_y = self.x, self.y
        
        if keys[pygame.K_LEFT] and self.x > self.size:
            new_x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < game_map.width - self.size:
            new_x += self.speed
        if keys[pygame.K_UP] and self.y > self.size:
            new_y -= self.speed
        if keys[pygame.K_DOWN] and self.y < game_map.height - self.size:
            new_y += self.speed
            
        # Check if new position is valid (not on water or rocks)
        tile_x = new_x // game_map.tile_size
        tile_y = new_y // game_map.tile_size
        
        if 0 <= tile_x < game_map.width // game_map.tile_size and 0 <= tile_y < game_map.height // game_map.tile_size:
            tile_index = tile_y * (game_map.width // game_map.tile_size) + tile_x
            
            if 0 <= tile_index < len(game_map.tiles):
                tile_type = game_map.tiles[tile_index].type
                if tile_type not in ["water", "rock"]:
                    self.x, self.y = new_x, new_y
            
    def collides_with(self, entity):
        distance = math.sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2)
        return distance < self.size + entity.size

class Treasure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        
    def reset(self, x, y):
        self.x = x
        self.y = y
        
    def draw(self, camera_x, camera_y):
        # Calculate screen position
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Only draw if on screen
        if -self.size*2 <= screen_x <= WIDTH + self.size*2 and -self.size*2 <= screen_y <= HEIGHT + self.size*2:
            # Draw a treasure chest
            chest_width = self.size * 2
            chest_height = self.size * 1.5
            
            # Chest base
            pygame.draw.rect(screen, BROWN, (screen_x - chest_width//2, screen_y - chest_height//2, chest_width, chest_height))
            
            # Chest lid
            pygame.draw.rect(screen, BROWN, (screen_x - chest_width//2, screen_y - chest_height//2 - 5, chest_width, chest_height//3))
            
            # Gold highlights
            pygame.draw.rect(screen, GOLD, (screen_x - chest_width//2, screen_y - chest_height//2, chest_width, chest_height), 2)
            pygame.draw.rect(screen, GOLD, (screen_x - chest_width//2, screen_y - chest_height//2 - 5, chest_width, chest_height//3), 2)
            
            # Lock
            pygame.draw.rect(screen, GOLD, (screen_x - 5, screen_y - chest_height//2 - 3, 10, 8))

class Key:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 15
        self.collected = False
        self.rotation = 0
        
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        
    def draw(self, camera_x, camera_y):
        if not self.collected:
            # Calculate screen position
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            
            # Only draw if on screen
            if -self.size*2 <= screen_x <= WIDTH + self.size*2 and -self.size*2 <= screen_y <= HEIGHT + self.size*2:
                # Draw a more detailed key
                # Key head
                pygame.draw.circle(screen, GOLD, (screen_x, screen_y), self.size // 2)
                
                # Key shaft
                pygame.draw.rect(screen, GOLD, (screen_x, screen_y, self.size, self.size // 4))
                
                # Key teeth
                pygame.draw.rect(screen, GOLD, (screen_x + self.size, screen_y - self.size // 4, self.size // 4, self.size // 2))
                pygame.draw.rect(screen, GOLD, (screen_x + self.size * 0.7, screen_y - self.size // 4, self.size // 4, self.size // 2))

class Minimap:
    def __init__(self, game_map, size=150):
        self.game_map = game_map
        self.size = size
        self.scale_x = size / game_map.width
        self.scale_y = size / game_map.height
        self.image = None
        self.generate_minimap()
        
    def generate_minimap(self):
        # Create a surface for the minimap
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BLACK)
        
        # Draw simplified map tiles
        tile_size = self.game_map.tile_size * self.scale_x
        for tile in self.game_map.tiles:
            mini_x = tile.x * self.scale_x
            mini_y = tile.y * self.scale_y
            mini_size = max(1, int(tile_size))
            
            if tile.type == "water":
                pygame.draw.rect(self.image, WATER, (mini_x, mini_y, mini_size, mini_size))
            elif tile.type == "sand":
                pygame.draw.rect(self.image, SAND, (mini_x, mini_y, mini_size, mini_size))
            elif tile.type == "grass":
                pygame.draw.rect(self.image, GRASS, (mini_x, mini_y, mini_size, mini_size))
            elif tile.type == "forest":
                pygame.draw.rect(self.image, DARK_GREEN, (mini_x, mini_y, mini_size, mini_size))
            elif tile.type == "rock":
                pygame.draw.rect(self.image, ROCK, (mini_x, mini_y, mini_size, mini_size))
        
    def draw(self, explorer, treasure, key, camera_x, camera_y):
        # Draw minimap background
        screen.blit(self.image, (WIDTH - self.size - 10, 10))
        
        # Draw camera view area on minimap
        view_x = (camera_x / self.game_map.width) * self.size
        view_y = (camera_y / self.game_map.height) * self.size
        view_width = (WIDTH / self.game_map.width) * self.size
        view_height = (HEIGHT / self.game_map.height) * self.size
        pygame.draw.rect(screen, WHITE, (WIDTH - self.size - 10 + view_x, 10 + view_y, view_width, view_height), 1)
        
        # Draw explorer on minimap
        mini_explorer_x = WIDTH - self.size - 10 + explorer.x * self.scale_x
        mini_explorer_y = 10 + explorer.y * self.scale_y
        pygame.draw.circle(screen, BLUE, (mini_explorer_x, mini_explorer_y), 3)
        
        # Draw treasure on minimap
        mini_treasure_x = WIDTH - self.size - 10 + treasure.x * self.scale_x
        mini_treasure_y = 10 + treasure.y * self.scale_y
        pygame.draw.rect(screen, GOLD, (mini_treasure_x - 2, mini_treasure_y - 2, 4, 4))
        
        # Draw key on minimap if not collected
        if not key.collected:
            mini_key_x = WIDTH - self.size - 10 + key.x * self.scale_x
            mini_key_y = 10 + key.y * self.scale_y
            pygame.draw.circle(screen, WHITE, (mini_key_x, mini_key_y), 2)

class Game:
    def __init__(self):
        self.state = MENU
        self.map = Map(WIDTH, HEIGHT, 20)
        
        # Initialize camera position
        self.camera_x = 0
        self.camera_y = 0
        
        explorer_pos = self.map.get_valid_position(20)
        self.explorer = Explorer(*explorer_pos)
        
        treasure_pos = self.map.get_valid_position(20)
        self.treasure = Treasure(*treasure_pos)
        
        key_pos = self.map.get_valid_position(15)
        self.key = Key(*key_pos)
        
        self.minimap = Minimap(self.map)
        
        self.current_challenge = None
        self.challenge_type = None
        self.secret_answer = None
        self.explorer_answer = ""
        self.challenge_result = None
        self.rank = 1
        self.adventure_points = 0
        self.challenge_timer = 0
        self.challenge_time_limit = 20 * 60  # 20 seconds in frames at 60 FPS
        
    def generate_challenge(self):
        self.challenge_type = random.randint(0, 6)
        self.explorer_answer = ""
        self.challenge_result = None
        self.challenge_timer = self.challenge_time_limit
        
        if self.challenge_type == COLLECTING:
            a = random.randint(1, 10 * self.rank)
            b = random.randint(1, 10 * self.rank)
            self.current_challenge = f"The treasure chest needs a special code! Count {a} glowing stones and {b} magical pebbles together to find the magic total."
            self.secret_answer = str(a + b)
            
        elif self.challenge_type == SPENDING:
            a = random.randint(10 * self.rank, 20 * self.rank)
            b = random.randint(1, a)
            self.current_challenge = f"Oh no! The treasure is locked! If you had {a} gold coins and spent {b} coins on supplies, how many coins remain in your pouch?"
            self.secret_answer = str(a - b)
            
        elif self.challenge_type == TREASURES:
            a = random.randint(1, 5 + self.rank)
            b = random.randint(1, 10)
            self.current_challenge = f"You found {a} treasure chests, each with {b} gems. How many gems have you discovered in total?"
            self.secret_answer = str(a * b)
            
        elif self.challenge_type == SHARING:
            b = random.randint(1, 5 + self.rank)
            a = b * random.randint(1, 10)
            self.current_challenge = f"You need to share {a} gold coins equally among {b} crew members. How many coins does each crew member receive?"
            self.secret_answer = str(a // b)
            
        elif self.challenge_type == MAPPING:
            a = random.randint(30, 100)
            self.current_challenge = f"Map reading: About how many paces to the nearest ten is {a} paces to the treasure?"
            rounded = round(a / 10) * 10
            self.secret_answer = str(rounded)
            
        elif self.challenge_type == CODES:
            start = random.randint(1, 5)
            step = random.randint(2, 5)
            sequence = [start + step*i for i in range(4)]
            self.current_challenge = f"Decode the secret sequence: {sequence[0]}, {sequence[1]}, {sequence[2]}, {sequence[3]}, ?"
            self.secret_answer = str(sequence[3] + step)
            
        elif self.challenge_type == SECRETS:
            shapes = ["triangle", "square", "pentagon", "hexagon"]
            shape = random.choice(shapes)
            if shape == "triangle":
                self.current_challenge = "How many edges does a triangular amulet have?"
                self.secret_answer = "3"
            elif shape == "square":
                self.current_challenge = "How many edges does a square treasure map have?"
                self.secret_answer = "4"
            elif shape == "pentagon":
                self.current_challenge = "How many edges does a pentagonal coin have?"
                self.secret_answer = "5"
            elif shape == "hexagon":
                self.current_challenge = "How many edges does a hexagonal gem have?"
                self.secret_answer = "6"
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.state == MENU and event.key == pygame.K_SPACE:
                    self.state = PLAYING
                    
                elif self.state == GAME_OVER and event.key == pygame.K_SPACE:
                    self.__init__()  # Reset the game
                    
                elif self.state == CHALLENGE:
                    if event.key == pygame.K_RETURN:
                        if self.explorer_answer == self.secret_answer:
                            self.challenge_result = True
                            self.adventure_points += 100 * self.rank
                            self.explorer.treasures += 1
                            if self.explorer.treasures % 5 == 0:
                                self.rank += 1
                            self.state = PLAYING
                            
                            # Reset treasure and key in new positions
                            treasure_pos = self.map.get_valid_position(20)
                            self.treasure.reset(*treasure_pos)
                            
                            key_pos = self.map.get_valid_position(15)
                            self.key.reset(*key_pos)
                        else:
                            self.challenge_result = False
                            self.explorer.hearts -= 1
                            if self.explorer.hearts <= 0:
                                self.state = GAME_OVER
                            else:
                                self.generate_challenge()  # Try again
                    elif event.key == pygame.K_BACKSPACE:
                        self.explorer_answer = self.explorer_answer[:-1]
                    elif event.unicode.isdigit():
                        self.explorer_answer += event.unicode
    
    def update(self):
        if self.state == PLAYING:
            keys = pygame.key.get_pressed()
            self.explorer.move(keys, self.map, self.camera_x, self.camera_y)
            
            # Update camera to follow explorer
            self.camera_x = self.explorer.x - WIDTH // 2
            self.camera_y = self.explorer.y - HEIGHT // 2
            
            # Keep camera within map bounds
            self.camera_x = max(0, min(self.camera_x, self.map.width - WIDTH))
            self.camera_y = max(0, min(self.camera_y, self.map.height - HEIGHT))
            
            # Check for key collection
            if not self.key.collected and self.explorer.collides_with(self.key):
                self.key.collected = True
                self.explorer.keys += 1
                
            # Check for treasure collection
            if self.key.collected and self.explorer.collides_with(self.treasure):
                self.state = CHALLENGE
                self.generate_challenge()
                
        elif self.state == CHALLENGE:
            self.challenge_timer -= 1
            if self.challenge_timer <= 0:
                self.challenge_result = False
                self.explorer.hearts -= 1
                if self.explorer.hearts <= 0:
                    self.state = GAME_OVER
                else:
                    self.generate_challenge()  # Try again
    
    def draw(self):
        # Clear the screen
        screen.fill(BLACK)
        
        if self.state == MENU:
            # Draw title
            title = font_large.render("Treasure Hunter Adventure", True, GOLD)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            
            # Draw start message
            start_msg = font_medium.render("Press SPACE to start your adventure!", True, WHITE)
            screen.blit(start_msg, (WIDTH//2 - start_msg.get_width()//2, HEIGHT//2))
            
            # Draw instructions
            instructions = [
                "Use arrow keys to guide your explorer",
                "Find magical keys to unlock ancient treasures",
                "Solve mysterious riddles to claim your rewards!",
                "Explore the larger world with multiple islands!"
            ]
            
            y_offset = HEIGHT * 2 // 3
            for instruction in instructions:
                text = font_small.render(instruction, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
                y_offset += 40
                
        elif self.state == PLAYING:
            # Draw map
            self.map.draw(self.camera_x, self.camera_y)
            
            # Draw game elements
            self.treasure.draw(self.camera_x, self.camera_y)
            if not self.key.collected:
                self.key.draw(self.camera_x, self.camera_y)
            self.explorer.draw(self.camera_x, self.camera_y)
                
            # Draw minimap
            self.minimap.draw(self.explorer, self.treasure, self.key, self.camera_x, self.camera_y)
                
            # Draw HUD
            score_text = font_small.render(f"Adventure Points: {self.adventure_points}", True, WHITE)
            level_text = font_small.render(f"Explorer Rank: {self.rank}", True, WHITE)
            treasures_text = font_small.render(f"Treasures: {self.explorer.treasures}", True, WHITE)
            lives_text = font_small.render(f"Hearts: {self.explorer.hearts}", True, WHITE)
            keys_text = font_small.render(f"Magic Key: {'Yes' if self.key.collected else 'No'}", True, WHITE)
            location_text = font_small.render(f"Location: ({int(self.explorer.x)}, {int(self.explorer.y)})", True, WHITE)
            
            # Draw HUD background
            pygame.draw.rect(screen, BLACK, (0, 0, 200, 190))
            
            screen.blit(score_text, (10, 10))
            screen.blit(level_text, (10, 40))
            screen.blit(treasures_text, (10, 70))
            screen.blit(lives_text, (10, 100))
            screen.blit(keys_text, (10, 130))
            screen.blit(location_text, (10, 160))
            
        elif self.state == CHALLENGE:
            # Draw game map with reduced opacity in background
            self.map.draw(self.camera_x, self.camera_y)
            
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Black with alpha
            screen.blit(overlay, (0, 0))
            
            # Draw challenge background - antique scroll
            scroll_width = WIDTH*2//3
            scroll_height = HEIGHT*2//3
            scroll_x = WIDTH//2 - scroll_width//2
            scroll_y = HEIGHT//2 - scroll_height//2
            
            # Scroll background
            pygame.draw.rect(screen, (244, 227, 188), (scroll_x, scroll_y, scroll_width, scroll_height))
            
            # Scroll edges
            pygame.draw.rect(screen, (198, 169, 91), (scroll_x, scroll_y, scroll_width, scroll_height), 5)
            
            # Scroll decorative elements
            pygame.draw.circle(screen, (198, 169, 91), (scroll_x + scroll_width//2, scroll_y + 20), 10)
            pygame.draw.circle(screen, (198, 169, 91), (scroll_x + scroll_width//2, scroll_y + scroll_height - 20), 10)
            
            # Draw challenge text
            challenge_text = font_medium.render("Ancient Riddle!", True, BROWN)
            screen.blit(challenge_text, (WIDTH//2 - challenge_text.get_width()//2, HEIGHT//4))
            
            # Wrap challenge text to fit the box
            words = self.current_challenge.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                test_width = font_small.size(test_line)[0]
                
                if test_width < scroll_width - 40:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            
            lines.append(current_line)
            
            y_offset = HEIGHT//3
            for line in lines:
                text = font_small.render(line, True, BLACK)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
                y_offset += 30
            
            # Draw answer box
            pygame.draw.rect(screen, WHITE, (WIDTH//3, HEIGHT*2//3 - 40, WIDTH//3, 40))
            pygame.draw.rect(screen, BROWN, (WIDTH//3, HEIGHT*2//3 - 40, WIDTH//3, 40), 2)
            answer_text = font_small.render(self.explorer_answer, True, BLACK)
            screen.blit(answer_text, (WIDTH//2 - answer_text.get_width()//2, HEIGHT*2//3 - 30))
            
            # Draw timer
            timer_width = (self.challenge_timer / self.challenge_time_limit) * scroll_width
            pygame.draw.rect(screen, (198, 169, 91), (scroll_x, scroll_y + scroll_height - 30, timer_width, 10))
            
            # Draw instructions
            instructions = font_small.render("Write your answer and press ENTER", True, BLACK)
            screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT*5//6))
            
        elif self.state == GAME_OVER:
            # Draw a dark overlay on the map
            self.map.draw(self.camera_x, self.camera_y)
            
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))  # Black with alpha
            screen.blit(overlay, (0, 0))
            
            # Draw game over screen
            game_over_text = font_large.render("Adventure Complete!", True, GOLD)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//4))
            
            score_text = font_medium.render(f"Final Adventure Points: {self.adventure_points}", True, WHITE)
            treasures_text = font_medium.render(f"Treasures Discovered: {self.explorer.treasures}", True, WHITE)
            level_text = font_medium.render(f"Explorer Rank: {self.rank}", True, WHITE)
            
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 40))
            screen.blit(treasures_text, (WIDTH//2 - treasures_text.get_width()//2, HEIGHT//2 + 10))
            screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 60))
            
            restart_text = font_medium.render("Press SPACE to start a new adventure", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT*3//4))
            
        # Update the display
        pygame.display.flip()

# Main game loop
def main():
    game = Game()
    clock = pygame.time.Clock()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(60)  # 60 FPS

if __name__ == "__main__":
    main()
