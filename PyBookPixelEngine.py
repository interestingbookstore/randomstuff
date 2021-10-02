import numpy
import pygame


def do_nothing():
    pass


pygame.init()
_run = False
_screen = None
_xres = None
_yres = None
_pixels = None
_update_loop = do_nothing
scaling = 1
_clock = pygame.time.Clock()
_delta = 0
_debug_fps = True


def update_loop(function):
    global _update_loop
    _update_loop = function


def init_screen(resx, resy):
    global _screen, _pixels, xres, yres
    xres, yres = resx, resy
    _screen = pygame.display.set_mode((resx, resy))
    _pixels = numpy.zeros((xres, yres, 3))


def set_pixel(x, y, color):
    global _pixels
    # for channel in range(3):
    #     _pixels[x, yres - y - 1, channel] = color[channel]

    if len(color) == 4:
        o = color[3] / 255
        color = color[:3]
        old_color = _pixels[x, y]
        for channel in range(3):
            _pixels[x, yres - y - 1, channel] = round(color[channel] * o + old_color[channel] * (1 - o))
    else:
        for channel in range(3):
            _pixels[x, yres - y - 1, channel] = color[channel]


def fill(color):
    global _pixels

    for channel in range(3):
        _pixels[:, :, channel] = color[channel]


def run_game():
    global _run, _delta
    _run = True
    try:
        while _run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    _run = False
                    pygame.quit()
                    raise SystemExit

            pixels = pygame.surfarray.pixels3d(_screen)
            for channel in range(3):
                # interp = NearestNDInterpolator((_pixels[:, :, channel]))
                # pixels2 = numpy.array(Image.fromarray(_pixels).resize(xres * scaling, yres * scaling, Image.NEAREST))
                pixels[:, :, channel] = _pixels[:, :, channel]
            del pixels

            _update_loop()

            pygame.display.flip()
            _delta += _clock.tick()
            if _delta >= 1000:
                _delta = 0
                if _debug_fps:
                    print(_clock.get_fps())
    except SystemExit:
        pass


def distance(point1, point2, distances_given=False):
    if not distances_given:
        point1, point2 = point1[0] - point2[0], point1[1] - point2[1]
    return (point1 ** 2 + point2 ** 2) ** 0.5


def normalized(vector):
    distance2 = distance(vector[0], vector[1], True)

    if distance2 == 0:
        return vector

    return vector[0] / distance2, vector[1] / distance2


def lerp(from_point, to_point, weight=0.5):
    movement_vector = from_point[0] - to_point[0], from_point[1] - to_point[1]
    if isinstance(from_point, Vector2):
        return Vector2(from_point[0] + movement_vector[0] * weight, from_point[1] + movement_vector[1] * weight)
    return from_point[0] + movement_vector[0] * weight, from_point[1] + movement_vector[1] * weight


class Vector2:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.stuff = self.x, self.y

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def normalize(self):
        magnitude = distance(self.x, self.y, True)
        self.x /= magnitude
        self.y /= magnitude

    def move_toward(self, target, speed=1):
        movement_vector = target[0] - self.x, target[1] - self.y
        dist = distance(movement_vector[0], movement_vector[1], True)
        movement_vector = normalized(movement_vector)

        if speed > dist:
            speed = dist

        movement_vector = movement_vector[0] * speed, movement_vector[1] * speed

        self.x += movement_vector[0]
        self.y += movement_vector[1]

    def __eq__(self, other):
        if self.stuff == other:
            return True
        return False

    def __ne__(self, other):
        if self.x != other[0] and self.y != other[1]:
            return True
        return False

    def __getitem__(self, item):
        return self.stuff[item]

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError

    def __len__(self):
        return 2

    def check(self, other):
        if isinstance(other, Vector2) or type(other) == tuple or type(other) == list:
            if len(other) != 2:
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif type(other) == int or type(other) == float:
            other = other, other
        else:
            raise TypeError(f'Vector2, tuple, list, int, or float object expected, but {type(other)} given.')
        return other

    def round(self):
        pass
        # self.x, self.y = round(self.x), round(self.y)

    def __add__(self, other):
        if type(other) == tuple or type(other) == list:
            if not (len(other) == 1 or len(other) == 2):
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif not isinstance(other, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(other)} given.')

        if len(other) == 1:
            return self.x + other, self.y + other
        return self.x + other[0], self.y + other[1]

    def __sub__(self, other):  # subtraction
        if type(other) == tuple or type(other) == list:
            if not (len(other) == 1 or len(other) == 2):
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif not isinstance(other, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(other)} given.')

        if len(other) == 1:
            return self.x - other, self.y - other
        return self.x - other[0], self.y - other[1]

    def __mul__(self, other):
        other = self.check(other)

        return self.x * other[0], self.y * other[1]

    def __truediv__(self, other):
        if type(other) == tuple or type(other) == list:
            if not (len(other) == 1 or len(other) == 2):
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif not isinstance(other, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(other)} given.')

        if len(other) == 1:
            return self.x / other, self.y / other
        return self.x / other[0], self.y / other[1]

    def __floordiv__(self, other):
        if type(other) == tuple or type(other) == list:
            if not (len(other) == 1 or len(other) == 2):
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif not isinstance(other, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(other)} given.')

        if len(other) == 1:
            return self.x // other, self.y // other
        return self.x // other[0], self.y // other[1]

    def __pow__(self, power, modulo=None):
        if type(power) == tuple or type(power) == list:
            if not (len(power) == 1 or len(power) == 2):
                raise Exception(f'{type(power)} object given, but length is {len(power)}, when it should be either one or two.')
        elif not isinstance(power, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(power)} given.')

        if len(power) == 1:
            return self.x ** power, self.y ** power
        return self.x ** power[0], self.y ** power[1]

    def __iadd__(self, other):
        other = self.check(other)
        self.x += other[0]
        self.y += other[1]
        self.round()

    def __isub__(self, other):  # subtraction
        if type(other) == tuple or type(other) == list:
            if not (len(other) == 1 or len(other) == 2):
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif not isinstance(other, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(other)} given.')

        if len(other) == 1:
            self.x -= other
            self.y -= other
        else:
            self.x -= other[0]
            self.y -= other[1]

    def __imul__(self, other):
        other = self.check(other)
        print(f'{other=}')
        self.x *= other[0]
        self.y *= other[1]
        self.round()

    def __idiv__(self, other):
        if type(other) == tuple or type(other) == list:
            if not (len(other) == 1 or len(other) == 2):
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif not isinstance(other, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(other)} given.')

        if len(other) == 1:
            self.x /= other
            self.y /= other
        else:
            self.x /= other[0]
            self.y /= other[1]

    def __ifloordiv__(self, other):
        if type(other) == tuple or type(other) == list:
            if not (len(other) == 1 or len(other) == 2):
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif not isinstance(other, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(other)} given.')

        if len(other) == 1:
            self.x //= other
            self.y //= other
        else:
            self.x //= other[0]
            self.y //= other[1]

    def __ipow__(self, power, modulo=None):
        if type(power) == tuple or type(power) == list:
            if not (len(power) == 1 or len(power) == 2):
                raise Exception(f'{type(power)} object given, but length is {len(power)}, when it should be either one or two.')
        elif not isinstance(power, Vector2):
            raise TypeError(f'Vector2, tuple, or list object expected, but {type(power)} given.')

        if len(power) == 1:
            self.x **= power
            self.y **= power
        else:
            self.x **= power[0]
            self.y **= power[1]


# ----------------

def r(start, stop):
    if start > stop:
        for i in range(stop, start + 1):
            yield i
    else:
        for i in range(start, stop + 1):
            yield i


def draw_line(start, end, thickness, color):
    if len(color) == 3:
        color = color[0], color[1], color[2], 255

    top_left = list(start)
    if end[0] < start[0]:
        top_left[0] = end[0]
    if end[1] < start[1]:
        top_left[1] = end[1]

    sx, sy = start
    ex, ey = end

    if sx > ex:
        sx2 = ex - thickness
        ex2 = sx + thickness
    else:
        sx2 = sx - thickness
        ex2 = ex + thickness
    if sy > ey:
        sy2 = ey - thickness
        ey2 = sy + thickness
    else:
        sy2 = sy - thickness
        ey2 = ey + thickness

    draw_circle(start, thickness, color)
    draw_circle(end, thickness, color)

    for x in r(sx2, ex2):
        for y in r(sy2, ey2):
            line_length = ((sx - ex) ** 2 + (sy - ey) ** 2) ** 0.5
            dist = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
            dist2 = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
            if dist < dist2:
                distance_long = dist2
                cx, cy = sx, sy
            else:
                distance_long = dist
                cx, cy = ex, ey
            if cx - thickness <= x <= cx + thickness and cy - thickness <= y <= cy + thickness:
                if distance_long > line_length:
                    continue

            if end[0] == start[0]:
                intersection_x = start[0]
                intersection_y = y
            elif end[1] == start[1]:
                intersection_x = x
                intersection_y = start[1]
            else:
                slope_1 = (end[1] - start[1]) / (end[0] - start[0])
                slope_2 = -1 / slope_1
                offset_1 = start[1] - slope_1 * start[0]
                offset_2 = y - slope_2 * x
                intersection_x = (offset_2 - offset_1) / (slope_1 - slope_2)
                intersection_y = slope_2 * intersection_x + offset_2
            dist = ((x - intersection_x) ** 2 + (y - intersection_y) ** 2) ** 0.5
            if dist <= thickness:
                set_pixel(x, y, color)
            else:
                dist -= thickness
                if dist < 1:
                    set_pixel(x, y, (color[0], color[1], color[2], round(color[3] * (1 - dist))))


def draw_rectangle(x, y, width, height, color):
    if len(color) == 3:
        color = color[0], color[1], color[2], 255

    for x in range(x, x + width):
        for y in range(y, y + height):
            set_pixel(x, y, color)


def draw_circle(origin, radius, fill):
    if len(fill) == 3:
        fill = fill[0], fill[1], fill[2], 255
    origin = origin[0], origin[1]

    for x in r(origin[0] - radius, origin[0] + radius):
        for y in r(origin[1] - radius, origin[1] + radius):
            dist = distance((x, y), origin)

            if dist <= radius:
                set_pixel(x, y, fill)
            else:
                dist -= radius
                if dist < 1:
                    set_pixel(x, y, (fill[0], fill[1], fill[2], round(fill[3] * (1 - dist))))
