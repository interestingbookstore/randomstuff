import pygame
import pygame.freetype
from copy import copy
from PIL import Image, ImageFilter, ImageDraw
from platform import system

if system().lower() == 'windows':
    import ctypes

    PROCESS_PER_MONITOR_DPI_AWARE = 2
    ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)


def image_stuff(image, scale=1):
    if type(image) == pygame.Surface:
        return image

    if type(image) == RectangleImage:
        return pygame.image.fromstring(image.image, (image.width, image.height), 'RGBA')

    if type(image) == str:
        image = Image.open(image).convert_alpha()

    center_info = False

    if type(scale) == tuple:
        image = image.resize(fit_image(image.size, scale))
        if image.size[0] == scale[0]:
            center_info = 0, (scale[1] - image.size[1]) // 2
        else:
            center_info = (scale[0] - image.size[0]) // 2, 0
    else:
        image = image.resize((round(image.size[0] * scale), round(image.size[1] * scale)))

    if not center_info:
        return pygame.image.fromstring(image.convert('RGBA').tobytes('raw', 'RGBA'), image.size, 'RGBA').convert_alpha()
    return pygame.image.fromstring(image.convert('RGBA').tobytes('raw', 'RGBA'), image.size, 'RGBA').convert_alpha(), center_info


def fit_image(image_res, maximum):
    x_fac = maximum[0] / image_res[0]
    y_fac = maximum[1] / image_res[1]

    if x_fac < y_fac:
        return maximum[0], round(image_res[1] * x_fac)
    return round(image_res[0] * y_fac), maximum[1]


def calculate_drop_shadow(size, blur):
    # It's broken and weird, whatever, I'll just use the unoptimized method
    s = Image.new('RGBA', (1, blur))
    s.putpixel((0, blur - 1), (0, 0, 0))
    s = s.filter(ImageFilter.GaussianBlur(blur // 2))
    s = s.resize((size[0], blur), 1)
    # s.show()

    c = Image.new('RGBA', (blur, blur))

    f = Image.new('RGBA', (size[0] + blur * 2, size[1] + blur * 2))
    f.paste(s, (blur, 0))
    f.paste(s.rotate(90), (size[0] - blur, blur))
    f.paste(s.rotate(180), (blur, size[1] + blur))
    f.paste(s.rotate(270), (0, blur))
    f.show()


class Sprite:
    def __init__(self, img, x, y, scale=1, drop_shadow=0):
        self.img = image_stuff(img, scale)
        self._old_img = img
        self.x = x
        self.y = y
        self.old_rect = pygame.Rect(0, 0, 0, 0)
        self.dim = self.img.get_size()
        self.scale = scale
        self.drop_shadow = drop_shadow

    def _draw(self, game, scene, screen, res, erase=False, background=None):
        # Flips a y coordinate vertically (since Pygame uses top-left as the origin)
        def ny(y):
            return res[1] - y

        self.img = image_stuff(self.img)
        self.dim = self.img.get_size()

        if not erase:
            # Blit the image, calculate a rectangle around it to update, merge it with the older rectangle (to erase the previous frame),
            # update that region, make the current rectangle the old rectangle (for the next frame)
            if self.drop_shadow != 0:
                ds = Image.new('RGBA', (self.dim[0] + self.drop_shadow * 4, self.dim[1] + self.drop_shadow * 4))
                draw = ImageDraw.Draw(ds)
                draw.rectangle((self.drop_shadow * 2, self.drop_shadow * 2, self.dim[0] + self.drop_shadow * 2, self.dim[1] + self.drop_shadow * 2), (0, 0, 0))
                ds = ds.filter(ImageFilter.GaussianBlur(self.drop_shadow))
                screen.blit(image_stuff(ds), (self.x - self.drop_shadow * 2, ny(self.y + self.dim[1] + self.drop_shadow * 2)))

            screen.blit(self.img, (self.x, ny(self.y + self.dim[1])))
        else:
            scene.set_background(background, False)
        rect = pygame.Rect(self.x - self.drop_shadow * 2, ny(self.y) - self.dim[1] - self.drop_shadow * 2, self.dim[0] + self.drop_shadow * 4, self.dim[1] + self.drop_shadow * 4)
        rect2 = pygame.Rect.union(rect, self.old_rect)
        pygame.display.update(rect2)
        self.old_rect = rect


class Line:
    def __init__(self, point_1, point_2, color=(255, 255, 255), thickness=1):
        self.p1 = point_1
        self.p2 = point_2
        self.color = color
        self.thickness = thickness
        self.old_rect = pygame.Rect(0, 0, 0, 0)

    def _draw(self, game, scene, screen, res, erase=False, background=None):
        # Flips a y coordinate vertically (since Pygame uses top-left as the origin)
        def ny(y):
            if type(y) == tuple:
                return y[0], res[1] - y[1]
            return res[1] - y

        if not erase:
            # Blit the image, calculate a rectangle around it to update, merge it with the older rectangle (to erase the previous frame),
            # update that region, make the current rectangle the old rectangle (for the next frame)
            pygame.draw.line(screen, self.color, ny(self.p1), ny(self.p2), self.thickness)
        else:
            scene.set_background(background, False)
        x_dis = self.p2[0] - self.p1[0]
        y_dis = ny(self.p2[1] - self.p1[1])
        if x_dis > 0:
            left = self.p1[0]
        else:
            left = self.p2[0]
        if y_dis > 0:
            top = ny(self.p2[1])
        else:
            top = ny(self.p1[1])

        rect = pygame.Rect(left - self.thickness, top - self.thickness, abs(x_dis) + self.thickness, abs(y_dis) + self.thickness)
        pygame.draw.rect(screen, (255, 0, 0), rect)
        rect2 = pygame.Rect.union(rect, self.old_rect)
        pygame.display.update(rect2)
        self.old_rect = rect


class Rectangle:
    def __init__(self, x, y, width, height, color=(255, 255, 255), outline_thickness=None, rounded_corners=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.outline_thickness = outline_thickness
        self.rounded_corners = rounded_corners
        self.old_rect = pygame.Rect(0, 0, 0, 0)

    def _draw(self, game, scene, screen, res, erase=False, background=None):
        def ny(y):
            return res[1] - y

        outline_thickness = self.outline_thickness if self.outline_thickness is not None else 1
        rounded_corners = self.rounded_corners if self.rounded_corners is not None else 1

        x = self.x
        width = self.width
        if width < 0:
            width *= -1
            x -= width - outline_thickness
        y = self.y
        height = self.height
        if height < 0:
            height *= -1
            y -= height - outline_thickness

        rect = pygame.Rect(x, ny(y) - height, width, height)
        update_rect = pygame.Rect(x - outline_thickness // 2, ny(y) - height - outline_thickness // 2, width + outline_thickness + 5, height + outline_thickness + 5)
        pygame.draw.rect(screen, self.color, rect, outline_thickness, rounded_corners)
        pygame.display.update(pygame.Rect.union(update_rect, self.old_rect))
        self.old_rect = update_rect


def do_nothing():
    pass


class RectangleImage:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.image = Image.new('RGBA', (width, height), color).tobytes('raw', 'RGBA')


class GameObject:
    def __init__(self, img, x, y, movement_speed, scale=1, speedcap=None, drag=None, borders=(True, True, True, True), resetcol=False, xc=0, yc=0, xc2=0, yc2=0):
        self.img = Sprite(img, x, y, scale)
        self.movement_speed = movement_speed
        self.speedcap = speedcap
        self.drag = drag
        self.x = x
        self.y = y
        self.xc = xc
        self.yc = yc
        self.xc2 = xc2
        self.yc2 = yc2
        self.dim = self.img.dim
        self.movedir = [0, 0]
        self.bordercollision = borders
        self.collided = [False, False, False, False]
        self.resetcol = resetcol

    def update(self, img, scale=1):
        self.img.update(img, scale)

    def _draw(self, game, scene, screen, res, erase=False, background=None):
        # Flips a y coordinate vertically (since Pygame uses top-left as the origin)
        def ny(y):
            return res[1] - y

        if not erase:
            # Add the acceleration to the current speed
            self.xc += self.xc2
            self.yc += self.yc2

            # Prevent the sprite from surpassing the speed-cap
            if self.speedcap is not None:
                if self.xc > self.speedcap:
                    self.xc = self.speedcap
                elif self.xc < -self.speedcap:
                    self.xc = -self.speedcap
                if self.yc > self.speedcap:
                    self.yc = self.speedcap
                elif self.yc < -self.speedcap:
                    self.yc = -self.speedcap

            # Reset the values if the sprite isn't moving, or if it is, figure out which way the sprite is moving
            if self.xc == 0:
                self.movedir[0] = 0
            if self.yc == 0:
                self.movedir[1] = 0

            if self.xc < 0:
                self.movedir[0] = 1
            elif self.xc > 0:
                self.movedir[0] = -1
            if self.yc > 0:
                self.movedir[1] = 1
            elif self.yc < 0:
                self.movedir[1] = -1

            # Slow the player down with a constant drag force
            if self.drag is not None:
                if self.movedir[0] == 1:
                    self.xc += self.drag
                elif self.movedir[0] == -1:
                    self.xc -= self.drag
                if self.movedir[1] == 1:
                    self.yc -= self.drag
                elif self.movedir[1] == -1:
                    self.yc += self.drag

            # Prevent the player from infinitely moving if drag isn't a factor of the current speed (xc, yc)
            if self.drag is not None:
                if 0 < abs(self.xc) < self.drag:
                    self.xc = 0
                elif 0 < abs(self.yc) < self.drag:
                    self.yc = 0

            # Apply velocity (xc, yc) to position (x, y)
            self.x += self.xc
            self.y += self.yc

            # Prevent the sprite from exiting the window, and cancel their velocity if they collide from the inside
            # (velocity is maintained if the sprite is teleported from the outside)
            self.collided = [False, False, False, False]

            if self.bordercollision[1]:
                if self.x - self.dim[0] // 2 <= 0:
                    if self.resetcol and self.movedir[0] == 1:
                        self.xc = 0
                    self.x = 0 + self.dim[0] // 2
                    self.collided[1] = True
            if self.bordercollision[2]:
                if self.x + self.dim[0] // 2 >= res[0]:
                    if self.resetcol and self.movedir[0] == -1:
                        self.xc = 0
                    self.x = res[0] - self.dim[0] // 2
                    self.collided[2] = True
            if self.bordercollision[0]:
                if self.y <= 0:
                    if self.resetcol and self.movedir[1] == -1:
                        self.yc = 0
                    self.y = 0
                    self.collided[0] = True
            if self.bordercollision[3]:
                if self.y >= res[1]:
                    if self.resetcol and self.movedir[1] == 1:
                        self.yc = 0
                    self.y = res[1]
                    self.collided[3] = True
        self.img.updatelocation(self.x, self.y)
        self.img.draw(game, scene, screen, res, erase, background)


class Text:
    def __init__(self, text, font, size, color, x, y):
        self.text = text
        self.font = font
        self.font2 = pygame.freetype.Font(font, size)
        self.fontsurf, self.rect = self.font2.render(text, color, size=size)
        self.dim = (self.rect.width, self.rect.height)
        self.size = size
        self.color = color
        self.x = x
        self.y = y
        self.oldrect = pygame.Rect(0, 0, 0, 0)
        self.updatetext = False

    def update(self):
        self.oldrect = copy(self.rect)
        self.font2 = pygame.freetype.Font(self.font, self.size)
        self.fontsurf, self.rect = self.font2.render(str(self.text), self.color, size=self.size)
        self.dim = (self.rect.width, self.rect.height)
        self.updatetext = True

    def _draw(self, game, scene, screen, res, erase=False, background=None):
        # Flips a y coordinate vertically (since Pygame uses top-left as the origin)
        def ny(y):
            return res[1] - y

        if not erase:
            # Blit the image, calculate a rectangle around it to update, merge it with the older rectangle (to erase the previous frame),
            # update that region, make the current rectangle the old rectangle (for the next frame)
            screen.blit(self.fontsurf, (self.x - self.dim[0] // 2, ny(self.y + self.dim[1] // 2)))
            # print((self.x - self.dim[0] // 2, ny(self.y + self.dim[1] // 2)))
        else:
            screen.fill(background)
        rect = pygame.Rect(self.x - self.dim[0], ny(self.y + self.dim[1]), self.dim[0] * 2, self.dim[1] * 2)
        if self.updatetext:
            rect2 = pygame.Rect.union(rect, self.oldrect)
            pygame.display.update(rect2)
            self.updatetext = False
        else:
            pygame.display.update(rect)

    def changetext(self, new_text):
        self.text = new_text
        self.update()


class Button:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.sprite = Sprite(Rectangle(self.width, self.height, self.color), self.x, self.y, 0, 1)
        self.pressed = False

    def _draw(self, game, scene, screen, res):
        status = scene.mouse_test('left')
        if status == 1:
            if self.x - round(self.width / 2) <= game.mouseposition[0] <= self.x + round(self.width / 2) and self.y - round(self.width / 2) <= game.mouseposition[1] <= self.y + round(self.height / 2):
                self.pressed = True
        elif status == -1:
            self.pressed = False

        if self.pressed:
            self.sprite.img = Rectangle(self.width, self.height, tuple([i - 50 for i in self.color]))
            self.sprite.update()
        else:
            self.sprite.img = Rectangle(self.width, self.height, self.color)
            self.sprite.update()
        self.sprite.draw(game, scene, screen, res)


class Game:
    def __init__(self, res, fps, fullscreen=False, title='Untitled Game', icon=None, frame=True):
        self.current_scene = None
        self.run = True
        self.res = res
        self.framerate = fps
        self.fullscreen = fullscreen

        self.input_downs = []
        self.input_ups = []
        self.currently_pressed = []
        self.mouse_position = (0, 0)
        self.quit_letters = ['q', 'u', 'i', 't']
        self.quit_progress = 0

        self.delta = 0
        self._previous_frame_total_ticks = 0

        pygame.init()
        if self.fullscreen:
            if frame:
                self.screen = pygame.display.set_mode(self.res, pygame.FULLSCREEN, pygame.HWSURFACE)
            else:
                self.screen = pygame.display.set_mode(self.res, pygame.FULLSCREEN, pygame.NOFRAME, pygame.HWSURFACE)
        else:
            if frame:
                self.screen = pygame.display.set_mode(self.res, pygame.HWSURFACE)
            else:
                self.screen = pygame.display.set_mode(self.res, pygame.NOFRAME, pygame.HWSURFACE)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(title)
        if icon is not None:
            pygame.display.set_icon(pygame.image.load(icon))
        self.display_resolution = self.screen.get_size()

    def ny(self, y):
        return self.res[1] - y

    def run_game(self):
        mouse = pygame.mouse
        while self.run:
            self.clock.tick(self.framerate)
            t = pygame.time.get_ticks()
            self.input_ups.clear()
            self.input_downs.clear()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

                if event.type == pygame.KEYDOWN:
                    self.input_downs.append(pygame.key.name(event.key))
                    if pygame.key.name(event.key) == self.quit_letters[self.quit_progress]:
                        self.quit_progress += 1
                        if self.quit_progress == len(self.quit_letters):
                            self.run = False
                    else:
                        self.quit_progress = 0
                if event.type == pygame.KEYUP:
                    self.input_ups.append(pygame.key.name(event.key))

                if event.type == pygame.MOUSEMOTION:
                    position = mouse.get_pos()
                    self.mouse_position = (position[0], self.res[1] - position[1])
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pressed = mouse.get_pressed(3)
                    if pressed[0]:
                        self.input_downs.append('left')
                    if pressed[2]:
                        self.input_downs.append('right')
                    if pressed[1]:
                        self.input_downs.append('middle')
                if event.type == pygame.MOUSEBUTTONUP:
                    pressed = mouse.get_pressed(3)
                    if not pressed[0] and 'left' in self.currently_pressed:
                        self.input_ups.append('left')
                    if not pressed[2] and 'right' in self.currently_pressed:
                        self.input_ups.append('right')
                    if not pressed[1] and 'middle' in self.currently_pressed:
                        self.input_ups.append('middle')

            for i in self.input_downs:
                self.currently_pressed.append(i)

            for i in self.input_ups:
                self.currently_pressed.remove(i)

            self.current_scene.run_scene()
            self.delta = (t - self._previous_frame_total_ticks) / 1000
            self._previous_frame_total_ticks = t

    def just_pressed(self, button):
        if button in self.input_downs:
            return 1
        elif button in self.input_ups:
            return -1
        else:
            return 0

    def is_pressed(self, button):
        if button in self.currently_pressed:
            return True
        return False

    def quit(self):
        self.run = False

    def switch_scene(self, scene):
        self.current_scene = scene
        scene.redraw = True

    class Scene:
        def __init__(self, game):
            self.game = game
            self.stuff = []
            self.update_func = do_nothing
            self.background = 0, 0, 0
            self.background_center = 0, 0
            self.redraw = False

            self.animations = []
            self.animation_calls = 0

        def set_background(self, background, _update=True):
            if type(background) == pygame.Surface:
                self.background = background
                self.game.screen.blit(self.background, self.background_center)
            elif type(background) == tuple:
                self.background = background
                self.game.screen.fill(self.background)
            else:
                self.background, self.background_center = image_stuff(background, self.game.res)
                self.game.screen.blit(self.background, self.background_center)
            if _update:
                self.redraw = True

        def animate(self, start, stop, seconds=1):
            if len(self.animations) == 0 or self.animations[self.animation_calls][0] != (start, stop, seconds):
                self.animations.append([(start, stop, seconds), seconds, seconds / (stop - start), start, True])
                # print('hi')

            # (ID)     time_left     next_milestone     to_return_on_next_milestone     active
            #  0           1               2                        3                     4

            corresponding = self.animations[self.animation_calls]
            if corresponding[3] > stop:
                self.animations[self.animation_calls][4] = False
            if corresponding[4]:
                self.animations[self.animation_calls][1] -= self.game.delta
                to_return = None
                # print(f'{corresponding[3]}               {corresponding[4]}')
                if corresponding[1] <= seconds - corresponding[2]:
                    # print('hey')
                    to_return = corresponding[3]
                    self.animations[self.animation_calls][3] += 1
                    self.animations[self.animation_calls][2] += seconds / (stop - start)

                self.animation_calls += 1
                if to_return is not None:
                    return to_return

        def run_scene(self):
            self.animation_calls = 0
            self.update_func(self.game.delta)
            self.set_background(self.background, False)

            if self.redraw:
                pygame.display.flip()
                self.redraw = False

            for i in self.stuff:
                i._draw(self.game, self, self.game.screen, self.game.res)

        def game_update(self, func):
            self.update_func = func

        def add(self, *objects):
            if type(objects[0]) == tuple or type(objects[0]) == list:
                for i in objects[0]:
                    self.stuff.append(i)
            else:
                for i in objects:
                    self.stuff.append(i)

        def remove(self, *objects):
            for i in objects:
                for index, j in enumerate(self.stuff):
                    if i == j:
                        self.stuff.pop(index)
                        i.draw(self.game, self, self.game.screen, self.game.res, erase=True, background=self.background)

        def update_obj(self, obj):
            obj.update()
            obj.draw(self.game.screen, self.game.res)

        def key_bind(self, key, value, value2, negative, key_down_list, key_up_list):
            if key in key_down_list:
                value += value2 if negative else -value2
            elif key in key_up_list:
                value -= value2 if negative else -value2
            return value

        def dist(self, obj1, obj2):
            return (abs(obj1.x - obj2.x) ** 2 + abs(obj1.y - obj2.y) ** 2) ** 0.5