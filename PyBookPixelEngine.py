import numpy
import pygame
import math
from PyBookImages import *



# Made by interestingbookstore
# Github: https://github.com/interestingbookstore/randomstuff
# -----------------------------------------------------------------------
# Version released on December 31 2021
# ---------------------------------------------------------



def do_nothing():
    pass


pygame.init()
_mouse = pygame.mouse
_run = False
_screen = None
_pixels = None
_update_loop = do_nothing
scaling = 1  # NOT IMPLEMENTED
_clock = pygame.time.Clock()
_delta = 0
DEBUG_FPS = False
custom_update_rects = False
update_rects = []


def image_stuff(image):
    if type(image) == pygame.Surface:
        return image

    if isinstance(image, PyBookImage):
        return pygame.image.fromstring(image.to_bytes(), image.size, 'RGBA').convert_alpha()

    if type(image) == str:
        image = Image.open(image)
    return pygame.image.fromstring(image.convert('RGBA').tobytes('raw', 'RGBA'), image.size, 'RGBA').convert_alpha()


def update_loop(function):
    global _update_loop
    _update_loop = function


def init_screen(resx, resy=None):
    global _screen, _pixels, xres, yres
    if resy is None:
        resx, resy = resx
    xres, yres = resx, resy
    _screen = pygame.display.set_mode((resx, resy))
    _pixels = numpy.zeros((xres, yres, 3))


def draw_image(image, x, y):
    image = image_stuff(image)
    _screen.blit(image, (x, yres - y - image.get_height()))  # For some reason you don't need to subtract 1 from the y? IDK, I'm tired, whatever.


def set_pixel(x, y, color):
    x, y = round(x), round(y)
    if len(color) == 3:
        color = color[0], color[1], color[2], 255

    if 0 <= x < xres and 0 <= y < yres:
        if color[3] != 255:
            o = color[3] / 255
            color = color[:3]
            old_color = _pixels[x, y]
            for channel in range(3):
                _pixels[x, yres - y - 1, channel] = round(color[channel] * o + old_color[channel] * (1 - o))
        else:
            for channel in range(3):
                _pixels[x, yres - y - 1, channel] = color[channel]


def fill(color, color2=None, color3=None):
    if ((color2 is None) or (color3 is None)) and (color2 != color3):
        raise Exception('Either one or all three of the parameters are required')
    if color2 is not None:
        color = color, color2, color3
    for channel in range(3):
        _pixels[:, :, channel] = color[channel]


def update_screen(x, y, width, height):
    update_rects.append((x, y, width, height))


class TwoDimensionalList:
    def __init__(self, single_list, width):
        self.stuff = single_list
        self.width = width
        self.height = len(single_list) // self.width
        self.fancy_list = []
        fancy_buffer = []
        for i in self.stuff:
            fancy_buffer.append(i)
            if len(fancy_buffer) == self.width:
                self.fancy_list.append(fancy_buffer.copy())
                fancy_buffer.clear()
        if fancy_buffer:
            self.fancy_list.append(fancy_buffer)
        self.coords = []
        for index, _ in enumerate(self.stuff):
            self.coords.append((index % self.width, index // self.width))

    def check(self, index):
        if type(index) == list or type(index) == tuple:
            return index[0] + index[1] * self.width, index
        return index, (index % self.width, index // self.width)

    def __contains__(self, item):
        if self.check(item)[0] < len(self.stuff):
            return True
        return False

    def __getitem__(self, item):
        return self.stuff[self.check(item)[0]]

    def __setitem__(self, key, value):
        keys = self.check(key)
        self.stuff[keys[0]] = value
        self.fancy_list[keys[1][1]][keys[1][0]] = value

    def __repr__(self):
        return str('\n'.join(reversed([str(i) for i in self.fancy_list])))


input_downs = []  # Keys that were just now pressed
input_ups = []  # Keys that were just now released
currently_pressed = []  # Keys that were pressed but haven't yet been released
mouse_position = [0, 0]  # variables are weird; if I make this an immutable tuple, and redefine it every frame, I'm guessing that each redefinition breaks the original variable's links. Thereby keeping any references at (0, 0). So, it has to be a list.


def run_game():
    global _run, _delta, custom_update_rects
    _run = True
    try:
        while _run:
            input_downs.clear()
            input_ups.clear()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    _run = False
                    pygame.quit()
                    raise SystemExit
                elif event.type == pygame.KEYDOWN:
                    key = pygame.key.name(event.key)
                    if key == 'left' or key == 'right' or key == 'up' or key == 'down':
                        key += '_arrow'
                    key = key.replace(' ', '_')
                    if key == 'left_shift' or key == 'right_shift':
                        input_downs.append('shift')
                    input_downs.append(key)
                elif event.type == pygame.KEYUP:
                    key = pygame.key.name(event.key)
                    if key == 'left' or key == 'right' or key == 'up' or key == 'down':
                        key += '_arrow'
                    key = key.replace(' ', '_')
                    if key == 'left_shift' or key == 'right_shift':
                        input_ups.append('shift')
                    input_ups.append(key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pressed = _mouse.get_pressed(3)
                    if pressed[0]:
                        input_downs.append('left')
                    if pressed[1]:
                        input_downs.append('middle')
                    if pressed[2]:
                        input_downs.append('right')
                elif event.type == pygame.MOUSEBUTTONUP:
                    pressed = _mouse.get_pressed(3)
                    if not pressed[0] and 'left' in currently_pressed:
                        input_ups.append('left')
                    if not pressed[1] and 'middle' in currently_pressed:
                        input_ups.append('middle')
                    if not pressed[2] and 'right' in currently_pressed:
                        input_ups.append('right')
                elif event.type == pygame.MOUSEMOTION:
                    pos = _mouse.get_pos()
                    mouse_position[0] = pos[0]
                    mouse_position[1] = yres - pos[1]

            for key in input_downs:
                currently_pressed.append(key)
            for key in input_ups:
                currently_pressed.remove(key)

            pixels = pygame.surfarray.pixels3d(_screen)
            for channel in range(3):
                pixels[:, :, channel] = _pixels[:, :, channel]
            del pixels

            try:
                _update_loop(_delta)
            except TypeError:
                _update_loop()

            if update_rects or custom_update_rects:
                if not custom_update_rects:
                    custom_update_rects = True

                for (x, y, width, height) in update_rects:
                    pygame.display.update(x, yres - y - 1 - height, width, height)

                update_rects.clear()
            else:
                pygame.display.flip()
            _delta += _clock.tick()
            if _delta >= 1000:
                _delta = 0
                if DEBUG_FPS:
                    print(_clock.get_fps())
    except SystemExit:  # To end the loop immediately after "event.type == pygame.QUIT"
        pass


def just_pressed(*keys, type='and'):
    if type == 'and':
        for key in keys:
            if key not in input_downs:
                return False
        return True
    elif type == 'or':
        for key in keys:
            if key in input_downs:
                return True
        return False
    raise Exception(f'"type" can be "and" (meaning all of the keys must be pressed down) or "or" (meaning at least one key must be pressed down), but "{type}" was given.')


def just_released(*keys, type='and'):
    if type == 'and':
        for key in keys:
            if key not in input_ups:
                return False
        return True
    elif type == 'or':
        for key in keys:
            if key in input_ups:
                return True
        return False
    raise Exception(f'"type" can be "and" (meaning all of the keys must be released) or "or" (meaning at least one key must be released), but "{type}" was given.')


def just_interacted(*keys, type='and'):
    if type == 'and':
        for key in keys:
            if key not in (input_ups or input_downs):
                return False
        return True
    elif type == 'or':
        for key in keys:
            if key in (input_ups or input_downs):
                return True
        return False
    raise Exception(f'"type" can be "and" (meaning all of the keys must be released) or "or" (meaning at least one key must be released), but "{type}" was given.')


def is_pressed(*keys, type='and'):
    if type == 'and':
        for key in keys:
            if key not in currently_pressed:
                return False
        return True
    elif type == 'or':
        for key in keys:
            if key in currently_pressed:
                return True
        return False
    raise Exception(f'"type" can be "and" (meaning all of the keys must be pressed down) or "or" (meaning at least one key must be pressed down), but "{type}" given.')


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
    movement_vector = to_point[0] - from_point[0], to_point[1] - from_point[1]
    if isinstance(from_point, Vector2):
        return Vector2(from_point[0] + movement_vector[0] * weight, from_point[1] + movement_vector[1] * weight)
    return from_point[0] + movement_vector[0] * weight, from_point[1] + movement_vector[1] * weight


class Vector2:
    def __init__(self, x: int or float or tuple or list or Vector2, y=None):
        if y is None:
            if type(x) == tuple or type(x) == list or type(x) == Vector2:
                x, y = x
            else:
                raise Exception(f'y value not provided, x value was {x}')
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

    def __floor__(self):
        return Vector2(math.floor(self.x), math.floor(self.y))

    def __ceil__(self):
        return Vector2(math.ceil(self.x), math.ceil(self.y))

    def __trunc__(self):
        return Vector2(math.trunc(self.x), math.trunc(self.y))

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

    def __neg__(self):
        return Vector2(self * -1)

    def check(self, other):
        if isinstance(other, Vector2) or type(other) == tuple or type(other) == list:
            if len(other) != 2:
                raise Exception(f'{type(other)} object given, but length is {len(other)}, when it should be either one or two.')
        elif type(other) == int or type(other) == float:
            other = other, other
        else:
            raise TypeError(f'Vector2, tuple, list, int, or float object expected, but {type(other)} given.')
        return other

    def round(self, n=None):  # Round self
        self.x, self.y = self.__round__(n)

    def __round__(self, n=None):  # Return rounded version of self
        if n is None:
            return Vector2(round(self.x), round(self.y))
        return Vector2(round(self.x, n), round(self.y, n))

    def __add__(self, other):
        other = self.check(other)
        return Vector2(self.x + other[0], self.y + other[1])

    def __sub__(self, other):  # subtraction
        other = self.check(other)
        return Vector2(self.x - other[0], self.y - other[1])

    def __mul__(self, other):
        other = self.check(other)
        return Vector2(self.x * other[0], self.y * other[1])

    def __truediv__(self, other):
        other = self.check(other)
        return Vector2(self.x / other[0], self.y / other[1])

    def __floordiv__(self, other):
        other = self.check(other)
        return Vector2(self.x // other[0], self.y // other[1])

    def __pow__(self, power, modulo=None):
        power = self.check(power)
        return Vector2(self.x ** power[0], self.y ** power[1])

    def __iadd__(self, other):
        other = self.check(other)
        self.x += other[0]
        self.y += other[1]

    def __isub__(self, other):  # subtraction
        other = self.check(other)
        self.x -= other[0]
        self.y -= other[1]

    def __imul__(self, other):
        other = self.check(other)
        self.x *= other[0]
        self.y *= other[1]

    def __idiv__(self, other):
        other = self.check(other)
        self.x /= other[0]
        self.y /= other[1]

    def __ifloordiv__(self, other):
        other = self.check(other)
        self.x //= other[0]
        self.y //= other[1]

    def __ipow__(self, power, modulo=None):
        power = self.check(power)

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
    for x2 in range(x, x + width):
        for y2 in range(y, y + height):
            set_pixel(x2, y2, color)


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


def draw_optimized_line(start, end, color):
    start = start[0], yres - start[1] - 1
    end = end[0], yres - end[1] - 1
    pygame.draw.aaline(_screen, color, start, end)
