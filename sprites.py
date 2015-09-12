import pyglet
import tempfile
import numpy as np
from PIL import Image
from geometry import HorizontalSegment, VerticalSegment


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

    def check_collision(self, edges):
        for segment in edges:
            if segment.is_within_distance(self.xcen, self.ycen, self.r):
                return segment


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
    def edges(self):
        return [HorizontalSegment(self.xmin, self.xmax, self.ymin),
                HorizontalSegment(self.xmin, self.xmax, self.ymax),
                VerticalSegment(self.xmin, self.ymin, self.ymax),
                VerticalSegment(self.xmax, self.ymin, self.ymax)]

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
