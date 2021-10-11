import pygame
import pygame.freetype
from PIL import Image, ImageFilter, ImageDraw, ImageDraw, ImageFont
from platform import system

if system().lower() == 'windows':
    import ctypes

    PROCESS_PER_MONITOR_DPI_AWARE = 2
    ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

# ---------------------------------------------------------------------------------------------
drop_shadow_high_res = Image.new('RGBA', (800, 800))
draw = ImageDraw.Draw(drop_shadow_high_res)
draw.rectangle((200, 200, 600, 600), (0, 0, 0))
drop_shadow_high_res = drop_shadow_high_res.filter(ImageFilter.GaussianBlur(100))
drop_shadow_high_res = drop_shadow_high_res.crop((600, 0, 800, 200))


# drop_shadow_high_res.save('000aaa_pre_render.png')
# ---------------------------------------------------------------------------------------------

# drop_shadow_high_res = Image.new('RGBA', (500, 500), (0, 0, 0, 0))
# drop_shadow_high_res.putpixel((0, 250 - 1), (0, 0, 0))
# drop_shadow_high_res = drop_shadow_high_res.filter(ImageFilter.GaussianBlur(250 // 2))
# ---------------------------------------------------------------------------------------------

def image_stuff(image, scale=1):
    if type(image) == pygame.Surface:
        return image

    if type(image) == str:
        image = Image.open(image).convert()

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


def fit_image(image_res, maximum, scale_up=True):
    x_fac = maximum[0] / image_res[0]
    y_fac = maximum[1] / image_res[1]

    if not scale_up and x_fac >= 1 and y_fac >= 1:
        return image_res[0], image_res[1]

    if x_fac < y_fac:
        return maximum[0], round(image_res[1] * x_fac)
    return round(image_res[0] * y_fac), maximum[1]


def calculate_drop_shadow(size, blur):
    c = Image.new('RGBA', (blur, blur))

    # -----------------------------------------------------------------------------------------------------------------
    # c2 = c.load()
    # m = blur
    # m2 = (blur ** 2 + blur ** 2) ** 0.5
    # factor = 255 / m
    # for i in range(blur):
    #     for j in range(blur):
    #         j = blur - j - 1
    #         distance = m - (i ** 2 + j ** 2) ** 0.5
    #         if distance != 0:
    #             distance = m2 / distance * m2
    #         distance *= distance
    #         c2[i, blur - j - 1] = (0, 0, 0, round(distance * factor))
    # -----------------------------------------------------------------------------------------------------------------
    # c.putpixel((0, blur - 1), (0, 0, 0))
    # c = c.filter(ImageFilter.GaussianBlur(blur // 2))
    # -----------------------------------------------------------------------------------------------------------------
    c = drop_shadow_high_res.resize((blur, blur))
    # -----------------------------------------------------------------------------------------------------------------
    # c.save('0000AAATESTIMAGE3.png')

    sc = c.crop((0, 0, 1, blur))
    s1 = sc.resize((size[0], blur), 1)
    s2 = sc.resize((size[1], blur), 1)
    # s2.save('0000AAATESTIMAGE1.png')

    f = Image.new('RGBA', (size[0] + blur * 2, size[1] + blur * 2))
    f.paste(s1, (blur, 0))
    f.paste(s2.rotate(-90, expand=True), (size[0] + blur, blur))
    f.paste(s1.rotate(180), (blur, size[1] + blur))
    f.paste(s2.rotate(90, expand=True), (0, blur))

    f.paste(c, (size[0] + blur, 0))
    f.paste(c.rotate(90), (0, 0))
    f.paste(c.rotate(270), (size[0] + blur, size[1] + blur))
    f.paste(c.rotate(180), (0, size[1] + blur))
    # f.show()
    # f.save('0000AAATESTIMAGE2.png')

    return f


# calculate_drop_shadow((200, 200), 50)
# raise Exception


class Sprite:
    def __init__(self, img, x, y, scale=1, drop_shadow=0):
        self.img = image_stuff(img, scale)
        self.x = x
        self.y = y
        self.old_rect = 0, 0, 0, 0
        self.dim = self.img.get_size()
        self.width = self.dim[0]
        self.height = self.dim[1]
        self.scale = scale
        self.drop_shadow = drop_shadow

        self._update_area = True

    def _draw(self, game):
        if not isinstance(self.img, pygame.Surface):
            self.img = image_stuff(self.img)
            self.dim = self.img.get_size()
            self.width, self.height = self.dim[0], self.dim[1]
            self._update_area = True

        # Blit the image, calculate a rectangle around it to update, merge it with the older rectangle (to erase the previous frame),
        # update that region, make the current rectangle the old rectangle (for the next frame)
        if self.drop_shadow != 0:
            # ds = Image.new('RGBA', (self.dim[0] + self.drop_shadow * 4, self.dim[1] + self.drop_shadow * 4))
            # draw = ImageDraw.Draw(ds)
            # draw.rectangle((self.drop_shadow * 2, self.drop_shadow * 2, self.dim[0] + self.drop_shadow * 2, self.dim[1] + self.drop_shadow * 2), (0, 0, 0))
            # ds = ds.filter(ImageFilter.GaussianBlur(self.drop_shadow))
            ds = calculate_drop_shadow((self.width, self.height), self.drop_shadow)
            game.blit_image(image_stuff(ds), self.x - self.drop_shadow, self.y - self.drop_shadow, self.height)
            # screen.blit(image_stuff(ds), (self.x - self.drop_shadow, ny(self.y + self.height + self.drop_shadow)))

        game.blit_image(self.img, self.x, self.y, self.height)
        # screen.blit(self.img, (self.x, ny(self.y + self.height)))
        # else:
        #     pass
        # rect = pygame.Rect(self.x - self.drop_shadow, ny(self.y) - self.height - self.drop_shadow, self.width + self.drop_shadow * 2, self.height + self.drop_shadow * 2)
        # if update:
        #     pygame.display.update(pygame.Rect.union(rect, self.old_rect))
        # self.old_rect = rect

    def _update(self, game, erase=False):
        if self._update_area or erase:
            game.update_screen(self.x, self.y, self.width, self.height, self.old_rect)
            self.old_rect = self.x, self.y, self.width, self.height
            self._update_area = False


def do_nothing(*idk):
    pass


class Text:
    def __init__(self, text, font, size, color, x, y, align='bottom left'):
        self.text = text
        self.font = font
        self.font2 = pygame.freetype.Font(font, size)
        self.font_surf, self.rect = self.font2.render(text, color, size=size)
        self.dim = self.rect.width, self.rect.height
        self.width, self.height = self.dim[0], self.dim[1]
        self.size = size
        self.color = color
        self.x, self.y = x, y
        self.align = align
        self.old_rect = 0, 0, 0, 0
        self.old_text = None
        self.x_offset = 0
        self.y_offset = 0

    def _draw(self, game):
        if self.text != self.old_text:
            self.font2 = pygame.freetype.Font(self.font, self.size)
            self.font_surf, self.rect = self.font2.render(str(self.text), self.color, size=self.size)
            self.font_surf = self.font_surf.convert_alpha()
            self.dim = self.font_surf.get_size()
            self.width, self.height = self.dim[0], self.dim[1]

        if self.align == 'top left':
            self.x_offset = -self.width
            self.y_offset = 0
        elif self.align == 'top':
            self.x_offset = -self.width // 2
        elif self.align == 'top right':
            self.x_offset = 0
            self.y_offset = 0
        elif self.align == 'left':
            self.x_offset = -self.width
            self.y_offset = -self.height // 2
        elif self.align == 'center':
            self.x_offset = -self.width // 2
            self.y_offset = -self.height // 2
        elif self.align == 'right':
            self.x_offset = 0
            self.y_offset = -self.height // 2
        elif self.align == 'bottom left':
            self.x_offset = -self.width
            self.y_offset = -self.height
        elif self.align == 'bottom':
            self.x_offset = -self.width // 2
            self.y_offset = self.height
        elif self.align == 'bottom right':
            self.x_offset = 0
            self.y_offset = self.height
        else:
            raise Exception(f'Alignments can be "left", "center", or "right", but {self.align} given')

        game.blit_image(self.font_surf, self.x + self.x_offset, self.y + self.y_offset, self.height)

    def _update(self, game, erase=False):
        if self.text != self.old_text or erase:
            current_rect = self.x + self.x_offset, self.y + self.y_offset, self.width, self.height
            game.update_screen(current_rect, self.old_rect)
            self.old_rect = current_rect
            self.old_text = self.text


class Game:
    def __init__(self, resolution, fps, fullscreen=False, title='Untitled Game', icon=None, frame=True, hardware_acceleration=True):
        self.current_scene = None
        self.run = True
        self.default_resolution = resolution
        self._resolution = self.default_resolution
        self.framerate = fps
        self.fullscreen = fullscreen
        self.title = title
        self._title = title
        self.frame = frame
        self.hardware_acceleration = hardware_acceleration

        self.os = system().lower()
        if self.os == 'darwin':
            self.os = 'macos'

        self.input_downs = []
        self.input_ups = []
        self.currently_pressed = []
        self.mouse_position = (0, 0)
        self.quit_letters = 'q', 'u', 'i', 't'
        self.quit_progress = 0

        self.delta = 0
        self._previous_frame_total_ticks = 0

        self.file_paths = None

        self._update_screen_in = 0

        pygame.init()
        if self.fullscreen:
            if frame:
                if self.hardware_acceleration:
                    self.screen = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN, pygame.HWSURFACE)
                else:
                    self.screen = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN)
            else:
                if self.hardware_acceleration:
                    self.screen = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN, pygame.NOFRAME, pygame.HWSURFACE)
                else:
                    self.screen = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN, pygame.NOFRAME)
        else:
            if frame:
                if self.hardware_acceleration:
                    self.screen = pygame.display.set_mode(self._resolution, pygame.HWSURFACE)
                else:
                    self.screen = pygame.display.set_mode(self._resolution)
            else:
                if self.hardware_acceleration:
                    self.screen = pygame.display.set_mode(self._resolution, pygame.NOFRAME, pygame.HWSURFACE)
                else:
                    self.screen = pygame.display.set_mode(self._resolution, pygame.NOFRAME)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(title)
        if icon is not None:
            pygame.display.set_icon(pygame.image.load(icon))
        self.display_resolution = self.screen.get_size()

    def ny(self, y):
        return self._resolution[1] - y

    def update_screen(self, x=None, y=None, width=None, height=None, old_rect=None):
        if type(x) == tuple:
            y, width, height = x[1], x[2], x[3]
            x = x[0]

        if x is None and y is None and width is None and height is None and old_rect is None:
            pygame.display.flip()
        else:
            if old_rect is not None:
                # pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect.union(pygame.Rect(x, self._resolution[1] - y - height, width, height), pygame.Rect(old_rect[0], self._resolution[1] - old_rect[1] - old_rect[3], old_rect[2], old_rect[3])))
                pygame.display.update(pygame.Rect.union(pygame.Rect(x, self._resolution[1] - y - height, width, height), pygame.Rect(old_rect[0], self._resolution[1] - old_rect[1] - old_rect[3], old_rect[2], old_rect[3])))
            else:
                pygame.display.update(pygame.Rect(x, self._resolution[1] - y - height, width, height))

        # pygame.display.update()

    def blit_image(self, image, x, y, height):
        self.screen.blit(image, (x, self._resolution[1] - y - height))

    def get_color_at_pixel(self, x, y):
        return self.screen.get_at((x, self._resolution[1] - y))[:3]

    def change_resolution(self, to):
        self._resolution = to
        if self.fullscreen:
            if self.frame:
                self.screen = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN, pygame.HWSURFACE)
            else:
                self.screen = pygame.display.set_mode(self._resolution, pygame.FULLSCREEN, pygame.NOFRAME, pygame.HWSURFACE)
        else:
            if self.frame:
                self.screen = pygame.display.set_mode(self._resolution, pygame.HWSURFACE)
            else:
                self.screen = pygame.display.set_mode(self._resolution, pygame.NOFRAME, pygame.HWSURFACE)

        self._update_screen_in = 0.2

    def run_game(self):
        self.run = True
        # if self.current_scene is None:
        #     self.current_scene = self.sce

        mouse = pygame.mouse
        while self.run:
            self.clock.tick(self.framerate)
            t = pygame.time.get_ticks()
            self.input_ups.clear()
            self.input_downs.clear()
            self.file_paths = None

            if self.title != self._title:
                pygame.display.set_caption(self.title)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

                if event.type == pygame.DROPFILE:
                    self.file_paths = str(event.file)

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
                    self.mouse_position = (position[0], self._resolution[1] - position[1])
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

            if self._update_screen_in > 0 and self._update_screen_in - self.delta <= 0:
                self.update_screen()
            if self._update_screen_in > 0:
                self._update_screen_in -= self.delta
                if self._update_screen_in < 0:
                    self._update_screen_in = 0

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

    def constrict_to_screen(self, value, constricted_to, width=0, height=0, scale=False):
        def constrict(valueidk, plus, axis=0):
            if valueidk < 0:
                if not scale:
                    return 0
                else:
                    return 0, plus + valueidk
            elif valueidk + plus > self._resolution[axis]:
                if not scale:
                    return self._resolution[axis] - plus
                else:
                    return valueidk, plus - ((valueidk + plus) - (self._resolution[axis]))
            if not scale:
                return valueidk
            else:
                return valueidk, plus

        if constricted_to == 'x':
            if type(value) == int or type(value) == float:
                return constrict(value, width)
            return constrict(value.x, value.width)
        elif constricted_to == 'y':
            if type(value) == int or type(value) == float:
                return constrict(value, width, 1)
            return constrict(value.x, value.height, 1)

        if type(value) == int or type(value) == float:
            return constrict(value, width), constrict(constricted_to, height, 1)
        return constrict(value.x, value.width), constrict(constricted_to.x, constricted_to.height, 1)

    class Scene:
        def __init__(self, game):
            self.game = game
            self.stuff = []
            self.update_func = do_nothing
            self.resolution = game.default_resolution
            self.background = 0, 0, 0
            self._old_background = self.background
            self._background_center = 0, 0
            self.redraw = False

            self.animations = []
            self.animation_calls = 0

        def clear(self):
            self.stuff = []

        def __contains__(self, item):
            if item in self.stuff:
                return True
            return False

        def set_background(self, background, _update=True):
            if type(background) == pygame.Surface:
                self.background = background
                self.game.screen.blit(self.background, self._background_center)
            elif type(background) == tuple:
                self.background = background
                self.game.screen.fill(self.background)
            else:
                self.background, self._background_center = image_stuff(background, self.game._resolution)
                self.game.screen.blit(self.background, self._background_center)

        def animate(self, start, stop, seconds=1):
            if len(self.animations) == 0 or self.animations[self.animation_calls][0] != (start, stop, seconds):
                self.animations.append([(start, stop, seconds), seconds, seconds / (stop - start), start, True])

            # (ID)     time_left     next_milestone     to_return_on_next_milestone     active
            #  0           1               2                        3                     4

            corresponding = self.animations[self.animation_calls]
            if corresponding[3] > stop:
                self.animations[self.animation_calls][4] = False
            if corresponding[4]:
                self.animations[self.animation_calls][1] -= self.game.delta
                to_return = None
                if corresponding[1] <= seconds - corresponding[2]:
                    to_return = corresponding[3]
                    self.animations[self.animation_calls][3] += 1
                    self.animations[self.animation_calls][2] += seconds / (stop - start)

                self.animation_calls += 1
                if to_return is not None:
                    return to_return

        def run_scene(self):
            if self.resolution != self.game._resolution:
                self.game.change_resolution(self.resolution)

            self.set_background(self.background)
            if self.background != self._old_background:
                self._old_background = self.background
                self.redraw = True

            self.animation_calls = 0
            self.update_func(self.game.delta)

            for i in self.stuff:
                i._draw(self.game)
            if self.redraw:
                self.game.update_screen()
                self.redraw = False
            else:
                for i in self.stuff:
                    i._update(self.game)

        def game_update(self, func):
            self.update_func = func

        def add(self, *objects, position=-1):
            if type(objects[0]) == tuple or type(objects[0]) == list:
                for i in objects[0]:
                    self.stuff.append(i)
            else:
                for i in objects:
                    self.stuff.insert(position, i)

        def remove(self, *objects):
            for i in objects:
                self.stuff.remove(i)
                i._update(self.game, True)

        def update_obj(self, obj):
            obj.update()
            obj.draw(self.game.screen, self.game.res)

        def key_bind(self, key, value, value2, negative, key_down_list, key_up_list):
            if key in key_down_list:
                value += value2 if negative else -value2
            elif key in key_up_list:
                value -= value2 if negative else -value2
            return value

        def dist(self, obj_1, obj_2):
            if (type(obj_1) == int or type(obj_1) == float) and (type(obj_2) == int or type(obj_2) == float):
                return abs(obj_2 - obj_1)

            x1 = obj_1[0] if type(obj_1) == tuple else obj_1.x
            y1 = obj_1[1] if type(obj_1) == tuple else obj_1.y
            x2 = obj_2[0] if type(obj_2) == tuple else obj_2.x
            y2 = obj_2[1] if type(obj_2) == tuple else obj_2.y

            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        def square_distance(self, object_1, object_2, radius):
            if object_1[0] - radius <= object_2[0] <= object_1[0] + radius and object_1[1] - radius <= object_2[1] <= object_1[1] + radius:
                return True
            return False
