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

        # dx and dy together describe the direction in which the ball is moving. For example, if dx and dy are 1 and 0,
        # the ball is moving to the right, with no movement up or down. If both values are negative, the ball is moving
        # left and up, with the angle depending on the relative values of the two variables. If you're familiar with
        # vectors, dx and dy represent a unit vector.
        self.dx, self.dy = dx, 0

        self.speed = 5

    def update(self):
        # Each frame, we move the ball in a series of small steps - the number of steps being based on its speed attribute
        for i in range(self.speed):
            original_x = self.x

            # Move the ball
            self.x += self.dx
            self.y += self.dy

            # Check to see if ball needs to bounce off a bat

            # To determine whether the ball might collide with a bat, we first measure the horizontal distance from the
            # ball to the centre of the screen, and check to see if its edge has gone beyond the edge of the bat.
            # The centre of each bat is 40 pixels from the edge of the screen, or to put it another way, 360 pixels
            # from the centre of the screen. The bat is 18 pixels wide and the ball is 14 pixels wide. Given that these
            # sprites are anchored from their centres, when determining if they overlap or touch, we need to look at
            # their half-widths - 9 and 7. Therefore, if the centre of the ball is 344 pixels from the centre of the
            # screen, it can bounce off a bat (assuming the bat is in the right position on the Y axis - checked
            # shortly afterwards).
            # We also check the previous X position to ensure that this is the first frame in which the ball crossed the threshold.
            if abs(self.x - HALF_WIDTH) >= 344 and abs(original_x - HALF_WIDTH) < 344:

                # Now that we know the edge of the ball has crossed the threshold on the x-axis, we need to check to
                # see if the bat on the relevant side of the arena is at a suitable position on the y-axis for the
                # ball collide with it.
                if self.x < HALF_WIDTH:
                    new_dir_x = 1
                    bat = game.bats[0]
                else:
                    new_dir_x = -1
                    bat = game.bats[1]

                difference_y = self.y - bat.y

                if difference_y > -64 and difference_y < 64:
                    self.dx = -self.dx
                    # Deflect slightly up or down depending on where the ball hit bat
                    self.dy += difference_y / 128  # 128 -> 64 * 2

                    # Limit the y component of the vector so we don't get into a situation where the ball is bouncing up and down too rapidly
                    self.dy = min(max(self.dy, -1), 1)
                    # Ensure our direction vector is a unit vector
                    self.dx, self.dy = normalised(self.dx, self.dy)

                    # Create an impact effect
                    game.impacts.append(Impact((self.x - new_dir_x * 10, self.y)))

                    # Increase speed with each hit
                    self.speed += 1

                    # Add an offset to the AI player's target y position, so it won't aim to hit the ball exactly
                    # in the centre of the bat
                    game.ai_offset = random.randint(-10, 10)

                    # Bat glows for 10 frames
                    bat.timer = 10

                    # Play hit sounds, with more intense sound effects as the ball gets faster
                    game.play_sound("hit", 5)  # play every time in addition to:
                    if self.speed <= 10:
                        game.play_sound("hit_slow", 1)
                    elif self.speed <= 12:
                        game.play_sound("hit_medium", 1)
                    elif self.speed <= 16:
                        game.play_sound("hit_fast", 1)
                    else:
                        game.play_sound("hit_veryfast", 1)

            # The top and bottom of the arena are 220 pixels from the centre
            if abs(self.y - HALF_HEIGHT) > 220:
                # invert vertical direction and apply new dy to y so that the ball is no longer overlapping with the edge of the arena
                self.dy = -self.dy
                self.y += self.dy

                # Create impact effect
                game.impacts.append(Impact(self.pos))
                # Sound effect
                game.play_sound("bounce", 5)
                game.play_sound("bounce_synth", 1)

    def out(self) -> bool:
        """
        Has ball gone off the left or right edge of the screen?
        """
        return self.x < 0 or self.x > WIDTH


class Bat(Actor):
    def __init__(self, player, move_func=None):
        x = 40 if player == 0 else 760
        y = HALF_HEIGHT
        super().__init__("blank", (x, y))

        self.player = player
        self.score = 0

        # move_func is a function we may or may not have passed by the code which created this object.
        if move_func != None:
            self.move_func = move_func
        else:
            self.move_func = self.ai

        # Each bat has a timer which starts at zero and counts down by one every frame. When a player concedes a point,
        # their timer is set to 20, which causes the bat to display a different animation frame. It is also used to
        # decide when to create a new ball in the centre of the screen - see comments in Game.update for more on this.
        # Finally, it is used in Game.draw to determine when to display a visual effect over the top of the background
        self.timer = 0

    def update(self):
        self.timer -= 1

        # Our movement function tells us how much to move on the Y axis
        y_movement = self.move_func()
        # Apply y_movement to y position, ensuring bat does not go through the side walls
        self.y = min(400, max(80, self.y + y_movement))

        
        # Choose the appropriate sprite. There are 3 sprites per player - e.g. bat00 is the left-hand player's
        # standard bat sprite, bat01 is the sprite to use when the ball has just bounced off the bat, and bat02
        # is the sprite to use when the bat has just missed the ball and the ball has gone out of bounds.
        # bat10, 11 and 12 are the equivalents for the right-hand player

        frame = 0
        if self.timer > 0:
            if game.ball.out():
                frame = 2
            else:
                frame = 1
        
        self.image = "bat" + str(self.player) + str(frame)

    def ai(self)->int:
        """
            Returns a number indicating how the computer player move - e.g. 4 means it will move 4 pixels 
            down the screen
        """

        # To decide where we want to go, we first check to see how far we are from the ball.
        x_distance = abs(game.ball.x - self.x)

        # If the ball is far away, we move towards the centre of the screen (HALF_HEIGHT), on the basis that we don't
        # yet know whether the ball will be in the top or bottom half of the screen when it reaches our position on
        # the X axis. By waiting at a central position, we're as ready as it's possible to be for all eventualities.
        target_y_1 = HALF_HEIGHT

        # If the ball is close, we want to move towards its position on the Y axis. We also apply a small offset which
        # is randomly generated each time the ball bounces. This is to make the computer player slightly less robotic
        # - a human player wouldn't be able to hit the ball right in the centre of the bat each time.
        target_y_2 = game.ball.y + game.ai_offset

        # The final step is to work out the actual Y position we want to move towards. We use what's called a weighted
        # average - taking the average of the two target Y positions we've previously calculated, but shifting the
        # balance towards one or the other depending on how far away the ball is. If the ball is more than 400 pixels
        # (half the screen width) away on the X axis, our target will be half the screen height (target_y_1). If the
        # ball is at the same position as us on the X axis, our target will be target_y_2. If it's 200 pixels away,
        # we'll aim for halfway between target_y_1 and target_y_2. This reflects the idea that as the ball gets closer,
        # we have a better idea of where it's going to end up.
        weight1 = min(1, x_distance / HALF_WIDTH)
        weight2 = 1 - weight1

        target_y = (weight1 * target_y_1) + (weight2 * target_y_2)

        # Subtract target_y from our current Y position, then make sure we can't move any further than MAX_AI_SPEED
        # each frame
        return min(MAX_AI_SPEED, max(-MAX_AI_SPEED, target_y - self.y))


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

        # Remove any expired impact effects from the list. We go through the list backwards, starting from the last
        # element, and delete any elements those time attribute has reached 10. We go backwards through the list
        # instead of forwards to avoid a number of issues which occur in that scenario. 
        for i in range(len(self.impacts) - 1, -1, -1):
            if self.impacts[i].time >= 10:
                del self.impacts[i]

        # Has ball gone off the left or the right edge of the screen?
        if self.ball.out():
            # Work out which player gained a point, based on whether the ball
            # was on the left or right-hand side of the screen
            scoring_player = 1 if self.ball.x < WIDTH // 2 else 0
            losing_player = 1 - scoring_player

            # We use the timer of the player who has just conceded a point to decide when to create a new ball in the
            # centre of the level. This timer starts at zero at the beginning of the game and counts down by one every
            # frame. Therefore, on the frame where the ball first goes off the screen, the timer will be less than zero.
            # We set it to 20, which means that this player's bat will display a different animation frame for 20
            # frames, and a new ball will be created after 20 frames
            if self.bats[losing_player].timer < 0:
                self.bats[scoring_player].score += 1

                game.play_sound("score_goal", 1)
                self.bats[losing_player].timer = 20

            elif self.bats[losing_player].timer == 0:
                # After 20 frames, create new ball, heading in the direction of the player who just missed the ball
                direction = -1 if losing_player == 0 else 1
                self.ball = Ball(direction)

    def draw(self):
        # Draw background
        screen.blit("table", (0, 0))

        # Draw bats, ball and impact effects - in that order.
        for obj in self.bats + [self.ball] + self.impacts:
            obj.draw()

    def play_sound(self, name, count=1, menu_sound=False):
        # Some sounds have multiple varieties. If count > 1, we'll randomly choose one from those
        # We don't play any in-game sound effects if player 0 is an AI player - as this means we're on the menu
        # Updated Jan 2022 - some Pygame installations have issues playing ogg sound files. play_sound can skip sound
        # errors without stopping the game, but it previously couldn't be used for menu-only sounds
        if self.bats[0].move_func != self.bats[0].ai or menu_sound:
            # Pygame Zero allows you to write things like 'sounds.explosion.play()'
            # This automatically loads and plays a file named 'explosion.wav' (or .ogg) from the sounds folder (if
            # such a file exists)
            # But what if you have files named 'explosion0.ogg' to 'explosion5.ogg' and want to randomly choose
            # one of them to play? You can generate a string such as 'explosion3', but to use such a string
            # to access an attribute of Pygame Zero's sounds object, we must use Python's built-in function getattr
            try:
                getattr(sounds, name + str(random.randint(0, count - 1))).play()
            except Exception as e:
                pass


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


game = Game([p1_controls, None])

pgzrun.go()
