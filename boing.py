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



pgzrun.go()