import pygame
from math import sqrt
from random import randint


class Timers:
    def __init__(self):
        self.timers = list()

    def new(self, delay_time, function, reload=False):
        self.timers.append([pygame.time.get_ticks() + delay_time,
                            function, reload, delay_time])
        return self.timers[-1]

    def update(self):
        for timer in self.timers:
            if pygame.time.get_ticks() >= timer[0]:
                timer[1]()
                if timer[2]:
                    timer[0] += timer[3]
                else:
                    self.timers.remove(timer)


pygame.init()

you_win = False
is_running = True
fps = 60
level = 5
change = False
clock = pygame.time.Clock()
player = None
screen_size = (400, 600)
screen = pygame.display.set_mode(screen_size)
background_color = pygame.Color(125, 255, 200)
timers = Timers()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - screen_size[
            0] // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - screen_size[
            1] // 2)


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)

        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.Color('green'))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * x, 50 * y

        self.speed = 10
        self.target = None
        self.on_reload = True
        self.reload_time = 1000
        self.reload_timer = timers.new(self.reload_time, self.reload, True)

        self.hp = 5

    def reload(self):
        self.on_reload = False

    def direction_check(self, keys_pressed):
        turn_x = 0
        turn_y = 0

        if keys_pressed[pygame.K_LEFT]:
            turn_x -= self.speed
        if keys_pressed[pygame.K_RIGHT]:
            turn_x += self.speed
        if keys_pressed[pygame.K_UP]:
            turn_y -= self.speed
        if keys_pressed[pygame.K_DOWN]:
            turn_y += self.speed

        if turn_x == 0 and turn_y == 0:
            self.shot()
            return
        elif turn_x != 0 and turn_y != 0:
            turn_x *= sqrt(3) / 2
            turn_y *= sqrt(3) / 2

        self.rect.x += int(turn_x)
        self.rect.y += int(turn_y)

        while True:
            fucking_red_wells = pygame.sprite.spritecollide(self, walls,
                                                            False)
            if fucking_red_wells:
                self.rect.x -= int(turn_x / 5)
                self.rect.y -= int(turn_y / 5)
            else:
                break

        if pygame.sprite.spritecollide(self, check_points, False):
            global level
            global change
            level += 1
            change = True

    def shot(self):
        if not self.on_reload and self.target is not None:
            self.on_reload = True
            Bullet(self, self.target)

    def search_target(self):
        nearest_target = list()

        for n, enemy in enumerate(enemies):
            distance = sqrt((self.rect.x - enemy.rect.x) ** 2 +
                            (self.rect.y - enemy.rect.y) ** 2)

            if nearest_target == list():
                nearest_target = [enemy, distance]
            elif nearest_target[1] > distance:
                nearest_target = [enemy, distance]

            enemy.distance_to_hero = distance

        if len(nearest_target) == 0:
            self.target = None
        else:
            self.target = nearest_target[0]

    def update(self, *args, **kwargs):
        global is_running

        self.search_target()

        if self.hp <= 0:
            print('Game over')
            is_running = False


class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(check_points, all_sprites)

        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.Color(205, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * x, 50 * y
        self.draw()

    def draw(self):
        screen.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(enemies, all_sprites)

        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.Color('blue'))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * x, 50 * y

        self.target = None
        self.reload_time = 2000
        self.on_reload = True
        self.distance_to_hero = 10000
        self.reload_timer = timers.new(self.reload_time, self.reload, True)

        self.speed = 5
        self.draw()

    def reload(self):
        self.on_reload = False

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self, *args, **kwargs):
        distance = sqrt((player.rect.x - self.rect.x) ** 2 +
                        (player.rect.y - self.rect.y) ** 2) + 1

        self.shot()
        if distance < 100:
            return

        turn_x = int((player.rect.x - self.rect.x) * self.speed / distance)
        turn_y = int((player.rect.y - self.rect.y) * self.speed / distance)
        # print(turn_x, turn_y)

        self.rect.x += int(turn_x)
        self.rect.y += int(turn_y)

        if self.rect.x == player.rect.x:
            self.rect.y += self.speed // 2
        elif self.rect.y == player.rect.y:
            self.rect.x += self.speed // 2

        a = True
        while True:
            fucking_red_wells = pygame.sprite.spritecollide(self, walls,
                                                            False)
            if fucking_red_wells:
                a = not a
                if a:
                    self.rect.x -= turn_x
                else:
                    self.rect.y -= turn_y
            else:
                break

    def shot(self):
        if not self.on_reload:
            self.on_reload = True
            Bullet(self, player, True)


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(walls, all_sprites)

        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.Color('red'))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * x, 50 * y
        self.draw()

    def draw(self):
        screen.blit(self.image, self.rect)


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, enemies)

        self.image = pygame.Surface((100, 100))
        self.image.fill(pygame.Color(0, 0, 60))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * x, 50 * y

        self.target = None
        self.reload_time = 2000
        self.on_reload = True
        self.distance_to_hero = 10000
        self.reload_timer = timers.new(self.reload_time, self.reload, True)
        self.hp = 10

    def reload(self):
        self.on_reload = False

    def update(self, *args, **kwargs):
        distance = sqrt((player.rect.x - self.rect.x) ** 2 +
                        (player.rect.y - self.rect.y) ** 2) + 1

        if len(enemies) < 5 and not self.on_reload:
            Enemy(self.rect.x // 50, self.rect.y // 50)

        self.shot()

    def shot(self):
        if not self.on_reload:
            self.on_reload = True

            for i in range(16 - self.hp):
                a = Bullet(self, player, True)

                while True:
                    a.step_x = randint(-6, 6)
                    a.step_y = randint(-6, 6)

                    if not (a.step_x == 0 and a.step_y == 0):
                        break


class Bullet(pygame.sprite.Sprite):
    def __init__(self, from_smb, to_smb, enemy_fire=False):
        super().__init__(bullets, all_sprites)

        self.image = pygame.Surface((10, 10))
        self.image.fill(pygame.Color(200, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = from_smb.rect.center
        self.enemy_fire = enemy_fire

        self.speed = 10
        distance = sqrt((from_smb.rect.x - to_smb.rect.x) ** 2 +
                        (from_smb.rect.y - to_smb.rect.y) ** 2) + 1
        self.step_x = -int((from_smb.rect.x - to_smb.rect.x) * self.speed
                           / distance)
        self.step_y = -int((from_smb.rect.y - to_smb.rect.y) * self.speed
                           / distance)

        self.draw()

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self, *args, **kwargs):
        self.rect = self.rect.move(self.step_x, self.step_y)

        if pygame.sprite.spritecollide(self, walls, False):
            bullets.remove(self)
            all_sprites.remove(self)
        elif type(boss) != str and pygame.sprite.collide_rect(self, boss) and \
                self.enemy_fire == False:
            global is_running, you_win

            print('Boss Hit')
            boss.hp -= 1
            if boss.hp <= 0:
                is_running = False
                you_win = True

            bullets.remove(self)
            all_sprites.remove(self)
        elif self.enemy_fire:
            if pygame.sprite.collide_rect(self, player):
                print('Enemy Hit')
                player.hp -= 1
                bullets.remove(self)
                all_sprites.remove(self)
        elif pygame.sprite.spritecollide(self, enemies, True):
            print('Hit')
            bullets.remove(self)
            all_sprites.remove(self)


def generate_level(filename):
    global boss

    level_map = open(filename, 'r').read().split('\n')
    hero = 'me'

    for y, row in enumerate(level_map):
        for x, char in enumerate(list(row)):
            if char == '/':
                Wall(x, y)
            elif char == '-':
                Checkpoint(x, y)
            elif char == '*':
                Enemy(x, y)
            elif char == '@':
                hero = Hero(x, y)
            elif char == '$':
                boss = Boss(x, y)

    for enemy in enemies:
        enemy.target = hero
    return hero


camera = Camera()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
walls = pygame.sprite.Group()
bullets = pygame.sprite.Group()
check_points = pygame.sprite.Group()
player = generate_level('intro.txt')
boss = 'lucky you'

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            break

    keys_pressed = pygame.key.get_pressed()
    player.direction_check(keys_pressed)

    screen.fill(background_color)
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.update()
    clock.tick(fps)

    timers.update()
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    if change:
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        walls = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        check_points = pygame.sprite.Group()
        timers = Timers()
        player = generate_level(str(level) + '.txt')
        change = False

font = pygame.font.SysFont('Impact', 80)

if not you_win:
    game_over_text = font.render('Game over', False,
                                 pygame.Color(255, 100, 100))
    end_screen = pygame.Surface(game_over_text.get_size())
    end_screen.blit(game_over_text, (0, 0))
    screen.blit(end_screen, (screen_size[0] // 2 - end_screen.get_width() // 2,
                             screen_size[
                                 1] // 2 - end_screen.get_height() // 2))
else:
    game_over_text = font.render('You win', False,
                                 pygame.Color(100, 255, 100))
    end_screen = pygame.Surface(game_over_text.get_size())
    end_screen.fill(pygame.Color(133, 224, 224))
    end_screen.blit(game_over_text, (0, 0))
    screen.blit(end_screen, (screen_size[0] // 2 - end_screen.get_width() // 2,
                             screen_size[
                                 1] // 2 - end_screen.get_height() // 2))
pygame.display.update()

pygame.time.delay(1000)

pygame.quit()
