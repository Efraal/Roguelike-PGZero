import pgzrun
import random
import math

from pgzero.constants import mouse
from pgzhelper import Actor

from entities import *

# Lógica do jogo
WIDTH=640
HEIGHT=360

ng = 0
lng = -1
current = "main_menu"
main_menu = True
game_over = False
theme = True
sfx = True

# ***** Criação dos Atores *****

# Cria o ponteiro do mouse
pointer = Actor("mouse", anchor=("left", "top"))
pointer.x = WIDTH + 50
pointer.y = HEIGHT + 50

#   ***** Botões do Menu *****
menu_buttons = []

# Cria o botão START
start = Actor("start")
start.x = WIDTH / 2
start.y = HEIGHT / 2 - 40

menu_buttons.append(start)

# Cria o botão Music
music_button = Actor("music_on")
music_button.x = WIDTH * 6 / 8
music_button.y = HEIGHT * 7 / 8

menu_buttons.append(music_button)

# Cria o botão SFX
sfx_button = Actor("sfx_on")
sfx_button.x = WIDTH * 7 / 8
sfx_button.y = HEIGHT * 7 / 8

menu_buttons.append(sfx_button)

# Cria o botão EXIT
exit = Actor("exit")
exit.x = WIDTH / 2
exit.y = HEIGHT / 2 + 40

menu_buttons.append(exit)

# ***** Botões do Game Over *****
gameover_buttons = []

# Cria o botão RETRY
retry = Actor("retry")
retry.x = WIDTH / 4
retry.y = HEIGHT / 3

gameover_buttons.append(retry)

# Cria o botão Main Menu
menu = Actor("menu_button")
menu.x = WIDTH / 4
menu.y = HEIGHT / 3 + 50

gameover_buttons.append(menu)
gameover_buttons.append(exit)

# Jogador
tank = Actor('player')
tank.y = HEIGHT/2
tank.x = WIDTH / 2
tank.angle = 90

# Criando o objeto do jogador
player = Player(tank)

# Vidas do jogador
def add_health():
    while True:
        if len(player.lives) == player.health:
            break
        health = Actor('heart_0')
        health.x = 16 + 24 * len(player.lives) + 1
        health.y = 16
        player.lives.append(health)

# Balas do Jogador
bullets = []
def player_bullets(pos):
    bx = pos[0]
    by = pos[1]
    for b in range(player.bullet_count):
        for d in range(player.doubled_bullets):
            new_bullet = Actor('bullet')
            new_bullet.angle = player.angle
            if player.angle == 0 or player.angle == 180:
                new_bullet.x = bx[b]
                new_bullet.y = by[d]
            else:
                new_bullet.x = bx[d]
                new_bullet.y = by[b]
            bullet = PlayerBullets(new_bullet)
            bullets.append(bullet)
    player.bullet_delay = math.ceil(60 * player.attack_speed)

# Lista de poderes
powerlist = ["attack_speed", "multi_shoot", "double_shoot", "extra_life", "movement_speed", "bullet_speed"]
powers = Powers()

# Gera os powerups
def generate_power():
    global ng
    current = 0
    while True:
        if powers.count // 2 == current:
            powers.count += 1
            break
        choice = random.randint(0, 5)
        if player.health == 3 and choice == 3:
            continue
        power = Actor(powerlist[choice])
        powers.new_powerup(power, current, ng)
        current += 1

# Lógica dos inimigos
enemies = []
enemy_bullets = []
enemy_count = 0
enemy_lifes = 0

# Criação dos inimigos
def generate_enemies():
    global ng
    global enemy_lifes, enemy_count
    while True:
        new_enemy = Actor('enemie')
        x = random.randrange(32, WIDTH - 32, 32)
        y = random.randrange(24, HEIGHT - 24, 32)
        if (
                (x < tank.x-64 or x > tank.x+64) and
                (y < tank.y-64 or y > tank.y+64)
        ):
            new_enemy.x = x
            new_enemy.y = y
        else:
            continue
        new_enemy.angle = 270
        new_enemy.move_count = 0
        enemy = Enemy(new_enemy)
        enemy.health = enemy_lifes
        enemies.append(enemy)
        if len(enemies) > enemy_count:
            break

# Criação das balas inimigas
def generate_enemy_bullets(enemy):
    new_bullet = Actor('enemie_bullet')
    new_bullet.angle = enemy.angle
    new_bullet.x = enemy.x
    new_bullet.y = enemy.y
    bullet = EnemyBullets(new_bullet)
    enemy_bullets.append(bullet)
    enemy.move_delay = 10
    enemy.bullet_delay = 15

# Cria os limites do jogo
walls = []
wall_count = 0
for x in range(2):
    for y in range(2):
        wall = Actor('wall', anchor=("left", "top"))
        if wall_count == 0:
            wall.angle = 0
        elif wall_count == 1:
            wall.angle = 90
        elif wall_count == 2:
            wall.angle = 270
        elif wall_count == 3:
            wall.angle = 180
        wall.x = x * WIDTH
        wall.y = y * HEIGHT
        walls.append(wall)
        wall_count += 1

# Movimento do ponteiro
def on_mouse_move(pos, rel, buttons):
    global current
    pointer.x = pos[0]
    pointer.y = pos[1]

# Interação com os botões
def on_mouse_down(pos, button):
    global current, theme, sfx
    if mouse.LEFT:
        if main_menu:
            if pointer.colliderect(start):
                current = "load"
            elif pointer.colliderect(music_button):
                theme = not theme
            elif pointer.colliderect(sfx_button):
                sfx = not sfx
        elif game_over:
            if pointer.colliderect(retry):
                current = "load"
            elif pointer.colliderect(menu):
                current = "main_menu"
        if pointer.colliderect(exit) and (game_over or main_menu):
                current = "exit"

def game_state():
    global current, main_menu, game_over
    global ng, lng
    global enemy_count, enemy_lifes

    if current == "game_over":
        main_menu = False
        game_over = True
    elif current == "main_menu":
        player.health = 3
        game_over = False
        main_menu = True
    elif current == "load":
        player.reset()
        ng = 0
        lng = -1
        powers.count = 0
        enemy_lifes = 0
        enemy_count = 0
        current = "on_going"
    elif current == "exit":
        quit()
    else:
        game_over = False
        main_menu = False

def music_state():
    global theme, game_over
    if theme:
        if not music.is_playing("main_theme"):
            music.play("main_theme")
    else:
        music.stop()

def update():
    global current

    # Inicia as vidas do jogador
    add_health()

    # Movimentação do jogador
    move = []
    if keyboard.A:
        move.append('A')
    if keyboard.D:
        move.append('D')
    if keyboard.W:
        move.append('W')
    if keyboard.S:
        move.append('S')
    player.sprite_update(move)
    player.move(move)
    player.collide(walls)
    player.update()

    # Controle de disparos do jogador
    if player.bullet_delay == 0:
        if keyboard.space:
            if sfx:
                sounds.shoot_sfx.play()
            player_bullets(player.shoot())
    else:
        player.bullet_delay -= 1

    # Colisão do powerup
    power_index = player.actor.collidelist(powers.powerups)
    if power_index != -1:
        powers.powerup(powers.powerups[power_index], player)
        del powers.powerups[power_index]

    # Física de colisões das balas
    for bullet in bullets:
        bullet.update_speed(player)
        bullet.move()
        bullet.collide(bullets, walls, enemies)

    # Comportamento dos inimigos
    for enemy in enemies:
        if enemy.move_delay == 0:
            enemy.move(walls, player)
            if enemy.bullet_delay == 0:
                if enemy.in_front(player):
                    if sfx:
                        sounds.shoot_sfx.play()
                    generate_enemy_bullets(enemy)
            else:
                enemy.bullet_delay -= 1
        else:
            enemy.move_delay -= 1

    # Atualiza as posições e colisões das balas inimigas
    for bullet in enemy_bullets:
        bullet.move()
        bullet.collide(enemy_bullets, walls, player)

    # Altera o estado do jogo
    game_state()
    music_state()

    if player.health <= 0:
        enemies.clear()
        bullets.clear()
        enemy_bullets.clear()
        current = "game_over"

def draw():
    global ng, lng
    global game_over, main_menu
    global enemy_count, enemy_lifes
    global sfx, theme

    # Mostra a tela de fim de jogo
    if game_over:
        buttons = gameover_buttons
        screen.fill((0, 0, 0))
        screen.draw.text('You Lose!', (260, 250), color=(255, 255, 255), fontsize=100)
        exit.x = WIDTH / 4
        for button in buttons:
            button.draw()
        pointer.draw()

    # Mostra o menu principal
    elif main_menu:
        buttons = menu_buttons
        if theme:
            music_button.image = "music_on"
        else:
            music_button.image = "music_off"
        if sfx:
            sfx_button.image = "sfx_on"
        else:
            sfx_button.image = "sfx_off"
        exit.x = WIDTH / 2
        screen.fill((255,255,255))
        for button in buttons:
            button.draw()
        pointer.draw()

    else:
        # Verifica o fim da rodada, quantas se passaram e faz modificações de acordo
        if len(enemies) == 0:
            if len(powers.powerups) == 0:
                if lng != ng:
                    generate_power()
                    lng = ng
                else:
                    if ng%2 == 0:
                        enemy_lifes += 1
                    else:
                        enemy_count += 1
                    generate_enemies()
                    ng += 1

        # Desenha os atores do jogo e o background
        screen.fill((170, 230, 30))
        for wall in walls:
            wall.draw()
        for lives in player.lives:
            lives.draw()
        for bullet in bullets:
            bullet.actor.draw()
        for bullet in enemy_bullets:
            bullet.actor.draw()
        for enemy in enemies:
            enemy.actor.draw()
        for power in powers.powerups:
            power.draw()
        player.actor.draw()

pgzrun.go()