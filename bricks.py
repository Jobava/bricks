import pyglet
import tempfile
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Set global options

EMPTY_HEIGHT = 300
BRICK_WIDTH = 100
BRICK_HEIGHT = 20
NX = 6
NY = 7
MARGIN = 8
PADDLE_WIDTH = 130
PADDLE_HEIGHT = 17
BALL_RADIUS = 15

WINDOW_WIDTH = (BRICK_WIDTH + MARGIN) * NX + MARGIN
WINDOW_HEIGHT = EMPTY_HEIGHT + (BRICK_HEIGHT + MARGIN) * NY

CMAP = plt.cm.jet

# Prepare colormap
COLORS = [plt.cm.jet(x) for x in np.linspace(0., 1, NY)]


def pixels2sprite(pixels):
    # For now we write to a temporary file and re-load, but there has to be
    # another way!
    image = Image.fromarray(pixels.astype(np.uint8))
    tmp = tempfile.mktemp() + '.jpg'
    image.save(tmp)
    return pyglet.image.load(tmp)


class Ball(object):

    def __init__(self, x0, y0, r, vx, vy, color=(1, 1, 1, 1)):

        self.x0 = x0
        self.y0 = y0
        self.r = r
        self.vx = vx
        self.vy = vy

        X, Y = np.indices((2 * r, 2 * r)) - r
        R = np.hypot(X, Y) < r
        pixels = np.array(color) * R.astype(float)[:, :, None] * 255
        self.sprite = pixels2sprite(pixels)

    def blit(self):
        self.sprite.blit(self.x0 - self.r, self.y0 - self.r)

    def move(self, dt):

        self.x0 += self.vx * dt
        self.y0 += self.vy * dt

        if self.x0 < self.r:
            self.vx = -self.vx
            self.x0 = self.r
        if self.x0 > WINDOW_WIDTH - self.r:
            self.vx = -self.vx
            self.x0 = WINDOW_WIDTH - self.r
        if self.y0 > WINDOW_HEIGHT - self.r:
            self.vy = -self.vy
            self.y0 = WINDOW_HEIGHT - self.r

    def collides(self, rect):

        if self.x0 > rect.x0 and self.x0 < rect.x0 + rect.dx:
            if self.y0 < rect.y0 + rect.dy + self.r and self.y0 > rect.y0 - self.r:
                return True

        if self.y0 > rect.y0 and self.y0 < rect.y0 + rect.dy:
            if self.x0 < rect.x0 + rect.dx + self.r and self.x0 > rect.x0 - self.r:
                return True

        if np.hypot(self.x0 - rect.x0, self.y0 - rect.y0) < self.r:
            return True

        if np.hypot(self.x0 - (rect.x0 + rect.dx), self.y0 - rect.y0) < self.r:
            return True

        if np.hypot(self.x0 - rect.x0, self.y0 - (rect.y0 + rect.dy)) < self.r:
            return True

        if np.hypot(self.x0 - (rect.x0 + rect.dx), self.y0 - (rect.y0 + rect.dy)) < self.r:
            return True

        return False


class Rectangle(object):

    def __init__(self, x0, y0, dx, dy, color=(1, 1, 1, 1)):

        # Store position and size
        self.x0 = x0
        self.y0 = y0
        self.dx = dx
        self.dy = dy

        # Generate sprite
        pixels = np.array(color) * np.ones((dy, dx, 4)) * 255
        self.sprite = pixels2sprite(pixels)

    def blit(self):
        self.sprite.blit(self.x0, self.y0)

r = Rectangle(0, 0, 10, 10, color=(1, 0, 1, 1))


window = pyglet.window.Window(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, resizable=False)
window.clear()

# Set up bricks

bricks = []
for i in range(NX):
    for j in range(NY):
        x0 = MARGIN + (BRICK_WIDTH + MARGIN) * i
        y0 = WINDOW_HEIGHT - ((BRICK_HEIGHT + MARGIN) * (j + 1))
        bricks.append(Rectangle(x0, y0, BRICK_WIDTH, BRICK_HEIGHT, color=COLORS[j]))


# Set up paddle

paddle = Rectangle(WINDOW_WIDTH / 2. - PADDLE_WIDTH / 2., 0, PADDLE_WIDTH, PADDLE_HEIGHT)

# Set up ball

import random
ball = Ball(WINDOW_WIDTH / 2., EMPTY_HEIGHT / 2., BALL_RADIUS, random.uniform(-5, 5), 400)


def update(dt):

    ball.move(dt)

    if ball.collides(paddle):
        ball.vy = -ball.vy
        ball.vx = ball.x0 - paddle.x0 - paddle.dx / 2 * 4

    for brick in bricks:
        if ball.collides(brick):
            ball.vy = -ball.vy
            bricks.remove(brick)
            break


@window.event
def on_mouse_motion(x, y, dx, dy):
    paddle.x0 = max(0, min(WINDOW_WIDTH, x - paddle.dx / 2.))


@window.event
def on_draw():
    window.clear()
    for brick in bricks:
        brick.blit()
    paddle.blit()
    ball.blit()

pyglet.clock.schedule_interval(update, 0.02)

pyglet.app.run()
