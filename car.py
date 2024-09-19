#!/usr/bin/env python3

import pygame
import time
import math
from utils import scale_image, blit_rotate_center

# Function to load an image with error handling
def load_image(image_path, scale):
    try:
        image = pygame.image.load(image_path)
        return scale_image(image, scale)
    except pygame.error as e:
        print(f"Error loading image '{image_path}': {e}")
        return None

# Function to initialize pygame and set up the game window
def initialize_game():
    pygame.init()
    pygame.display.set_caption("Racing Game")

# Function to handle events during the game loop
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True

# Function to draw images and player car on the game window
def draw(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    pygame.display.update()

# Function to handle player car movement based on keyboard input
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

# Main function to run the game
def main():
    # Load images with error handling
    GRASS = load_image("imgs/grass.jpg", 2.2)
    TRACK = load_image("imgs/track.png", 0.8)
    TRACK_BORDER = load_image("imgs/track-border.png", 0.8)
    FINISH = load_image("imgs/finish.png", 0.7)
    
    RED_CAR = load_image("imgs/red-car.png", 0.45)

    # Check if any image failed to load
    if None in (GRASS, TRACK, TRACK_BORDER, FINISH, RED_CAR):
        return

    WIDTH, HEIGHT =  TRACK.get_width(), TRACK.get_height()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))

    FPS = 60
    run = True
    clock = pygame.time.Clock()

    # Additional loaded images and constants
    TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
    FINISH_MASK = pygame.mask.from_surface(FINISH)
    FINISH_POSITION = (120, 220)

    images = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
    player_car = PlayerCar(10, 6, RED_CAR)

    while run:
        clock.tick(FPS)
        draw(WIN, images, player_car)
        pygame.display.update()
        
        run = handle_events()  # Handle events and check for quit event
        if not run:
            break
        
        move_player(player_car)

        if player_car.collide(TRACK_BORDER_MASK) != None:
            player_car.bounce()

        finish_point_of_intersection_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)

        if finish_point_of_intersection_collide != None:
            if finish_point_of_intersection_collide[1] == 0:
                player_car.bounce()
            else:
                player_car.reset()

    pygame.quit()

# Class for the player's car
class PlayerCar:
    def __init__(self, max_vel, rotation_vel, img):
        self.img = img
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = 160, 180
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

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration/2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

    def reset(self):
        self.x, self.y = 0, 0
        self.angle = 0
        self.vel = 0

if __name__ == "__main__":
    initialize_game()
    main()
