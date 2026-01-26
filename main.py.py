import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1300, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Airplane Shooting Game - Boss Edition")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 100, 0)

# Font
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 80)

# ----------- IMAGE LOAD (same path as your old code) ----------------
logo_image = pygame.image.load('C:/Users/Harish Yaduvansi/OneDrive/Desktop/Games Harish code/AIRPLANE/ufo.png')
logo_image = pygame.transform.scale(logo_image, (200, 170))

player_image = pygame.image.load('C:/Users/Harish Yaduvansi/OneDrive/Desktop/Games Harish code/AIRPLANE/plane.png')
player_image = pygame.transform.scale(player_image, (70, 70))

ufo_image = pygame.image.load('C:/Users/Harish Yaduvansi/OneDrive/Desktop/Games Harish code/AIRPLANE/ufo.png')

fireball_image = pygame.image.load('C:/Users/Harish Yaduvansi/OneDrive/Desktop/Games Harish code/AIRPLANE/enemy ball.png')
fireball_image = pygame.transform.scale(fireball_image, (20, 20))

background_image = pygame.image.load('C:/Users/Harish Yaduvansi/OneDrive/Desktop/Games Harish code/AIRPLANE/background1.jpg')
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# -------------------------------------------------------------------

# Game variables
player_size = 70
player_pos = [WIDTH // 2, HEIGHT - player_size * 2]
player_speed = 10
player_health = 3

enemy_min_size = 80
enemy_max_size = 90
enemy_min_speed = 3
enemy_max_speed = 5

enemies = []
for _ in range(3):
    enemies.append({
        'pos': [random.randint(0, WIDTH - enemy_min_size), 0],
        'size': random.randint(enemy_min_size, enemy_max_size),
        'speed': random.randint(enemy_min_speed, enemy_max_speed),
        'health': 2
    })

bullet_size = 8
bullet_speed = 15
bullets = []

fireball_speed = 6
fireballs = []

score = 0
level = 1
clock = pygame.time.Clock()

# Powerups
powerups = []
POWERUP_TYPES = ["health", "double"]

# Boss
boss_active = False
boss_health = 40
boss_pos = [WIDTH // 2 - 100, 50]
boss_speed = 4
boss_direction = 1
boss_fireballs = []


def spawn_powerup(x, y):
    if random.random() < 0.3:  # 30% chance
        p_type = random.choice(POWERUP_TYPES)
        powerups.append({"pos": [x, y], "type": p_type})


def start_screen():
    start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    start = False
    while not start:
        screen.fill(BLACK)
        screen.blit(logo_image, (WIDTH // 4, HEIGHT // 6 - logo_image.get_height() // 5))
        title_text = title_font.render("PLAY & MAKE HIGH SCORE", True, GREEN)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 8 + 150))
        pygame.draw.rect(screen, WHITE, start_button_rect)
        start_text = font.render("START GAME", True, BLACK)
        screen.blit(start_text, (start_button_rect.x + 50, start_button_rect.y + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    start = True


def game_over_screen():
    screen.fill(BLACK)
    game_over_text = title_font.render("GAME OVER", True, RED)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()


def game_loop():
    global score, player_health, level, boss_active, boss_health, boss_pos
    background_y = 0
    double_bullet = False
    double_timer = 0
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if double_bullet:
                    bullets.append([player_pos[0] + 15, player_pos[1]])
                    bullets.append([player_pos[0] + player_size - 15, player_pos[1]])
                else:
                    bullets.append([player_pos[0] + player_size // 2, player_pos[1]])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_pos[0] > 0:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH - player_size:
            player_pos[0] += player_speed
        if keys[pygame.K_UP] and player_pos[1] > 0:
            player_pos[1] -= player_speed
        if keys[pygame.K_DOWN] and player_pos[1] < HEIGHT - player_size:
            player_pos[1] += player_speed

        # Background scroll
        background_y += 2
        if background_y >= HEIGHT:
            background_y = 0

        # Enemies
        if not boss_active:
            for enemy in enemies:
                enemy['pos'][1] += enemy['speed']
                if enemy['pos'][1] > HEIGHT:
                    enemy['pos'] = [random.randint(0, WIDTH - enemy['size']), 0]
                if random.randint(0, 60) == 1:
                    fireballs.append([enemy['pos'][0] + enemy['size'] // 2, enemy['pos'][1] + enemy['size']])

        # Bullets move
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)

        # Fireballs move
        for fireball in fireballs[:]:
            fireball[1] += fireball_speed
            if fireball[1] > HEIGHT:
                fireballs.remove(fireball)

        # Bullet collision with enemies
        for bullet in bullets[:]:
            for enemy in enemies:
                ex, ey = enemy['pos']
                size = enemy['size']
                if ex < bullet[0] < ex + size and ey < bullet[1] < ey + size:
                    bullets.remove(bullet)
                    enemy['health'] -= 1
                    if enemy['health'] <= 0:
                        score += 1
                        spawn_powerup(ex, ey)
                        enemy['pos'] = [random.randint(0, WIDTH - size), 0]
                        enemy['health'] = 2
                    if score % 10 == 0:
                        level += 1
                    if level % 5 == 0:  # Boss every 5 levels
                        boss_active = True
                    break

        # Bullet collision with boss
        if boss_active:
            for bullet in bullets[:]:
                bx, by = bullet
                if boss_pos[0] < bx < boss_pos[0] + 200 and boss_pos[1] < by < boss_pos[1] + 100:
                    bullets.remove(bullet)
                    boss_health -= 1
                    if boss_health <= 0:
                        boss_active = False
                        score += 20
                        boss_health = 40
                        boss_pos = [WIDTH // 2 - 100, 50]

        # Boss movement + attack
        if boss_active:
            boss_pos[0] += boss_direction * boss_speed
            if boss_pos[0] <= 0 or boss_pos[0] >= WIDTH - 200:
                boss_direction *= -1
            if random.randint(0, 20) == 1:
                boss_fireballs.append([boss_pos[0] + 100, boss_pos[1] + 100])

        # Boss fireball move
        for bf in boss_fireballs[:]:
            bf[1] += 8
            if bf[1] > HEIGHT:
                boss_fireballs.remove(bf)

        # Fireball hit player
        for fb in fireballs[:]:
            if (player_pos[0] < fb[0] < player_pos[0] + player_size and
                player_pos[1] < fb[1] < player_pos[1] + player_size):
                player_health -= 1
                fireballs.remove(fb)
                if player_health <= 0:
                    game_over = True

        for bf in boss_fireballs[:]:
            if (player_pos[0] < bf[0] < player_pos[0] + player_size and
                player_pos[1] < bf[1] < player_pos[1] + player_size):
                player_health -= 2
                boss_fireballs.remove(bf)
                if player_health <= 0:
                    game_over = True

        # Powerup collect
        for p in powerups[:]:
            if (player_pos[0] < p["pos"][0] < player_pos[0] + player_size and
                player_pos[1] < p["pos"][1] < player_pos[1] + player_size):
                if p["type"] == "health":
                    player_health += 1
                elif p["type"] == "double":
                    double_bullet = True
                    double_timer = pygame.time.get_ticks()
                powerups.remove(p)

        # Powerup timer
        if double_bullet and pygame.time.get_ticks() - double_timer > 5000:
            double_bullet = False

        # Draw background
        screen.blit(background_image, (0, background_y))
        screen.blit(background_image, (0, background_y - HEIGHT))

        # Draw player
        screen.blit(player_image, (player_pos[0], player_pos[1]))

        # Draw enemies
        if not boss_active:
            for enemy in enemies:
                scaled = pygame.transform.scale(ufo_image, (enemy['size'], enemy['size']))
                screen.blit(scaled, (enemy['pos'][0], enemy['pos'][1]))

        # Draw bullets
        for bullet in bullets:
            pygame.draw.circle(screen, YELLOW, (bullet[0], bullet[1]), bullet_size)

        # Draw fireballs
        for fb in fireballs:
            screen.blit(fireball_image, (fb[0], fb[1]))

        # Draw boss
        if boss_active:
            pygame.draw.rect(screen, ORANGE, (boss_pos[0], boss_pos[1], 200, 100))
            # Boss HP bar
            pygame.draw.rect(screen, RED, (WIDTH // 2 - 200, 20, 400, 20))
            pygame.draw.rect(screen, GREEN, (WIDTH // 2 - 200, 20, int(400 * boss_health / 40), 20))

        # Boss fireballs
        for bf in boss_fireballs:
            pygame.draw.circle(screen, ORANGE, (bf[0], bf[1]), 10)

        # Draw powerups
        for p in powerups:
            color = GREEN if p["type"] == "health" else ORANGE
            pygame.draw.rect(screen, color, (p["pos"][0], p["pos"][1], 20, 20))
            p["pos"][1] += 3

        # Score + Health + Level
        score_text = font.render(f"Score: {score}", True, WHITE)
        health_text = font.render(f"Health: {player_health}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))
        screen.blit(level_text, (10, 70))

        pygame.display.flip()
        clock.tick(30)

    game_over_screen()


# Run game
start_screen()
game_loop()
