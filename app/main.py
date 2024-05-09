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
        self.monster = pygame.sprite.Group()
        self.setup()
        self.font = pygame.font.Font('../graphics/subatomic.ttf', 25)
        self.music = pygame.mixer.Sound('../sound/music.mp3')
        self.music.set_volume(0.3)
        self.music.play(-1)

    def create_bullet(self, pos, direction):
        Bullet(pos, self.bullet_surf, direction, [self.all_sprites, self.bullet])

    def bullet_collision(self):

        for bullet in self.bullet.sprites():
            collision = pygame.sprite.spritecollide(bullet, self.monster, False, pygame.sprite.collide_mask)
            if collision:
                bullet.kill()
                for sprite in collision:
                    sprite.damage()

        for obstacle in self.obstacle.sprites():
            pygame.sprite.spritecollide(obstacle, self.bullet, True, pygame.sprite.collide_mask)

        if pygame.sprite.spritecollide(self.player, self.bullet, True, pygame.sprite.collide_mask):
            self.player.damage()

    def life_display(self):
        text = f'LIFE: {self.player.health}'
        life = self.font.render(text, True, 'red')
        life_rect = life.get_rect(center=(WINDOW_WIDTH - 80, 35))
        pygame.draw.rect(self.display_surface, 'green', life_rect.inflate(30, 30), width=5, border_radius=10)
        self.display_surface.blit(life, life_rect)

    def monster_left(self):
        text = f'Monsters: {len(self.monster)}'
        display = self.font.render(text, True, 'green')
        display_rect = display.get_rect(center=((WINDOW_WIDTH - (WINDOW_WIDTH-120)), 35))
        pygame.draw.rect(self.display_surface, 'red', display_rect.inflate(30, 30), width=5, border_radius=10)
        self.display_surface.blit(display, display_rect)

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
                    groups=[self.all_sprites, self.monster]
                )

            if obj.name == 'Cactus':
                Cactus(
                    pos=(obj.x, obj.y),
                    path=PATHS['cactus'],
                    collision_sprites=self.obstacle,
                    player=self.player,
                    create_bullet= self.create_bullet,
                    groups=[self.all_sprites, self.monster]
                )

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick(120) / 1000

            if self.player.health >= 0 and len(self.monster):
                self.all_sprites.update(dt)

                self.bullet_collision()

                self.display_surface.fill('black')

                self.all_sprites.customize_draw(self.player)

                self.life_display()
                self.monster_left()

            if self.player.health < 0:
                text = 'You died Press P to play again or Q to quit'
                display = self.font.render(text, True, 'red')
                display_rect = display.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
                pygame.draw.rect(self.display_surface, 'green', display_rect.inflate(30, 30), width=5, border_radius=10)
                self.display_surface.blit(display, display_rect)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_p]:
                    self.all_sprites.empty()
                    self.obstacle.empty()
                    self.bullet.empty()
                    self.monster.empty()
                    self.setup()

                if keys[pygame.K_q]:
                    pygame.quit()
                    sys.exit()

            if not len(self.monster):
                self.player.kill()
                text = 'You Won Press P to play again or Q to quit'
                display = self.font.render(text, True, 'green')
                display_rect = display.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
                pygame.draw.rect(self.display_surface, 'red', display_rect.inflate(30, 30), width=5, border_radius=10)
                self.display_surface.blit(display, display_rect)
                keys = pygame.key.get_pressed()

                if keys[pygame.K_p]:
                    self.all_sprites.empty()
                    self.obstacle.empty()
                    self.bullet.empty()
                    self.monster.empty()
                    self.setup()

                if keys[pygame.K_q]:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


if __name__ == '__main__':
    game = Begin()
    game.run()
