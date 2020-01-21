import pygame
from math import sqrt
from random import randint

pygame.init()

is_running = True
fps = 60
clock = pygame.time.Clock()
screen_size = (400, 600)
screen = pygame.display.set_mode(screen_size)


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
        self.dx = -(target.rect.x + target.rect.w // 2 - screen_size[0] // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - screen_size[1] // 2)


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)

        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.Color('green'))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * x, 50 * y
        self.draw()

        self.speed = 10
        self.target = None
        self.on_reload = True
        self.reload_time = 1000
        pygame.time.set_timer(pygame.USEREVENT + 1, self.reload_time, True)

    def draw(self):
        screen.blit(self.image, self.rect)

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
        else:
            turn_x *= sqrt(3) / 2
            turn_y *= sqrt(3) / 2

        self.rect.x += int(turn_x)
        self.rect.y += int(turn_y)

        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > screen_size[0] - self.rect.width:
            self.rect.x = screen_size[0] - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > screen_size[1] - self.rect.height:
            self.rect.y = screen_size[1] - self.rect.height

        while True:
            fucking_red_wells = pygame.sprite.spritecollide(self, walls, False)
            if fucking_red_wells:
                self.rect.x -= int(turn_x / 5)
                self.rect.y -= int(turn_y / 5)
            else:
                break

    def shot(self):
        if not self.on_reload:
            self.on_reload = True
            pygame.time.set_timer(pygame.USEREVENT + 1, self.reload_time, True)
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

        self.target = nearest_target[0]

    def update(self, *args, **kwargs):
        self.search_target()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(enemies, all_sprites)

        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.Color('blue'))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * x, 50 * y
        self.draw()

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self, *args, **kwargs):
        pass


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


class Bullet(pygame.sprite.Sprite):
    def __init__(self, from_smb, to_smb):
        super().__init__(bullets, all_sprites)

        self.image = pygame.Surface((10, 10))
        self.image.fill(pygame.Color(200, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = from_smb.rect.center

        self.speed = 10
        distance = sqrt((from_smb.rect.x - to_smb.rect.x) ** 2 +
                        (from_smb.rect.y - to_smb.rect.y) ** 2)
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
        elif pygame.sprite.spritecollide(self, enemies, False):
            print('Hit')
            bullets.remove(self)
            all_sprites.remove(self)


def generate_level(filename):
    level_map = open(filename, 'r').read().split('\n')
    hero = 'me'

    for y, row in enumerate(level_map):
        for x, char in enumerate(list(row)):
            if char == '/':
                Wall(x, y)
            elif char == '*':
                Enemy(x, y)
            elif char == '@':
                hero = Hero(x, y)
    return hero


camera = Camera()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
walls = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = generate_level('level.txt')

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            break
        if event.type == pygame.USEREVENT + 1:
            player.on_reload = False

    keys_pressed = pygame.key.get_pressed()
    player.direction_check(keys_pressed)

    screen.fill(pygame.Color(125, 255, 200))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.update()
    clock.tick(fps)

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

pygame.quit()
