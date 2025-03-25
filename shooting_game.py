import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Game window setup
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Advanced")

# Load images
def load_image(name, size):
    return pygame.transform.scale(
        pygame.image.load(os.path.join(name)),
        size
    )

# Player setup
player_img = load_image("Shooter.png", (64, 64))
player_rect = player_img.get_rect()
player_rect.midbottom = (WIDTH // 2, HEIGHT - 10)
player_speed = 7

# Enemy setup
enemy_img = load_image("Enemy.png", (50, 50))
enemy_speed = 2  
enemies = []
spawn_rate = 80  

# Enemy bullet setup
enemy_bullet_color = (255, 255, 0)  
enemy_bullets = []
enemy_bullet_speed = 6
enemy_shoot_chance = 200  # 1 in 200 chance per enemy per frame to shoot

# Boss setup
boss_img = load_image("Boss.png", (150, 150))
boss_rect = None
boss_speed = 5  # Horizontal speed for boss movement
boss_health = 0
BOSS_SPAWN_SCORE = 200
boss_defeated = False  # Track if boss is defeated

# Boss bullet setup
boss_bullets = []
boss_bullet_color = (128, 0, 128)  # Purple for boss bullets
boss_bullet_speed = 8
boss_shoot_chance = 100  # 1 in 100 chance per frame to shoot

# Player bullet setup
bullet_img = load_image("bullet.png", (8, 20))
bullets = []
bullet_speed = 9

# Health system
max_health = 5
current_health = max_health
health_img = load_image("health.png", (30, 30))  # heart image

# Score system
score = 0
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

def show_message(text):
    """Display a full screen message before quitting."""
    WIN.fill(BLACK)
    message = large_font.render(text, True, WHITE)
    message_rect = message.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    WIN.blit(message, message_rect)
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()
    exit()

def draw_health():
    for i in range(current_health):
        WIN.blit(health_img, (10 + i * 35, 10))

def draw_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    WIN.blit(score_text, (10, 50))
    if boss_rect:
        boss_health_text = font.render(f"Boss Health: {boss_health}", True, RED)
        WIN.blit(boss_health_text, (WIDTH // 2 - 80, 10))

def check_collisions():
    global current_health, score, boss_health, boss_rect, boss_defeated

    # Player-enemy collision
    for enemy in enemies[:]:
        if player_rect.colliderect(enemy['rect']):
            current_health -= 1
            enemies.remove(enemy)
            if current_health <= 0:
                show_message("Game Over")

    # Bullet (player) - enemy collision
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy['rect']):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                break
        # Bullet (player) - boss collision
        if boss_rect and bullet.colliderect(boss_rect):
            if bullet in bullets:
                bullets.remove(bullet)
            boss_health -= 1
            score += 10
            if boss_health <= 0:
                boss_rect = None
                boss_defeated = True

    # Enemy bullet - player collision
    for eb in enemy_bullets[:]:
        if player_rect.colliderect(eb):
            enemy_bullets.remove(eb)
            current_health -= 1
            if current_health <= 0:
                show_message("Game Over")

    # Boss bullet - player collision
    for bb in boss_bullets[:]:
        if player_rect.colliderect(bb):
            boss_bullets.remove(bb)
            current_health -= 1
            if current_health <= 0:
                show_message("Game Over")

def main():
    global player_rect, score, boss_rect, boss_health, current_health, boss_defeated, boss_speed

    clock = pygame.time.Clock()
    running = True

    while running:
        WIN.fill(BLACK)
        clock.tick(60)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = pygame.Rect(
                        player_rect.centerx - 4,
                        player_rect.top,
                        8,
                        20
                    )
                    bullets.append(bullet)

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += player_speed

        # Move player bullets
        for bullet in bullets[:]:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets.remove(bullet)

        # Spawn enemies (if boss is not active)
        if not boss_rect and random.randint(1, spawn_rate) == 1:
            enemy_rect = pygame.Rect(
                random.randint(0, WIDTH - 50),
                -50,
                50,
                50
            )
            enemies.append({'rect': enemy_rect, 'speed': enemy_speed})

        # Enemies shooting bullets
        for enemy in enemies:
            if random.randint(1, enemy_shoot_chance) == 1:
                enemy_bullet = pygame.Rect(
                    enemy['rect'].centerx - 4,
                    enemy['rect'].bottom,
                    8,
                    20
                )
                enemy_bullets.append(enemy_bullet)

        # Spawn boss when score is reached and if not already active or defeated
        if score >= BOSS_SPAWN_SCORE and boss_rect is None and not boss_defeated:
            boss_rect = pygame.Rect(WIDTH // 2 - 75, 50, 150, 150)
            boss_health = 10

        # Boss shooting bullets
        if boss_rect and random.randint(1, boss_shoot_chance) == 1:
            boss_bullet = pygame.Rect(
                boss_rect.centerx - 4,
                boss_rect.bottom,
                8,
                20
            )
            boss_bullets.append(boss_bullet)

        # Move enemies
        for enemy in enemies[:]:
            enemy['rect'].y += enemy['speed']
            if enemy['rect'].top > HEIGHT:
                enemies.remove(enemy)

        # Move enemy bullets
        for eb in enemy_bullets[:]:
            eb.y += enemy_bullet_speed
            if eb.top > HEIGHT:
                enemy_bullets.remove(eb)

        # Move boss bullets
        for bb in boss_bullets[:]:
            bb.y += boss_bullet_speed
            if bb.top > HEIGHT:
                boss_bullets.remove(bb)

        # Boss movement (horizontal only)
        if boss_rect:
            boss_rect.x += boss_speed
            # Bounce off the edges
            if boss_rect.left <= 0 or boss_rect.right >= WIDTH:
                boss_speed *= -1

        check_collisions()

        # Draw player
        WIN.blit(player_img, player_rect)
        # Draw enemies
        for enemy in enemies:
            WIN.blit(enemy_img, enemy['rect'])
        # Draw boss if active
        if boss_rect:
            WIN.blit(boss_img, boss_rect)
        # Draw player bullets
        for bullet in bullets:
            WIN.blit(bullet_img, bullet)
        # Draw enemy bullets
        for eb in enemy_bullets:
            pygame.draw.rect(WIN, enemy_bullet_color, eb)
        # Draw boss bullets
        for bb in boss_bullets:
            pygame.draw.rect(WIN, boss_bullet_color, bb)
        # Draw health and score
        draw_health()
        draw_score()

        pygame.display.update()

        # If boss was defeated, display WIN screen and exit
        if boss_defeated:
            show_message("WIN")

    pygame.quit()

if __name__ == "__main__":
    main()
