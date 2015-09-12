import random

import pyglet
import numpy as np

import settings
from geometry import HorizontalSegment, VerticalSegment
from sprites import Ball, Rectangle

# Set global options

window_width = (settings.brick_width + settings.margin) * settings.nx + settings.margin
window_height = settings.empty_height + (settings.brick_height + settings.margin) * settings.ny

# Initialize window

window = pyglet.window.Window(width=window_width, height=window_height, resizable=False)
window.clear()

# Prepare colormap

colors = [settings.cmap(x) for x in np.linspace(0., 1, settings.ny)]

window_edges = [HorizontalSegment(0, window.width, window.height),
                VerticalSegment(0, 0, window.height),
                VerticalSegment(window.width, 0, window.height)]

bottom_edge = [HorizontalSegment(0, window.width, 0)]


# Set up bricks

bricks = []
for i in range(settings.nx):
    for j in range(settings.ny):
        x0 = settings.margin + (settings.brick_width + settings.margin) * i
        y0 = window.height - ((settings.brick_height + settings.margin) * (j + 1))
        bricks.append(Rectangle(x0, y0, settings.brick_width, settings.brick_height, color=colors[j]))

# Set up paddle

paddle = Rectangle(window.width / 2. - settings.paddle_width / 2.,
                  0,
                  settings.paddle_width,
                  settings.paddle_height,
                  side_bounce=True)

# Set up ball

ball = Ball(window.width / 2.,
            settings.empty_height / 2.,
            settings.ball_radius,
            random.uniform(-5, 5), 400)

playing = True


def update(dt):

    global playing

    if not playing:
        return

    ball.move(dt)

    segment = ball.check_collision(window_edges)

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
        segment = ball.check_collision(bottom_edge)
        if segment is not None:
            ball.xcen = window.width / 2.
            ball.ycen = settings.empty_height / 2.
            playing = False
    else:
        ball.xcen, ball.ycen, ball.vx, ball.vy = segment.reflect(ball.xcen, ball.ycen,
                                                                 ball.vx, ball.vy, ball.r,
                                                                 side_bounce=side_bounce)


@window.event
def on_mouse_motion(x, y, dx, dy):
    paddle.xcen = max(0, min(window.width, x))


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
