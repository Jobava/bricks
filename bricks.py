import random

import pyglet
import numpy as np
import matplotlib.pyplot as plt

from geometry import HorizontalSegment, VerticalSegment
from sprites import Ball, Rectangle

# Set global options

EMPTY_HEIGHT = 300
BRICK_WIDTH = 130
BRICK_HEIGHT = 20
NX = 7
NY = 12
MARGIN = 5
PADDLE_WIDTH = 130
PADDLE_HEIGHT = 17
BALL_RADIUS = 12

WINDOW_WIDTH = (BRICK_WIDTH + MARGIN) * NX + MARGIN
WINDOW_HEIGHT = EMPTY_HEIGHT + (BRICK_HEIGHT + MARGIN) * NY

CMAP = plt.cm.jet

# Prepare colormap

COLORS = [plt.cm.jet(x) for x in np.linspace(0., 1, NY)]

WINDOW_EDGES = [HorizontalSegment(0, WINDOW_WIDTH, WINDOW_HEIGHT),
                VerticalSegment(0, 0, WINDOW_HEIGHT),
                VerticalSegment(WINDOW_WIDTH, 0, WINDOW_HEIGHT)]

BOTTOM_EDGE = [HorizontalSegment(0, WINDOW_WIDTH, 0)]

# Initialize window

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

ball = Ball(WINDOW_WIDTH / 2., EMPTY_HEIGHT / 2., BALL_RADIUS, random.uniform(-5, 5), 400)

playing = True


def update(dt):

    global playing

    if not playing:
        return

    ball.move(dt)

    segment = ball.check_collision(WINDOW_EDGES)

    side_bounce = False

    if segment is None:
        segment = ball.check_collision(paddle.edges)
        if segment is not None:
            side_bounce = True

    if segment is None:
        for brick in bricks:
            segment = ball.check_collision(brick.edges)
            if segment is not None:
                bricks.remove(brick)
                break

    if segment is None:
        segment = ball.check_collision(BOTTOM_EDGE)
        if segment is not None:
            ball.xcen = WINDOW_WIDTH / 2.
            ball.ycen = EMPTY_HEIGHT / 2.
            playing = False
    else:
        ball.xcen, ball.ycen, ball.vx, ball.vy = segment.reflect(ball.xcen, ball.ycen,
                                                                 ball.vx, ball.vy, ball.r,
                                                                 side_bounce=side_bounce)


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

pyglet.clock.schedule_interval(update, 0.01)

pyglet.app.run()
