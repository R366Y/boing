import pgzero, pgzrun, pygame
import math, sys, random
from enum import Enum

if sys.version_info < (3,5):
    print("This game requires at least version 3.5 of Python")
    sys.exit()

pgzero_version = [int(s) if s.isnumeric() else s for s in pgzero.__version__.split('.')]

if pgzero_version < [1,2]: 
    print("This game requires at least version 1.2 of Pygame Zero. You are using verion {pgzero.__version__}")

WIDTH = 800
HEIGHT = 480
TITLE = "Boing!"

HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
PLAYER_SPEED = 6
MAX_AI_SPEED = 6


def normalised(x, y):
    """
        normalize the coordinates, returns unit vector
    """
    length = math.hypot(x, y)
    return (x / length, y / length)

def sign(x):
    return -1 if x < 0 else 1


class Impact(Actor):
    """
        Class for animation that is displayed briefly whenever the ball bounces
    """
    def __init__(self, pos):
        super().__init__("blank", pos)
        self.time = 0

    def update(self):
        # there are 5 impact sprites numbered 0 to 4. We update a new sprite every 2 frames.
        self.image = "impact" + str(self.time // 2)

        # The Game class mantains a list of impact instances. If the time for an object 
        # has gone beyond 10, the object is removed from the list.
        self.time += 1

class Ball(Actor):
    def __init__(self, dx):
        super().__init__("ball", (0,0))

        self.x, self.y = HALF_WIDTH, HALF_HEIGHT

        self.dx, self.dy = dx, 0

        self.speed = 0

class Game:
    def __init__(self, controls=(None, None)) -> None:
        self.bats = []
        self.ball = Ball(-1)
        self.impacts = []
        self.ai_offset = 0

    def update(self):
        pass

    def draw(self):
        #Draw background
        screen.blit("table", (0,0))

        # Draw bats, ball and impact effects - in that order. 
        for obj in self.bats + [self.ball] + self.impacts:
            obj.draw()

def update():
    pass

def draw():
    game.draw()

game = Game()

pgzrun.go()