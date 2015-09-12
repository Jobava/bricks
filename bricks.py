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

    def __init__(self, xcen, ycen, r, vx, vy, color=(1, 1, 1, 1)):

        self.xcen = xcen
        self.ycen = ycen
        self.xcen_prev = None
        self.xcen_prev = None

        self.side_bounce = True

        self.r = r

        self.vx = vx
        self.vy = vy

        X, Y = np.indices((2 * r, 2 * r)) - r
        R = np.hypot(X, Y) < r
        pixels = np.array(color) * R.astype(float)[:, :, None] * 255
        self.sprite = pixels2sprite(pixels)

    @property
    def xmin(self):
        return self.xcen - self.r

    @property
    def xmax(self):
        return self.xcen + self.r

    @property
    def ymin(self):
        return self.ycen - self.r

    @property
    def ymax(self):
        return self.ycen + self.r

    def blit(self):
        self.sprite.blit(self.xmin, self.ymin)

    def move(self, dt):

        self.xcen_prev = self.xcen
        self.ycen_prev = self.ycen

        self.xcen += self.vx * dt
        self.ycen += self.vy * dt

        c1 = self.collide_vertical(0)
        c2 = self.collide_vertical(WINDOW_WIDTH)
        c3 = self.collide_horizontal(WINDOW_HEIGHT)

    def collide_vertical(self, x, y_range=None, side_bounce=False):
        if abs(self.xcen - x) < self.r and (y_range is None or y_range[0] < self.ycen < y_range[1]):
            self.vx = -self.vx
            if self.xcen_prev > x:
                self.xcen = x + self.r
            else:
                self.xcen = x - self.r
            return True
        else:
            return False

    def collide_horizontal(self, y, x_range=None, side_bounce=False):
        print(self.ycen, self.ymax, y)
        if abs(self.ycen - y) < self.r and (x_range is None or x_range[0] < self.xcen < x_range[1]):
            print(self.vy)
            self.vy = -self.vy
            if self.ycen_prev > y:
                self.ycen = y + self.r
            else:
                self.ycen = y - self.r
            if side_bounce:
                frac = (self.xcen - x_range[0]) / (x_range[1] - x_range[0]) - 0.5
                self.vx = self.vy * frac
            return True
        else:
            return False

    def collides(self, rect):

        c1 = self.collide_horizontal(rect.ymin, x_range=[rect.xmin, rect.xmax], side_bounce=rect.side_bounce)
        c2 = self.collide_horizontal(rect.ymax, x_range=[rect.xmin, rect.xmax], side_bounce=rect.side_bounce)
        c3 = self.collide_vertical(rect.xmin, y_range=[rect.ymin, rect.ymax], side_bounce=rect.side_bounce)
        c4 = self.collide_vertical(rect.xmax, y_range=[rect.ymin, rect.ymax], side_bounce=rect.side_bounce)

        return c1 or c2 or c3 or c4


class Rectangle(object):

    def __init__(self, x0, y0, dx, dy, color=(1, 1, 1, 1), side_bounce=False):

        self.xcen = x0 + dx / 2.
        self.ycen = y0 + dy / 2.
        self.dx = dx
        self.dy = dy

        self.side_bounce = side_bounce

        # Generate sprite
        pixels = np.array(color) * np.ones((dy, dx, 4)) * 255
        self.sprite = pixels2sprite(pixels)

    @property
    def xmin(self):
        return self.xcen - self.dx / 2.

    @property
    def xmax(self):
        return self.xcen + self.dx / 2.

    @property
    def ymin(self):
        return self.ycen - self.dy / 2.

    @property
    def ymax(self):
        return self.ycen + self.dy / 2.

    def blit(self):
        self.sprite.blit(self.xmin, self.ymin)

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

paddle = Rectangle(WINDOW_WIDTH / 2. - PADDLE_WIDTH / 2., 0, PADDLE_WIDTH, PADDLE_HEIGHT, side_bounce=True)

# Set up ball

import random
ball = Ball(WINDOW_WIDTH / 2., EMPTY_HEIGHT / 2., BALL_RADIUS, random.uniform(-5, 5), 400)

playing = True


def update(dt):

    global playing

    if not playing:
        return

    ball.move(dt)

    ball.collides(paddle)

    for brick in bricks:
        if ball.collides(brick):
            bricks.remove(brick)
            break

    if ball.collide_horizontal(0):
        ball.xcen = WINDOW_WIDTH / 2.
        ball.ycen = EMPTY_HEIGHT / 2.
        playing = False


@window.event
def on_mouse_motion(x, y, dx, dy):
    paddle.xcen = max(0, min(WINDOW_WIDTH, x))


@window.event
def on_mouse_press(*args):
    global playing
    if not playing:
        playing = True
        ball.vx = random.uniform(-5, 5)
        ball.vy = 400


@window.event
def on_draw():
    window.clear()
    for brick in bricks:
        brick.blit()
    paddle.blit()
    ball.blit()

pyglet.clock.schedule_interval(update, 0.02)

pyglet.app.run()
