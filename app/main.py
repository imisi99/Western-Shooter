import pygame
import sys
from settings import *
from player import Player
from pytmx.util_pygame import load_pygame
from sprite import Sprite, Bullet
from pygame.math import Vector2 as Vector
from enemies import Coffin, Cactus


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = Vector()
        self.display_surface = pygame.display.get_surface()
        self.bg = pygame.image.load('../graphics/other/bg.png').convert_alpha()

    def customize_draw(self, player):
        self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
        self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2

        self.display_surface.blit(self.bg, -self.offset)
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.image.get_rect(center=sprite.rect.center)
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)


class Begin:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Western Shooter')
        self.clock = pygame.time.Clock()
        self.bullet_surf = pygame.image.load('../graphics/other/particle.png').convert_alpha()

        self.all_sprites = AllSprites()

        self.obstacle = pygame.sprite.Group()
        self.bullet = pygame.sprite.Group()
        self.setup()

    def create_bullet(self, pos, direction):
        Bullet(pos, self.bullet_surf, direction, [self.all_sprites, self.bullet])

    def setup(self):
        tmx_map = load_pygame('../data/map.tmx')
        for x, y, surf in tmx_map.get_layer_by_name('Fence').tiles():
            Sprite((x * 64, y * 64), surf, [self.all_sprites, self.obstacle])

        for obj in tmx_map.get_layer_by_name('Objects'):
            Sprite((obj.x, obj.y), obj.image, [self.all_sprites, self.obstacle])

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    path=PATHS['player'],
                    collision_sprites=self.obstacle,
                    create_bullet=self.create_bullet,
                    groups=self.all_sprites)

            if obj.name == 'Coffin':
                Coffin(
                    pos=(obj.x, obj.y),
                    path=PATHS['coffin'],
                    collision_sprites=self.obstacle,
                    player=self.player,
                    groups=self.all_sprites
                )

            if obj.name == 'Cactus':
                Cactus(
                    pos=(obj.x, obj.y),
                    path=PATHS['cactus'],
                    collision_sprites=self.obstacle,
                    player=self.player,
                    groups=self.all_sprites
                )

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick(120) / 1000

            self.all_sprites.update(dt)

            self.display_surface.fill('black')

            self.all_sprites.customize_draw(self.player)

            pygame.display.update()


if __name__ == '__main__':
    game = Begin()
    game.run()
