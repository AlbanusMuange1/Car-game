#!/usr/bin/env python3

import pygame
import time
import math
from utils import scale_image, blit_rotate_center


GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.2)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.8)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.8)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = scale_image(pygame.image.load("imgs/finish.png"), 0.7)
FINISH_POSITION = (120, 220)
FINISH_MASK = pygame.mask.from_surface(FINISH)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.5)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.5)

WIDTH, HEIGHT =  TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game")

FPS = 60
PATH = [(155, 86), (41, 129), (51, 412), (232, 614), (351, 600), (370, 466), (370, 466), (535, 473), (536, 612), (657, 619), (653, 330), (383, 327), (414, 224), (611, 221), (636, 72), (263, 76), (244, 328), (142, 311), (160, 185)]

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.2
    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)

        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        point_of_intersection = mask.overlap(car_mask, offset)
        return point_of_intersection
    def reset(self):
        self.x, self.y = 0
        self.angle = 0
        self.vel = 0

class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (160, 180)
    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 4)


    # def draw(self, win):
    #     super().draw(win)
    #     self.draw_points(win)


    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)


        if target_y > self.y:
            desired_radian_angle += math.pi


        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360
        
        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (130, 180)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration/2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

def draw(win, images, player_car, computer_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

run = True
clock = pygame.time.Clock()

images = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(8, 8)
computer_car = ComputerCar(4, 6, PATH)
while run:
    clock.tick(FPS)
    draw(WIN, images, player_car, computer_car)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            computer_car.path.append(pos)

    move_player(player_car)
    computer_car.move()

    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    finish_point_of_intersection_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)

    if finish_point_of_intersection_collide != None:
        if finish_point_of_intersection_collide[1] == 0:
            player_car.bounce()
        else:
            player_car.reset()
# print(computer_car.path)
pygame.quit()