import pygame
import numpy as np
from enum import Enum
from collections import namedtuple
import random

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

# Create an iteratable (loop-able) set of values for directions
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# namedtuple() is a function that generates a subclass of tuple
# with named fields. create an instance of 'Point" with
# P = Point(11, y = 22) and access x and y with print(p.x, p.y)
Point = namedtuple('Point', 'x, y')

# color values in rgb
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)

# constant values
BLOCK_SIZE = 60
SPEED = 40

class obstacleCourse:
    
    def __init__(self, w=720, h=720):
        self.w = w
        self.h = h
        # initialize display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Obstacle Course')
        self.clock = pygame.time.Clock()
        self.obstacles = []
        self.placeObstacles()
        self.reset()

    def reset(self):
        # initial game state
        self.direction = Direction.RIGHT

        self.playerPosition = Point(self.w/2, self.h/2)
        self.player = [self.playerPosition]
        self.score = 0
        self.target = None
        self.placeTarget()
        self.frameIteration = 0

    def placeTarget(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.target = Point(x, y)
        if self.target == self.playerPosition:
            self.placeTarget() #if playerPosition and food are the same, try again.
        if self.target in self.obstacles:
            self.placeTarget()

    def placeObstacles(self):
        for i in range(10):
            x = random.randint(0,(self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
            y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
            self.obstacle = Point(x, y)
            if self.obstacle in self.obstacles:
                self.placeObstacles()
            else:
                self.obstacles.append(self.obstacle)

    def playStep(self, action):
        self.frameIteration += 1
        # Collect User Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # Move
        self.move(action) # update the player position
        # Check if game over
        reward = 0
        game_over = False
        # Check for collisions
        if self.collision() or self.frameIteration > 100:
            game_over = True
            reward = -10
            return reward, game_over, self.score
        # Place new target or move
        if self.playerPosition == self.target:
            self.score += 1
            reward = 10
            self.placeTarget()

        # Update ui and clock
        self.updateUI()
        self.clock.tick(SPEED)
        # Return game over and score
        return reward, game_over, self.score
    
    def collision(self, pt=None):
        if pt is None:
            pt = self.playerPosition
        # hits edge
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
                return True
        # hits obstacle
        if pt in self.obstacles:
            return True
        
        return False

    def drawGrid(self):
        for x in range(0, self.w, BLOCK_SIZE):
            for y in range(0, self.h, BLOCK_SIZE):
                rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.display, BLACK, rect, 1)

    def updateUI(self):
        self.display.fill(WHITE)
        self.drawGrid()

        for obstacle in self.obstacles:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(obstacle.x, obstacle.y, BLOCK_SIZE, BLOCK_SIZE))
        
        pygame.draw.rect(self.display, BLUE, pygame.Rect(self.playerPosition.x, self.playerPosition.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(self.display, RED, pygame.Rect(self.target.x, self.target.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, BLACK)
        self.display.blit(text, [0,0])
        pygame.display.flip()

    def move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
                new_dir = clock_wise[idx] # same direction
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn
        
        self.direction = new_dir

        x = self.playerPosition.x
        y = self.playerPosition.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.playerPosition = Point(x, y)