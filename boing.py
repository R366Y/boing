import pgzero, pgzrun, pygame
import math, sys, random
from enum import Enum

if sys.version_info < (3, 5):
    print("This game requires at least version 3.5 of Python")
    sys.exit()

pgzero_version = [int(s) if s.isnumeric() else s for s in pgzero.__version__.split(".")]

if pgzero_version < [1, 2]:
    print(
        "This game requires at least version 1.2 of Pygame Zero. You are using verion {pgzero.__version__}"
    )

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
        super().__init__("ball", (0, 0))

        self.x, self.y = HALF_WIDTH, HALF_HEIGHT

        self.dx, self.dy = dx, 0

        self.speed = 0

    def update(self):
        pass


class Bat(Actor):
    def __init__(self, player, move_func=None):
        x = 40 if player==0 else 760
        y = HALF_HEIGHT
        super().__init__("blank", (x,y))

        self.player = player
        self.score = 0

        # move_func is a function we may or may not have passed by the code which created this object.
        if move_func != None:
            self.move_func = move_func
        else:
            # TODO: ai 
            pass
        
        self.timer = 0

    def update(self):
        self.timer -= 1

        # Our movement function tells us how much to move on the Y axis
        y_movement = self.move_func()
        # Apply y_movement to y position, ensuring bat does not go through the side walls
        self.y = min(400, max(80, self.y + y_movement))

        frame = 0
        self.image = "bat" +str(self.player) + str(frame)

class Game:
    def __init__(self, controls=(None, None)) -> None:
        self.bats = [Bat(0, controls[0]), Bat(1, controls[1])]
        self.ball = Ball(-1)
        self.impacts = []
        self.ai_offset = 0

    def update(self):
        # Update all active objects
        for obj in self.bats + [self.ball] + self.impacts:
            obj.update()

    def draw(self):
        # Draw background
        screen.blit("table", (0, 0))

        # Draw bats, ball and impact effects - in that order.
        for obj in self.bats + [self.ball] + self.impacts:
            obj.draw()


def p1_controls():
    """
    Function that maps keyboard to player 1 movements
    """
    move = 0
    if keyboard.z or keyboard.down:
        move = PLAYER_SPEED
    elif keyboard.a or keyboard.up:
        move = -PLAYER_SPEED
    return move


def p2_controls():
    """
    Function that maps keyboard to player 2 movements
    """
    move = 0
    if keyboard.m:
        move = PLAYER_SPEED
    elif keyboard.k:
        move = -PLAYER_SPEED
    return move


def update():
    game.update()


def draw():
    game.draw()


game = Game([p1_controls, p2_controls])

pgzrun.go()
