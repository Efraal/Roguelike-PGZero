import random
import math

frame = 0
tick = 0

# Classe mãe de todas as entidades
class Entity:
    def __init__(self, actor):
        self.actor = actor
        self.y = self.actor.y
        self.x = self.actor.x
        self.angle = self.actor.angle
        self.speed = 1

# Classe do jogador
class Player(Entity):
    def __init__(self, actor):
        super().__init__(actor)
        self.bullet_delay = 0
        self.doubled_bullets = 1
        self.bullet_count = 1
        self.attack_speed = 1
        self.bullet_speed = 5
        self.health = 3
        self.original_attributes = {}
        for attr, value in self.__dict__.items():
            self.original_attributes [attr] = value
        self.lives = []
        self.original = []
        self.standby = ["player_sb0", "player_sb1"]
        self.running = ["player_run0", "player_run1", "player_run2", "player_run3"]

    # Movimentação do jogador
    def move(self, key):
        self.original = (self.x, self.y)
        if 'A' in key:
            self.x -= round(2 * self.speed, 2)
            self.angle = 180
        if 'D' in key:
            self.x += round(2 * self.speed, 2)
            self.angle = 0
        if 'W' in key:
            self.y -= round(2 * self.speed, 2)
            self.angle = 90
        if 'S' in key:
            self.y += round(2 * self.speed, 2)
            self.angle = 270

    # Colisão com as paredes do jogo
    def collide(self, walls):
        if self.actor.collidelist(walls) != -1:
            self.x = self.original[0]
            self.y = self.original[1]
        if self.actor.collidelist(walls) == 0:
            self.x += 1
        elif self.actor.collidelist(walls) == 1:
            self.y -= 1
        elif self.actor.collidelist(walls) == 2:
            self.y += 1
        elif self.actor.collidelist(walls) == 3:
            self.x -= 1

    # Atualiza a posição do jogador
    def update(self):
        self.actor.x = self.x
        self.actor.y = self.y
        self.actor.angle = self.angle

    def sprite_update(self, key):
        global tick, frame
        if key == []:
            if frame > len(self.standby)-1:
                frame = 0
            self.actor.image = self.standby[frame]
        else:
            if frame > len(self.running)-1:
                frame = 0
            self.actor.image = self.running[frame]
        tick += 1
        if tick % 8 == 0:
            frame += 1

    # Define a quantidade e de onde sairão as balas
    def shoot(self):
        bx = []
        by = []
        for b in range(self.bullet_count):
            if self.angle == 0:
                bx.append(self.x - 16 + 8 * b)
            elif self.angle == 180:
                bx.append(self.x + 16 - 8 * b)
            elif self.angle == 90:
                by.append(self.y + 16 - 8 * b)
            elif self.angle == 270:
                by.append(self.y - 16 + 8 * b)
            for d in range(self.doubled_bullets):
                if self.angle == 0 or self.angle == 180:
                    by.append((self.y - 16) + (32 * (d + 1) / (self.doubled_bullets + 1)))
                elif self.angle == 90 or self.angle == 270:
                    bx.append((self.x - 16) + (32 * (d + 1) / (self.doubled_bullets + 1)))
        shots = (bx, by)
        return shots

    def reset(self):
        for attr, value in self.__dict__.items():
            if attr == "lives":
                break
            original = self.original_attributes[attr]
            if attr == 'x':
                self.x = original
            if attr == 'y':
                self.y = original
            if attr == "angle":
                self.angle = original
            if attr == "speed":
                self.speed = original
            if attr == "bullet_delay":
                self.bullet_delay = original
            if attr == "doubled_bullets":
                self.doubled_bullets = original
            if attr == "bullet_count":
                self.bullet_count = original
            if attr == "health":
                self.health = original
            if attr == "attack_speed":
                self.attack_speed = original
            if attr == "bullet_speed":
                self.bullet_speed = original

# Classe dos Inimigos
class Enemy(Entity):
    def __init__(self, actor):
        super().__init__(actor)
        self.bullet_delay = 0
        self.move_delay = 0
        self.move_count = self.actor.move_count
        self.current_frame = ["enemy_run0", "enemy_run1", "enemy_run2", "enemy_run3"]
        self.frame = 0


    # Verifica se o jogador está na frente dos inimigos
    def in_front(self, player):
        if (
                (self.angle == 0 and player.x - 16 > self.x + 16 and player.y + 16 > self.y and player.y - 16 < self.y) or
                (self.angle == 90 and player.y + 16 < self.y - 16 and player.x + 16 > self.x and player.x - 16 < self.x) or
                (self.angle == 180 and player.x + 16 < self.x - 16 and player.y + 16 > self.y and player.y - 16 < self.y) or
                (self.angle == 270 and player.y - 16 > self.y + 16 and player.x + 16 > self.x and player.x - 16 < self.x)
        ):
            return True
        else:
            return False

    def move(self, walls, player):
        global tick
        if self.move_count > 0:
            self.move_count -= 1

            if self.move_count%8 == 0:
                choice = random.randint(0, 1)
                if choice == 0:
                    if player.y < self.y:
                        self.angle = 90
                    else:
                        self.angle = 270
                else:
                    if player.x < self.x:
                        self.angle = 180
                    else:
                        self.angle = 0

            if self.angle == 0:
                self.x += 2
            elif self.angle == 90:
                self.y -= 2
            elif self.angle == 180:
                self.x -= 2
            elif self.angle == 270:
                self.y += 2

            if self.actor.collidelist(walls) == 0:
                self.x += walls[0].x + 35
            elif self.actor.collidelist(walls) == 1:
                self.y = walls[1].y - 35
            elif self.actor.collidelist(walls) == 2:
                self.y = walls[2].y + 35
            elif self.actor.collidelist(walls) == 3:
                self.x = walls[3].x - 35
            if self.actor.collidelist(walls) != -1:
                self.move_count = 10
        else:
            self.move_count = 50
            self.move_delay = 10

        if tick % 8 == 0:
            self.frame += 1
        if self.frame > len(self.current_frame) - 1:
            self.frame = 0
        self.actor.image = self.current_frame[self.frame]

        self.actor.y = self.y
        self.actor.x = self.x
        self.actor.angle = self.angle

    # Cria as balas inimigas
    def shoot(enemy):
        pass

# Classe mãe das balas
class Bullets(Entity):
    def __init__(self, actor):
        super().__init__(actor)
        self.speed = 5

    # Movimento das balas
    def move(self):
        if self.angle == 0:
            self.x += self.speed
        elif self.angle == 90:
            self.y -= self.speed
        elif self.angle == 180:
            self.x -= self.speed
        elif self.angle == 270:
            self.y += self.speed

        self.actor.x = self.x
        self.actor.y = self.y
        self.actor.angle = self.angle

# Classe das balas inimigas
class EnemyBullets(Bullets):

    # Colisão das balas inimigas
    def collide(self, bullets, collision, player):
        if self.actor.collidelist(collision) != -1:
            bullets.remove(self)
        if self.actor.colliderect(player.actor):
            player.health -= 1
            player.lives.pop()
            bullets.remove(self)

# Classe das balas do jogador
class PlayerBullets(Bullets):

    def update_speed(self, player):
        if player.bullet_speed > self.speed:
            self.speed = player.bullet_speed

    # Colisão das balas do jogador
    def collide(self, bullets, collision, enemies):
        if self.actor.collidelist(collision) != -1:
            bullets.remove(self)
        for enemy in enemies:
            if self.actor.colliderect(enemy.actor):
                enemy_index = enemies.index(enemy)
                enemy.health -= 1
                if enemy.health <= 0:
                    enemies.remove(enemies[enemy_index])
                bullets.remove(self)

# Classe dos poderes
class Powers:
    def __init__(self):
        self.powerups = []
        self.count = 0

    # Define as posições corretas dos poderes
    def new_powerup(self, actor, current, ng):
        if self.count < 4:
            actor.x = 640 * (current + 1) / (ng // 2 + 1)
            actor.y = 180
        else:
            actor.x = 640 * (current + 1) / (ng // 2 + 1)
            actor.y = 360 *(current + 1)/ (ng // 2 + 1)
        self.powerups.append(actor)


    def powerup(self, power, player):
        if power.image == "attack_speed":
            player.attack_speed = round(player.attack_speed * .9, 2)
        elif power.image == "multi_shoot":
            player.bullet_count += 1
        elif power.image == "double_shoot":
            player.doubled_bullets += 1
        elif power.image == "extra_life":
            player.health += 1
        elif power.image == "movement_speed":
            player.speed = round(player.speed * 1.05, 2)
        elif power.image == "bullet_speed":
            player.bullet_speed = round(player.bullet_speed * 1.1, 2)