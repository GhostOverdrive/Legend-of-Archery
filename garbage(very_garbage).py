import pygame
from math import sqrt

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
        self.horizont_danger = False
        self.vertical_danger = False
        self.draw()

        self.speed = 10

    def draw(self):
        screen.blit(self.image, self.rect)

    def direction_check(self, keys_pressed):
        turn_x = 0
        turn_y = 0
        if keys_pressed[pygame.K_LEFT] and not self.horizont_danger:
            turn_x -= self.speed
            print(1, self.horizont_danger, self.vertical_danger)
        if keys_pressed[pygame.K_RIGHT] and not self.horizont_danger:
            turn_x += self.speed
            print(2, self.horizont_danger, self.vertical_danger)
        if keys_pressed[pygame.K_UP] and not self.vertical_danger:
            turn_y -= self.speed
            print(3, self.horizont_danger, self.vertical_danger)
        if keys_pressed[pygame.K_DOWN] and not self.vertical_danger:
            turn_y += self.speed
            print(4, self.horizont_danger, self.vertical_danger)

        if turn_x != 0 and turn_y != 0:
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
            self.rect.x += int(turn_x / 5)
            if pygame.sprite.spritecollide(self, walls, False):
                self.horizont_danger = True
                self.vertical_danger = False
            self.rect.x -= int(turn_x / 5)
            self.rect.y += int(turn_y / 5)
            if pygame.sprite.spritecollide(self, walls, False):
                self.vertical_danger = True
                self.horizont_danger = False
            self.rect.y -= int(turn_y / 5)
            if not pygame.sprite.spritecollide(self, walls, False):
                self.horizont_danger = False
                self.vertical_danger = False
                break


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


def generate_level(filename):
    map = open(filename, 'r').read().split('\n')
    player = 'me'

    for y, row in enumerate(map):
        for x, char in enumerate(list(row)):
            if char == '/':
                Wall(x, y)
            elif char == '@':
                player = Hero(x, y)
    return player


walls = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
camera = Camera()
player = generate_level('level.txt')

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            break
    keys_pressed = pygame.key.get_pressed()
    player.direction_check(keys_pressed)

    screen.fill(pygame.Color(125, 255, 200))
    all_sprites.draw(screen)
    pygame.display.update()
    clock.tick(fps)

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

pygame.quit()
