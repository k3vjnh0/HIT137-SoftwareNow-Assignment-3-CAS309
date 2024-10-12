import pygame
import random

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PLAYER_SIZE = (120, 120)
ENEMY_SIZE = (100, 100)
PROJECTILE_SIZE = (50, 50)
COLLECTIBLE_SIZE = (50, 50)
BOSS_SIZE = (150, 150)
FPS = 60
JUMP_SPEED = 10
GRAVITY = 0.5
PLAYER_HEALTH = 100
ENEMY_HEALTH = 30
BOSS_HEALTH = 300
PROJECTILE_DAMAGE = 10
BOSS_PROJECTILE_DAMAGE = 20
BOSS_JUMP_PROBABILITY = 0.01
BOSS_SHOOT_PROBABILITY = 0.02
ENEMY_SPAWN_INTERVAL = 2000
MAX_ENEMIES = 10
LEVEL_SCORES = {1: 10, 2: 20, 3: 30}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooting Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Load Images and Pre-scale
background_image = pygame.image.load("./img/background.jpg")
player_image = pygame.transform.scale(
    pygame.image.load("./img/player.gif"), PLAYER_SIZE
)
enemy_image = pygame.transform.scale(pygame.image.load("./img/enemy.png"), ENEMY_SIZE)
projectile_image = pygame.transform.scale(
    pygame.image.load("./img/bullet.png"), PROJECTILE_SIZE
)
boss_image = pygame.transform.scale(pygame.image.load("./img/boss.png"), BOSS_SIZE)
boss_image = pygame.transform.flip(boss_image, True, False)
boss_projectile_image = pygame.transform.scale(
    pygame.image.load("./img/boss_shot.png"), PROJECTILE_SIZE
)

# Load collectible images
ammo_image = pygame.transform.scale(
    pygame.image.load("./img/ammo_box.png"), COLLECTIBLE_SIZE
)
health_image = pygame.transform.scale(
    pygame.image.load("./img/health_box.png"), COLLECTIBLE_SIZE
)
coin_image = pygame.transform.scale(
    pygame.image.load("./img/coin.png"), COLLECTIBLE_SIZE
)


# Player Class
class Player(pygame.sprite.Sprite):
    """Represents the player in the game, allowing movement, jumping, and shooting."""

    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(
            self.image
        )  # Mask for pixel-perfect collision
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
        self.speed = 5
        self.velocity_y = 0
        self.health = PLAYER_HEALTH
        self.lives = 3
        self.is_jumping = False
        self.ammo = 20

    def update(self):
        """Updates the player's position and handles movement logic."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Handle jump
        if self.is_jumping:
            self.rect.y += self.velocity_y
            self.velocity_y += GRAVITY
            if self.rect.y >= SCREEN_HEIGHT - self.rect.height - 10:
                self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
                self.is_jumping = False

        # Keep player on screen
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))

    def jump(self):
        """Initiates the jump action if the player is not already jumping."""
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = -JUMP_SPEED

    def shoot(self):
        """Creates a projectile and reduces ammo if available."""
        if self.ammo > 0:
            self.ammo -= 1
            projectile = Projectile(self.rect.centerx, self.rect.centery)
            return projectile
        return None

    def draw(self, surface):
        """Draws the player on the screen."""
        surface.blit(self.image, self.rect)


# Projectile Class
class Projectile(pygame.sprite.Sprite):
    """Represents a projectile shot by the player."""

    def __init__(self, x, y):
        super().__init__()
        self.image = projectile_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(
            self.image
        )  # Mask for pixel-perfect collision
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 10

    def update(self):
        """Moves the projectile across the screen."""
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()


# Boss Projectile Class
class BossProjectile(pygame.sprite.Sprite):
    """Represents a projectile shot by the boss."""

    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = boss_projectile_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        direction_vector = pygame.math.Vector2(target_x - x, target_y - y).normalize()
        self.speed_x = direction_vector.x * 7
        self.speed_y = direction_vector.y * 7

    def update(self):
        """Moves the boss projectile toward the player's last known position."""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if (
            self.rect.right < 0
            or self.rect.left > SCREEN_WIDTH
            or self.rect.top > SCREEN_HEIGHT
            or self.rect.bottom < 0
        ):
            self.kill()


# Enemy Class
class Enemy(pygame.sprite.Sprite):
    """Represents an enemy that moves toward the player."""

    def __init__(self, x):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
        self.speed = random.randint(1, 3)
        self.health = ENEMY_HEALTH

    def update(self):
        """Moves the enemy from right to left and removes it when it goes off-screen."""
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

    def take_damage(self, damage):
        """Reduces enemy health when hit by a projectile."""
        self.health -= damage
        if self.health <= 0:
            self.kill()


# Boss Class
class Boss(pygame.sprite.Sprite):
    """Represents the final boss with more complex behavior."""

    def __init__(self, x):
        super().__init__()
        self.image = boss_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
        self.health = BOSS_HEALTH
        self.jump_speed = 12
        self.velocity_y = 0
        self.gravity = GRAVITY
        self.is_jumping = False

    def update(self):
        """Handles boss jumping behavior and movement."""
        if not self.is_jumping and random.random() < BOSS_JUMP_PROBABILITY:
            self.is_jumping = True
            self.velocity_y = -self.jump_speed

        if self.is_jumping:
            self.rect.y += self.velocity_y
            self.velocity_y += self.gravity
            if self.rect.y >= SCREEN_HEIGHT - self.rect.height - 10:
                self.rect.y = SCREEN_HEIGHT - self.rect.height - 10
                self.is_jumping = False

    def shoot(self, player):
        """Boss shoots projectiles aimed at the player's position."""
        return BossProjectile(
            self.rect.left, self.rect.centery, player.rect.centerx, player.rect.centery
        )

    def take_damage(self, damage):
        """Reduces boss health when hit by a projectile."""
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, surface):
        """Draws the boss's health bar."""
        bar_length = 150
        bar_height = 15
        fill = (self.health / BOSS_HEALTH) * bar_length
        outline_rect = pygame.Rect(
            self.rect.x + 15, self.rect.y - 25, bar_length, bar_height
        )
        fill_rect = pygame.Rect(self.rect.x + 15, self.rect.y - 25, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)


# Collectible Class
class Collectible(pygame.sprite.Sprite):
    """Represents a collectible item like ammo, health, or coins."""

    def __init__(self, kind):
        super().__init__()
        self.kind = kind
        if self.kind == "ammo":
            self.image = ammo_image
        elif self.kind == "health":
            self.image = health_image
        elif self.kind == "coin":
            self.image = coin_image

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(
            self.image
        )  # Mask for pixel-perfect collision
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)

    def update(self):
        """Moves collectible downwards and removes it if it goes off-screen."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# UI Drawing Functions
def draw_health_bar(surface, x, y, pct):
    """Draws a health bar at the given position."""
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


def draw_lives(surface, x, y, lives):
    """Displays the player's remaining lives on the screen."""
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    surface.blit(lives_text, (x, y))


def draw_ammo(surface, x, y, ammo):
    """Displays the player's remaining ammo on the screen."""
    ammo_text = font.render(f"Ammo: {ammo}", True, WHITE)
    surface.blit(ammo_text, (x, y))


# Screen Display Functions for Level Completion, Game Over, and Boss Defeat
def show_level_complete_screen(level):
    """Displays a 'Level Complete' screen when the player finishes a level."""
    screen.fill(BLACK)
    level_complete_text = font.render(f"Level {level} Complete!", True, WHITE)
    screen.blit(
        level_complete_text,
        (
            (SCREEN_WIDTH // 2 - level_complete_text.get_width() // 2),
            (SCREEN_HEIGHT // 2 - level_complete_text.get_height() // 2),
        ),
    )
    pygame.display.flip()
    pygame.time.wait(2000)


def show_congratulations_screen(score):
    """Displays a congratulation screen upon defeating the boss."""
    screen.fill(BLACK)
    congrats_text = font.render("Congratulations! You defeated the Boss!", True, WHITE)
    screen.blit(
        congrats_text,
        (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50),
    )
    leaderboard_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(
        leaderboard_text,
        (SCREEN_WIDTH // 2 - leaderboard_text.get_width() // 2, SCREEN_HEIGHT // 2),
    )

    # Buttons for retry and exit
    retry_button_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 60, 150, 50
    )
    exit_button_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 120, 150, 50
    )
    pygame.draw.rect(screen, GREEN, retry_button_rect)
    pygame.draw.rect(screen, RED, exit_button_rect)
    retry_text = font.render("Retry", True, WHITE)
    exit_text = font.render("Exit", True, WHITE)
    screen.blit(retry_text, (retry_button_rect.x + 40, retry_button_rect.y + 10))
    screen.blit(exit_text, (exit_button_rect.x + 50, exit_button_rect.y + 10))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if retry_button_rect.collidepoint(mouse_pos):
                    waiting = False
                    main()
                elif exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()


def show_game_over_screen(score):
    """Displays the game over screen when the player loses all lives."""
    screen.fill(BLACK)
    game_over_text = font.render("Game Over! You lost all your lives.", True, WHITE)
    screen.blit(
        game_over_text,
        (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50),
    )
    leaderboard_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(
        leaderboard_text,
        (SCREEN_WIDTH // 2 - leaderboard_text.get_width() // 2, SCREEN_HEIGHT // 2),
    )

    # Buttons for retry and exit
    retry_button_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 60, 150, 50
    )
    exit_button_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 120, 150, 50
    )
    pygame.draw.rect(screen, GREEN, retry_button_rect)
    pygame.draw.rect(screen, RED, exit_button_rect)
    retry_text = font.render("Retry", True, WHITE)
    exit_text = font.render("Exit", True, WHITE)
    screen.blit(retry_text, (retry_button_rect.x + 40, retry_button_rect.y + 10))
    screen.blit(exit_text, (exit_button_rect.x + 50, exit_button_rect.y + 10))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if retry_button_rect.collidepoint(mouse_pos):
                    waiting = False
                    main()
                elif exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()


# Pause screen function
def pause_screen():
    screen.fill(BLACK)
    pause_text = font.render("Paused", True, WHITE)
    resume_text = font.render("Press R to Resume or ESC to Exit", True, WHITE)

    screen.blit(
        pause_text,
        (
            (SCREEN_WIDTH // 2 - pause_text.get_width() // 2),
            (SCREEN_HEIGHT // 2 - pause_text.get_height() // 2 - 30),
        ),
    )
    screen.blit(
        resume_text,
        (
            (SCREEN_WIDTH // 2 - resume_text.get_width() // 2),
            (SCREEN_HEIGHT // 2 - resume_text.get_height() // 2 + 30),
        ),
    )
    pygame.display.flip()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    paused = False  # Resume the game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        clock.tick(5)  # Limit the frame rate while paused


# Instruction screen function
def instruction_screen():
    screen.fill(BLACK)
    title_text = font.render("Welcome to the Shooting Game", True, WHITE)
    instruction_text = font.render("Instructions:", True, WHITE)
    movement_text = font.render("Move: LEFT and RIGHT Arrow Keys", True, WHITE)
    jump_text = font.render("Jump: UP Arrow Key", True, WHITE)
    shoot_text = font.render("Shoot: SPACE Key", True, WHITE)
    pause_text = font.render("Pause: ESC Key", True, WHITE)
    start_text = font.render("Press any key to start", True, GREEN)

    # Displaying text on screen
    screen.blit(title_text, ((SCREEN_WIDTH - title_text.get_width()) // 2, 100))
    screen.blit(
        instruction_text, ((SCREEN_WIDTH - instruction_text.get_width()) // 2, 200)
    )
    screen.blit(movement_text, ((SCREEN_WIDTH - movement_text.get_width()) // 2, 250))
    screen.blit(jump_text, ((SCREEN_WIDTH - jump_text.get_width()) // 2, 300))
    screen.blit(shoot_text, ((SCREEN_WIDTH - shoot_text.get_width()) // 2, 350))
    screen.blit(pause_text, ((SCREEN_WIDTH - pause_text.get_width()) // 2, 400))
    screen.blit(start_text, ((SCREEN_WIDTH - start_text.get_width()) // 2, 500))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False  # Exit the loop when a key is pressed


# Main Game Loop
def main():
    """Main game loop where player, enemies, and boss logic are handled."""

    instruction_screen()

    player = Player()
    all_sprites = pygame.sprite.Group(player)
    projectiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    boss_projectiles = pygame.sprite.Group()

    score = 0
    defeated_enemies = 0
    level = 1
    boss = None
    boss_fight = False
    running = True
    last_enemy_spawn_time = pygame.time.get_ticks()
    last_collectible_spawn_time = pygame.time.get_ticks()

    # Initialize the game with a few enemies
    for _ in range(5):
        enemy = Enemy(SCREEN_WIDTH + random.randint(100, 300))
        all_sprites.add(enemy)
        enemies.add(enemy)

    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    projectile = player.shoot()
                    if projectile:
                        all_sprites.add(projectile)
                        projectiles.add(projectile)
                elif event.key == pygame.K_UP:
                    player.jump()
                elif event.key == pygame.K_ESCAPE:
                    pause_screen()

        all_sprites.update()

        # Enemy spawn logic
        if (
            not boss_fight
            and current_time - last_enemy_spawn_time > ENEMY_SPAWN_INTERVAL
            and len(enemies) < MAX_ENEMIES
        ):
            enemy = Enemy(SCREEN_WIDTH + random.randint(100, 300))
            all_sprites.add(enemy)
            enemies.add(enemy)
            last_enemy_spawn_time = current_time

        # Collectible spawn logic
        if current_time - last_collectible_spawn_time > random.randint(3000, 5000):
            kind = random.choice(["ammo", "health", "coin"])
            collectible = Collectible(kind)
            all_sprites.add(collectible)
            collectibles.add(collectible)
            last_collectible_spawn_time = current_time

        # Handle enemy collisions with player
        for enemy in enemies:
            if pygame.sprite.collide_mask(player, enemy):  # Pixel-perfect collision
                player.health -= 20
                enemy.kill()
                if player.health <= 0:
                    player.lives -= 1
                    if player.lives > 0:
                        player.health = PLAYER_HEALTH
                    else:
                        show_game_over_screen(score)
                        return

        # Handle projectile collisions with enemies
        for projectile in projectiles:
            enemy_hits = pygame.sprite.spritecollide(
                projectile, enemies, False, pygame.sprite.collide_mask
            )
            if enemy_hits:
                projectile.kill()
                for enemy in enemy_hits:
                    enemy.take_damage(PROJECTILE_DAMAGE)
                    if enemy.health <= 0:
                        enemy.kill()
                        score += 10
                        defeated_enemies += 1

        # Handle collectible collisions with player
        collectible_hits = pygame.sprite.spritecollide(
            player, collectibles, True, pygame.sprite.collide_mask
        )
        for collectible in collectible_hits:
            if collectible.kind == "ammo":
                player.ammo = min(player.ammo + 10, 40)
            elif collectible.kind == "health":
                player.health = min(player.health + 20, PLAYER_HEALTH)
            elif collectible.kind == "coin":
                score += 5

        # Level progression logic
        if defeated_enemies == LEVEL_SCORES[1] and level == 1:
            show_level_complete_screen(level)
            level += 1
        elif defeated_enemies == LEVEL_SCORES[2] and level == 2:
            show_level_complete_screen(level)
            level += 1

        # Boss fight initiation
        if level == 3 and defeated_enemies >= LEVEL_SCORES[3] and not boss_fight:
            boss = Boss(SCREEN_WIDTH - 200)
            all_sprites.add(boss)
            boss_fight = True
            for enemy in enemies:
                enemy.kill()

        # Drawing
        screen.blit(background_image, (0, 0))
        all_sprites.draw(screen)

        # Boss behavior during fight
        if boss:
            boss.update()
            if random.random() < BOSS_SHOOT_PROBABILITY:
                boss_projectile = boss.shoot(player)
                all_sprites.add(boss_projectile)
                boss_projectiles.add(boss_projectile)

            # Boss projectile collision with player
            boss_projectile_hits = pygame.sprite.spritecollide(
                player, boss_projectiles, True, pygame.sprite.collide_mask
            )
            if boss_projectile_hits:
                player.health -= BOSS_PROJECTILE_DAMAGE
                if player.health <= 0:
                    player.lives -= 1
                    if player.lives > 0:
                        player.health = PLAYER_HEALTH
                    else:
                        show_game_over_screen(score)
                        return

            # Player projectile collision with boss
            boss_hits = pygame.sprite.spritecollide(
                boss, projectiles, True, pygame.sprite.collide_rect
            )
            for projectile in boss_hits:
                boss.take_damage(PROJECTILE_DAMAGE)
                if boss.health <= 0:
                    show_congratulations_screen(score)
                    return

            # Draw boss health bar
            boss.draw_health_bar(screen)

        # Draw player UI (health, lives, ammo, score)
        draw_health_bar(screen, 10, 10, player.health)
        draw_lives(screen, SCREEN_WIDTH - 150, 10, player.lives)
        draw_ammo(screen, SCREEN_WIDTH - 150, 40, player.ammo)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 70))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
