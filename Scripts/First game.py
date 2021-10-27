import pygame
import time
import os
import random
import numpy as np

# initialise window
WIN_WIDTH = 800
WIN_HEIGHT = 800
FPS = 60
pygame.init()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("First game")
clock = pygame.time.Clock()

# sprite image paths and fonts
current_dir = os.getcwd()
TURRET_IMG = pygame.image.load(
    os.path.join(current_dir, "FirstGame/Assets", "Turret.png")
).convert()
BULLET_IMG = pygame.image.load(
    os.path.join(current_dir, "FirstGame/Assets", "Bullet.png")
).convert()
TARGET_IMG = pygame.image.load(
    os.path.join(current_dir, "FirstGame/Assets", "Target.png")
).convert()
font = pygame.font.Font("freesansbold.ttf", 32)

# functions
def screen_counter(number, x, y):
    show_count = font.render(str(number), True, (255, 255, 255))
    screen.blit(show_count, (x, y))


def screen_timer(time):
    seconds = int(time / 60)
    countdown = 60 - seconds
    return countdown


def mouse_vector():
    x, y = pygame.mouse.get_pos()  # get mouse position
    mpos = [
        x - (WIN_WIDTH / 2),
        y - (WIN_HEIGHT / 2),
    ]  # mouse position vector (origin at center)
    ipos = [WIN_WIDTH / 2, 0]  # initial direction of bullet sprite as a vector
    unit_vector_1 = mpos / np.linalg.norm(
        mpos
    )  # block of code to find angle between mpos and ipos vectors
    unit_vector_2 = ipos / np.linalg.norm(ipos)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    theta = np.arccos(dot_product)
    degrees = np.degrees(theta)  # convert angle to degrees
    if y > WIN_HEIGHT / 2:
        degrees = 360 - degrees  # use outer angle when vector angles become >180
    return degrees


# Classes
class Turret(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale2x(TURRET_IMG)  # scale image
        self.original = self.image
        self.image.set_colorkey((0, 0, 0))  # removes black background from .convert()
        self.rect = self.image.get_rect()  # fetches image rectangle
        self.rect.center = (WIN_WIDTH / 2, WIN_HEIGHT / 2)  # centre image on screen
        self.degrees = 0  # initilize direction

    def update(self):
        center = self.rect.center  # set centre of turret rect
        self.degrees = mouse_vector()
        self.image = pygame.transform.rotate(
            self.original, self.degrees
        )  # transform image using original
        self.rect = self.image.get_rect(center=center)  # center new rect


class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale2x(BULLET_IMG)
        self.original = self.image
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIN_WIDTH / 2, WIN_HEIGHT / 2)
        self.degrees = 0
        self.velocity = 1

    def update(self):
        center = self.rect.center
        x, y = pygame.mouse.get_pos()
        self.degrees = mouse_vector()
        self.image = pygame.transform.rotate(
            self.original, self.degrees
        )  # transform image using original
        self.rect = self.image.get_rect(center=center)  # center new rect
        self.rect.x += (
            x - (WIN_WIDTH / 2)
        ) / 50  # set bullet velocity relative to mouse position
        self.rect.y += (
            y - (WIN_HEIGHT / 2)
        ) / 50  # may want to change bullet mechanics in the future


class Target(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = TARGET_IMG
        self.original = self.image
        self.image.set_colorkey((0, 0, 0))  # removes black background from .convert()
        self.rect = self.image.get_rect()  # fetches image rectangle
        self.rect.center = (
            random.randrange(10, (WIN_WIDTH - 50), 5),
            random.randrange(10, (WIN_HEIGHT - 50), 5),
        )  # randomly places target


# initilize objects/variables
turret = Turret()
bullet = Bullet()
target = Target()
bullet_count = 0
bullet_limit = 1
score_count = 0
time_count = 0

# sprite groups
game_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
target_sprites = pygame.sprite.Group()
game_sprites.add(turret)
game_sprites.add(target)
target_sprites.add(target)

# Game loop
running = True
while running:

    clock.tick(FPS)
    time_count += 1
    screen.fill((0, 0, 0))

    # process input
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT or time_count > 3600:
            running = False

        # shooting the turret, placed within pygame.event.get() to check event list during the same game loop.
        elif event.type == pygame.MOUSEBUTTONDOWN and bullet_count < (
            bullet_limit or 50
        ):
            bullet = Bullet()
            game_sprites.add(bullet)
            bullet_sprites.add(bullet)
            bullet_count += 1

    # hit reg for targets and ammo limit increment
    for bullet in bullet_sprites:
        bullet_hit_list = pygame.sprite.spritecollide(bullet, target_sprites, True)
        for target in bullet_hit_list:
            bullet_sprites.remove(bullet)
            game_sprites.remove(bullet)
            bullet_count -= 1
            score_count += 1
            target = Target()
            game_sprites.add(target)
            target_sprites.add(target)
            if score_count % 2 == 0:
                bullet_limit += 1

        # delete bullet if out of screen
        if (
            bullet.rect.x < 0
            or bullet.rect.x > (WIN_WIDTH - 10)
            or bullet.rect.y < 0
            or bullet.rect.y > (WIN_HEIGHT - 10)
        ):
            bullet_sprites.remove(bullet)
            game_sprites.remove(bullet)
            bullet_count -= 1

        # add new target when previous is removed
        if bullet_hit_list.__len__() >= 1:
            target_sprites.add(target)
            game_sprites.add(target)

    # Update sprites and draw to screen
    game_sprites.update()
    screen_counter(score_count, 10, 10)  # draw score in top left
    screen_counter(
        screen_timer(time_count), (WIN_WIDTH / 2), 10
    )  # draw timer in top middle
    game_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
