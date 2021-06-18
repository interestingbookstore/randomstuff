import pygame
import pygame.freetype
import ctypes
from copy import copy
from PIL import Image

PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)


def imagestuff(img, scale=1):
    if str(type(img)) == "<class 'PygameFuncLibrary.Rectangle'>":
        return pygame.image.fromstring(img.image, (img.width, img.height), 'RGBA')
    else:
        if scale == 1:
            return pygame.image.load(img)
        elif scale == 2:
            return pygame.transform.scale2x(pygame.image.load(img))
        else:
            img = pygame.image.load(img)
            imgsize = img.get_size()
            return pygame.transform.smoothscale(img, (round(imgsize[0] * scale), round(imgsize[1] * scale)))


class Sprite:
    def __init__(self, img, x, y, scale=1):
        self.img = imagestuff(img, scale)
        self.x = x
        self.y = y
        self.oldrect = pygame.Rect(0, 0, 0, 0)
        self.dim = self.img.get_size()
        self.scale = scale

    def update(self, img, scale=1):
        self.img = imagestuff(img, scale)

    def updatelocation(self, x, y):
        self.x = x
        self.y = y

    def draw(self, game, scene, screen, res, erase=False, background=None):
        # Flips a y coordinate vertically (since Pygame uses top-left as the origin)
        def ny(y):
            return res[1] - y

        if not erase:
            # Blit the image, calculate a rectangle around it to update, merge it with the older rectangle (to erase the previous frame),
            # update that region, make the current rectangle the old rectangle (for the next frame)
            screen.blit(self.img, (self.x - self.dim[0] // 2, ny(self.y + self.dim[1] // 2)))
        else:
            screen.fill(background)
        rect = pygame.Rect(self.x - self.dim[0], ny(self.y + self.dim[1]), self.dim[0] * 2, self.dim[1] * 2)
        rect2 = pygame.Rect.union(rect, self.oldrect)
        pygame.display.update(rect2)
        self.oldrect = rect


def do_nothing():
    pass


class Rectangle:
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

    def draw(self, game, scene, screen, res, erase=False, background=None):
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
        self.fontsurf, self.rect = self.font2.render(self.text, self.color, size=self.size)
        self.dim = (self.rect.width, self.rect.height)
        self.updatetext = True

    def draw(self, game, scene, screen, res, erase=False, background=None):
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

    def draw(self, game, scene, screen, res):
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
    def __init__(self, res, fps, fullscreen=False, title='Untitled Game', icon=None):
        self.current_scene = None
        self.run = True
        self.res = res
        self.framerate = fps
        self.fullscreen = fullscreen
        self.keydowns = []
        self.keyups = []
        self.mousedowns = []
        self.mouseups = []
        self.mouseposition = (0, 0)
        self.quit_letters = ['q', 'u', 'i', 't']
        self.quit_progress = 0

        pygame.init()
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.res, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.res)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(title)
        if icon is not None:
            pygame.display.set_icon(pygame.image.load(icon))

    def ny(self, y):
        return self.res[1] - y

    def run_game(self):
        mouse = pygame.mouse
        while self.run:
            self.clock.tick(60)

            self.keydowns.clear()
            self.keyups.clear()
            self.mousedowns.clear()
            self.mouseups.clear()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

                if event.type == pygame.KEYDOWN:
                    self.keydowns.append(pygame.key.name(event.key))
                    if pygame.key.name(event.key) == self.quit_letters[self.quit_progress]:
                        self.quit_progress += 1
                        if self.quit_progress == len(self.quit_letters):
                            self.run = False
                    else:
                        self.quit_progress = 0
                if event.type == pygame.KEYUP:
                    self.keyups.append(pygame.key.name(event.key))

                if event.type == pygame.MOUSEMOTION:
                    position = mouse.get_pos()
                    self.mouseposition = (position[0], self.res[1] - position[1])
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pressed = mouse.get_pressed(3)
                    if pressed[0]:
                        self.mousedowns.append('left')
                    if pressed[2]:
                        self.mousedowns.append('right')
                    if pressed[1]:
                        self.mousedowns.append('middle')
                if event.type == pygame.MOUSEBUTTONUP:
                    pressed = mouse.get_pressed(3)
                    if not pressed[0]:
                        self.mouseups.append('left')
                    if not pressed[2]:
                        self.mouseups.append('right')
                    if not pressed[1]:
                        self.mouseups.append('middle')

            self.current_scene.run_scene()

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
            self.background = (0, 0, 0)
            self.redraw = False

        def set_background(self, background, res=(0, 0)):
            if type(background) == tuple:
                self.background = background
                self.game.screen.fill(self.background)
            elif type(background) == bytes:
                self.background = pygame.image.fromstring(background, (res[0], res[1]), 'RGBA')
                self.game.screen.blit(self.background, (0, 0))
            else:
                img = Image.open(background)
                size = img.size
                res = self.game.res
                ratio = (res[0] / size[0]) / (res[1] / size[1])
                if ratio > 1:
                    img = img.resize((round(res[1] / size[1] * size[0]), res[1]), 3)
                elif ratio < 1:
                    img = img.resize((res[0], round(size[0] / res[0] * res[1])), 3)
                else:
                    img = img.resize((res[0], res[1]), 3)
                size = img.size

                newsize = (res[0] if ratio > 1 else size[0], res[1] if ratio < 1 else size[1])
                img2 = Image.new('RGBA', newsize, (0, 0, 0))
                img2.paste(img, (round((res[0] - size[0]) / 2) if ratio > 1 else 0, round((res[1] - size[1]) / 2) if ratio < 1 else 0), img)
                img2 = img2.convert('RGB')
                self.background = pygame.image.fromstring(img2.tobytes('raw', 'RGB'), newsize, 'RGB')
                self.game.screen.blit(self.background, (0, 0))

                # img = pygame.image.load(background)
                # imgsize = img.get_size()
                # res = self.game.res
                # print((round(res[0] / imgsize[0]), round(res[1] / imgsize[1])))
                # self.background = pygame.transform.smoothscale(img, (res[0], res[1]))
                # self.game.screen.blit(self.background, (0, 0))
            pygame.display.flip()

        def _change_background(self):
            if type(self.background) == tuple:
                self.game.screen.fill(self.background)
            else:
                self.game.screen.blit(self.background, (0, 0))

        def run_scene(self):
            self.update_func()

            self._change_background()

            if self.redraw:
                pygame.display.flip()
                self.redraw = False

            for i in self.stuff:
                i.draw(self.game, self, self.game.screen, self.game.res)

        def game_update(self, func):
            self.update_func = func

        def add(self, *args):
            if type(args[0]) == list:
                for i in args[0]:
                    self.stuff.append(i)
            else:
                for i in args:
                    self.stuff.append(i)

        def remove(self, *args):
            for i in args:
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

        def key_test(self, key):
            if key in self.game.keydowns:
                return 1
            elif key in self.game.keyups:
                return -1
            else:
                return 0

        def mouse_test(self, button):
            if button in self.game.mousedowns:
                return 1
            elif button in self.game.mouseups:
                return -1
            else:
                return 0

        def dist(self, obj1, obj2):
            return (abs(obj1.x - obj2.x) ** 2 + abs(obj1.y - obj2.y) ** 2) ** 0.5
