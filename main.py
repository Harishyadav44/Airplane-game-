import pygame
import random
import sys

# ================== CONSTANTS ==================
WIDTH, HEIGHT = 1300, 650
FPS = 30

PLAYER_SPEED = 10
BULLET_SPEED = 15
FIREBALL_SPEED = 6
BOSS_FIREBALL_SPEED = 8

ENEMY_MIN_SIZE = 80
ENEMY_MAX_SIZE = 90
ENEMY_MIN_SPEED = 3
ENEMY_MAX_SPEED = 5
ENEMY_FIRE_RATE = 60

BOSS_WIDTH = 200          # width SAME
BOSS_HEIGHT = 180         # height increased
BOSS_HEALTH_MAX = 60

POWERUP_SPEED = 3
DOUBLE_TIME = 5000

# ================== INIT ==================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Airplane Shooting Game - Boss Edition")
clock = pygame.time.Clock()

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,0)
ORANGE = (255,120,0)

# Fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 80)

# ================== IMAGES ==================
player_image = pygame.transform.scale(pygame.image.load("plane.png"), (70,70))
ufo_image = pygame.image.load("ufo.png")
fireball_image = pygame.transform.scale(pygame.image.load("enemy ball.png"), (20,20))
background_image = pygame.transform.scale(pygame.image.load("background1.jpg"), (WIDTH,HEIGHT))
boss_image = pygame.transform.scale(pygame.image.load("boss.png"), (BOSS_WIDTH,BOSS_HEIGHT))
logo_image = pygame.transform.scale(ufo_image, (200,170))

# ================== GAME VARIABLES ==================
player_pos = [WIDTH//2, HEIGHT-100]
player_health = 3
player_size = 70

bullets = []
fireballs = []
boss_fireballs = []

score = 0
level = 1

# Enemies
enemies = []
for _ in range(3):
    enemies.append({
        "pos":[random.randint(0,WIDTH-ENEMY_MIN_SIZE),0],
        "size":random.randint(ENEMY_MIN_SIZE,ENEMY_MAX_SIZE),
        "speed":random.randint(ENEMY_MIN_SPEED,ENEMY_MAX_SPEED),
        "health":2
    })

# Powerups
powerups = []
POWERUP_TYPES = ["health","double"]

# Boss
boss_active = False
boss_health = BOSS_HEALTH_MAX
boss_pos = [WIDTH//2 - BOSS_WIDTH//2, 20]
boss_speed = 4
boss_direction = 1

# ================== FUNCTIONS ==================
def spawn_powerup(x,y):
    if random.random() < 0.3:
        powerups.append({"pos":[x, max(y-20, 0)],"type":random.choice(POWERUP_TYPES)})

def start_screen():
    start_btn = pygame.Rect(WIDTH//2-100, HEIGHT//2, 200, 50)
    while True:
        screen.fill(BLACK)
        screen.blit(logo_image,(WIDTH//2-100,100))
        screen.blit(title_font.render("AIRPLANE GAME",True,GREEN),(WIDTH//2-220,300))
        pygame.draw.rect(screen,WHITE,start_btn)
        screen.blit(font.render("START",True,BLACK),(start_btn.x+70,start_btn.y+10))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and start_btn.collidepoint(e.pos):
                return

def game_over_screen():
    screen.fill(BLACK)
    screen.blit(title_font.render("GAME OVER",True,RED),(WIDTH//2-200,HEIGHT//3))
    screen.blit(font.render(f"Final Score: {score}",True,WHITE),(WIDTH//2-100,HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

# ================== MAIN LOOP ==================
def game_loop():
    global score, level, player_health
    global boss_active, boss_health, boss_pos, boss_direction, boss_speed
    global BOSS_FIREBALL_SPEED 

    background_y = 0
    double_bullet = False
    double_timer = 0
    game_over = False

    while not game_over:

        # EVENTS
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                if double_bullet:
                    bullets.append([player_pos[0]+10,player_pos[1]])
                    bullets.append([player_pos[0]+player_size-10,player_pos[1]])
                else:
                    bullets.append([player_pos[0]+player_size//2,player_pos[1]])

        # MOVEMENT
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_pos[0]>0: player_pos[0]-=PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player_pos[0]<WIDTH-player_size: player_pos[0]+=PLAYER_SPEED
        if keys[pygame.K_UP] and player_pos[1]>0: player_pos[1]-=PLAYER_SPEED
        if keys[pygame.K_DOWN] and player_pos[1]<HEIGHT-player_size: player_pos[1]+=PLAYER_SPEED

        # BACKGROUND
        background_y += 2
        if background_y >= HEIGHT: background_y = 0

        # ENEMIES
        if not boss_active:
            for enemy in enemies:
                enemy["pos"][1]+=enemy["speed"]
                if enemy["pos"][1]>HEIGHT:
                    enemy["pos"]=[random.randint(0,WIDTH-enemy["size"]),0]
                if random.randint(0,ENEMY_FIRE_RATE)==1:
                    fireballs.append([enemy["pos"][0],enemy["pos"][1]])

        # BULLETS MOVE
        for b in bullets[:]:
            b[1]-=BULLET_SPEED
            if b[1]<0: bullets.remove(b)

        # FIREBALL MOVE
        for f in fireballs[:]:
            f[1]+=FIREBALL_SPEED
            if f[1]>HEIGHT: fireballs.remove(f)

        # ===== ENEMY HIT (NO AUTO SCORE) =====
        for b in bullets[:]:
            for enemy in enemies:
                ex,ey = enemy["pos"]
                s = enemy["size"]
                if ex<b[0]<ex+s and ey<b[1]<ey+s:
                    bullets.remove(b)
                    enemy["health"]-=1
                    if enemy["health"]<=0:
                        score+=1
                        spawn_powerup(ex,ey)
                        enemy["pos"]=[random.randint(0,WIDTH-s),0]
                        enemy["health"]=2
                        if score%10==0: level+=1
                        if level%5==0:
                            boss_active=True
                            boss_health=BOSS_HEALTH_MAX
                    break

        # ===== BOSS =====
        if boss_active:
            boss_pos[0]+=boss_direction*boss_speed
            if boss_pos[0]<=0 or boss_pos[0]>=WIDTH-BOSS_WIDTH:
                boss_direction*=-1
            if random.randint(0,20)==1:
                boss_fireballs.append([boss_pos[0]+BOSS_WIDTH//2,boss_pos[1]+BOSS_HEIGHT])

        # ===== BOSS RAGE MODE =====
        if boss_active and boss_health < BOSS_HEALTH_MAX//2:
            boss_speed = 6
            BOSS_FIREBALL_SPEED = 12

        # ===== BOSS FIREBALL MOVE =====
        for bf in boss_fireballs[:]:
            bf[1]+=BOSS_FIREBALL_SPEED
            if bf[1]>HEIGHT: boss_fireballs.remove(bf)

        # ===== HIT PLAYER =====
        for f in fireballs[:]:
            if player_pos[0]<f[0]<player_pos[0]+player_size and player_pos[1]<f[1]<player_pos[1]+player_size:
                player_health-=1
                fireballs.remove(f)

        for bf in boss_fireballs[:]:
            if player_pos[0]<bf[0]<player_pos[0]+player_size and player_pos[1]<bf[1]<player_pos[1]+player_size:
                player_health-=2
                boss_fireballs.remove(bf)

        # ===== HIT BOSS (NO AUTO DEATH) =====
        if boss_active:
            for b in bullets[:]:
                if boss_pos[0]<b[0]<boss_pos[0]+BOSS_WIDTH and boss_pos[1]<b[1]<boss_pos[1]+BOSS_HEIGHT:
                    bullets.remove(b)
                    boss_health-=1
                    if boss_health<=0:
                        boss_active=False
                        score+=50
                        level+=1

        if player_health<=0:
            game_over=True

        # ===== POWERUPS =====
        for p in powerups[:]:
            p["pos"][1]+=POWERUP_SPEED
            if p["pos"][1]>HEIGHT: powerups.remove(p)
            if player_pos[0]<p["pos"][0]<player_pos[0]+player_size and player_pos[1]<p["pos"][1]<player_pos[1]+player_size:
                if p["type"]=="health": player_health+=1
                else:
                    double_bullet=True
                    double_timer=pygame.time.get_ticks()
                powerups.remove(p)

        if double_bullet and pygame.time.get_ticks()-double_timer>DOUBLE_TIME:
            double_bullet=False

        # ===== DRAW =====
        screen.blit(background_image,(0,background_y))
        screen.blit(background_image,(0,background_y-HEIGHT))
        screen.blit(player_image,player_pos)

        for enemy in enemies:
            screen.blit(pygame.transform.scale(ufo_image,(enemy["size"],enemy["size"])),enemy["pos"])

        for b in bullets:
            pygame.draw.circle(screen,YELLOW,(b[0],b[1]),6)

        for f in fireballs:
            screen.blit(fireball_image,(f[0],f[1]))

        if boss_active:
            screen.blit(boss_image,boss_pos)
            pygame.draw.rect(screen,RED,(WIDTH//2-200,20,400,20))
            pygame.draw.rect(screen,GREEN,(WIDTH//2-200,20,int(400*boss_health/BOSS_HEALTH_MAX),20))

        for bf in boss_fireballs:
            screen.blit(fireball_image,(bf[0],bf[1]))

        screen.blit(font.render(f"Score: {score}",True,WHITE),(10,10))
        screen.blit(font.render(f"Health: {player_health}",True,WHITE),(10,40))
        screen.blit(font.render(f"Level: {level}",True,WHITE),(10,70))

        pygame.display.flip()
        clock.tick(FPS)

    game_over_screen()

# ================== RUN ==================
start_screen()
game_loop()
