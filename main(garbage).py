import pygame
from math import sqrt

pygame.init()

is_running = True
fps = 60
clock = pygame.time.Clock()
screen_size = (400, 600)
screen = pygame.display.set_mode(screen_size)


class Hero(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.Color('green'))
        self.rect = self.image.get_rect()
        self.rect.center = screen.get_rect().midbottom
        self.rect.y -= self.rect.height // 2
        self.draw()

        self.speed = 10

    def draw(self):
        screen.blit(self.image, self.rect)

    def direction_check(self, keys_pressed):
        turn_x = 0
        turn_y = 0
        if keys_pressed[pygame.K_LEFT]:
            turn_x -= me.speed
        if keys_pressed[pygame.K_RIGHT]:
            turn_x += me.speed
        if keys_pressed[pygame.K_UP]:
            turn_y -= me.speed
        if keys_pressed[pygame.K_DOWN]:
            turn_y += me.speed

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


me = Hero()

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            break
    keys_pressed = pygame.key.get_pressed()
    me.direction_check(keys_pressed)

    screen.fill(pygame.Color(125, 255, 200))
    me.draw()
    pygame.display.update()
    clock.tick(fps)

pygame.quit()
