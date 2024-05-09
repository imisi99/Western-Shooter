import pygame
from pygame.math import Vector2 as Vector
from entity import Entity
from settings import *


class Player(Entity):
    def __init__(self, pos, path, collision_sprites, create_bullet, groups):
        super().__init__(pos, path, collision_sprites, groups)
        self.bullet_direction = 0
        self.bullet_pos = 0
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.health = 5

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = self.status.split('_')[0] + '_idle'

        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.attacking:
            if keys[pygame.K_UP]:
                self.status = 'up'
                self.direction.y = -1
            elif keys[pygame.K_DOWN]:
                self.status = 'down'
                self.direction.y = 1
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.status = 'left'
                self.direction.x = -1
            elif keys[pygame.K_RIGHT]:
                self.status = 'right'
                self.direction.x = 1
            else:
                self.direction.x = 0

            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.direction = Vector()
                self.frame_index = 0
                self.bullet_shot = False

                match self.status.split('_')[0]:
                    case 'left':
                        self.bullet_direction = Vector(-1, 0)
                    case 'right':
                        self.bullet_direction = Vector(1, 0)
                    case 'up':
                        self.bullet_direction = Vector(0, -1)
                    case 'down':
                        self.bullet_direction = Vector(0, 1)

    def animate(self, dt):
        current_animation = self.animation[self.status]

        self.frame_index += 8 * dt

        if int(self.frame_index) == 0 and self.attacking and not self.bullet_shot:
            self.bullet_pos = self.rect.center + self.bullet_direction * 80
            self.create_bullet(self.bullet_pos, self.bullet_direction)
            self.bullet_shot = True
            self.shoot_sound.play()

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.get_status()
        self.timer()
        self.blink()
