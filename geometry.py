def sign(x):
    return x / abs(x)


class Segment(object):

    def __init__(self, x0, x1, y0, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def is_within_distance(self, x, y):
        raise NotImplementedError()


class HorizontalSegment(Segment):

    def __init__(self, x0, x1, y):
        super(HorizontalSegment, self).__init__(x0, x1, y, y)

    def is_within_distance(self, x, y, distance):
        if abs(self.y0 - y) > distance:
            return False
        elif x < self.x0 - distance:
            return False
        elif x > self.x1 + distance:
            return False
        elif x < self.x0:
            return ((x - self.x0)**2 + (y - self.y0)**2) < distance ** 2
        elif x > self.x1:
            return ((x - self.x1)**2 + (y - self.y1)**2) < distance ** 2
        else:
            return True

    def reflect(self, x, y, vx, vy, distance, side_bounce=False):
        if side_bounce:
            offset = (x - self.x0) / (self.x1 - self.x0) - 0.5
            return x, self.y0 - sign(vy) * distance, -vy * offset, -vy
        else:
            return x, self.y0 - sign(vy) * distance, vx, -vy


class VerticalSegment(HorizontalSegment):

    def __init__(self, x, y0, y1):
        super(VerticalSegment, self).__init__(y0, y1, x)

    def is_within_distance(self, x, y, distance):
        return super(VerticalSegment, self).is_within_distance(y, x, distance)

    def reflect(self, x, y, vx, vy, distance, side_bounce=False):
        y, x, vy, vx = super(VerticalSegment, self).reflect(y, x, vy, vx, distance, side_bounce=side_bounce)
        return x, y, vx, vy


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    h = HorizontalSegment(1, 2, 1)
    v = VerticalSegment(4, 2, 3)
    import random
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for point in range(10000):
        x = random.uniform(0, 6)
        y = random.uniform(0, 6)
        print(x, y)
        if h.is_within_distance(x, y, 0.5) or v.is_within_distance(x, y, 0.5):
            ax.plot([x], [y], 'ro')
        else:
            ax.plot([x], [y], 'ko')
    fig.savefig('points.png')
