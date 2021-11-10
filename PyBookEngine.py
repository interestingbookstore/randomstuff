import pygame
import pygame.freetype
from PIL import Image, ImageFilter, ImageDraw, ImageDraw, ImageFont
from platform import system
import copy



# Made by interestingbookstore
# Github: https://github.com/interestingbookstore/randomstuff
# -----------------------------------------------------------------------
# Version released on October 11 2021
# ---------------------------------------------------------



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


def separate_sprite_sheet(image, h_images, v_images=None):
    if type(image) == str:
        im = Image.open(image)
    elif isinstance(image, Image.Image):
        im = image
    else:
        raise TypeError(f'Sprite sheet image expected to be either path or Pillow image, got "{type(image)}"')
    if v_images is None:
        if not (h_images ** 0.5).is_integer():
            raise Exception(f'{h_images} is not a perfect square, and as such, cannot be used to unpack the sprite sheet')
        h_images, v_images = int(h_images ** 0.5), int(h_images ** 0.5)

    xf = im.size[0] / h_images
    yf = im.size[1] / v_images
    if (not xf.is_integer()) and (not yf.is_integer()):
        raise Exception(f"Sprite sheet image given has a resolution of {im.size[0]} by {im.size[1]}, which isn't horizontally\ndividable by {h_images}, nor vertically dividable by {v_images}")
    if not xf.is_integer():
        raise Exception(f"Sprite sheet image given has a resolution of {im.size[0]} by {im.size[1]}, which isn't horizontally dividable by {h_images}")
    if not yf.is_integer():
        raise Exception(f"Sprite sheet image given has a resolution of {im.size[0]} by {im.size[1]}, which isn't vertically dividable by {v_images}")

    images = []
    for y in range(h_images):
        for x in range(v_images):
            images.append(im.crop((x * xf, y * yf, x * xf + xf, y * yf + yf)))
    return tuple(images)


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
    def __init__(self, img, x, y, scale=1, drop_shadow=0, origin='bl'):
        self.rect_expansion_amount = 0

        self.img = img
        self._old_img = copy.copy(self.img)
        self._img_surface = image_stuff(img, scale)
        self.x = x
        self.y = y
        self.velocity = 0, 0
        self.current_speed = 0
        self._dim = self._img_surface.get_size()
        self._width = self._dim[0]
        self._height = self._dim[1]
        self.origin = origin
        if self.origin == 'bl':
            self._rect = self.x - self.rect_expansion_amount, self.y - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
        elif self.origin == 'm':
            self._rect = self.x - self._width // 2 - self.rect_expansion_amount, self.y - self._height // 2 - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
        self._old_rect = 0, 0, 0, 0
        self.scale = scale
        self._old_scale = scale
        self.drop_shadow = drop_shadow

        self._update_area = True

    def _update_area_check(self, game):
        self.current_speed = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity = 0, 0

        if self.origin == 'bl':
            self._rect = self.x - self.rect_expansion_amount, self.y - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
        elif self.origin == 'm':
            self._rect = self.x - self._width // 2 - self.rect_expansion_amount, self.y - self._height // 2 - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
        if self.img != self._old_img or self.scale != self._old_scale:
            self._img_surface = image_stuff(self.img, self.scale)
            self._dim = self._img_surface.get_size()
            self._width, self._height = self._dim[0], self._dim[1]
            self._update_area = True
            self._old_img = copy.copy(self.img)
            if self.origin == 'bl':
                self._rect = self.x - self.rect_expansion_amount, self.y - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
            elif self.origin == 'm':
                self._rect = self.x - self._width // 2 - self.rect_expansion_amount, self.y - self._height // 2 - self.rect_expansion_amount, self._width + self.rect_expansion_amount, self._height + self.rect_expansion_amount
            self._old_scale = self.scale
        elif self._rect != self._old_rect:
            self._update_area = True

    def _draw(self, game):
        if self.drop_shadow != 0:
            ds = calculate_drop_shadow((self._width, self._height), self.drop_shadow)
            game.blit_image(image_stuff(ds), self._rect[0] - self.drop_shadow, self._rect[1] - self.drop_shadow)

        game.blit_image(self._img_surface, self._rect[0], self._rect[1])

    def _update(self, game, erase=False):
        if self._update_area or erase:
            game.update_screen(self._rect[0], self._rect[1], self._rect[2], self._rect[3], self._old_rect)
            self._old_rect = self._rect
            self._update_area = False

    def print_info(self, sprite_object=True, img=True, x=True, y=True, scale=True, drop_shadow=True, origin=True, update=True):
        string = ''
        if sprite_object:
            string += f'SPRITE object'
        if img:
            string += f'  img: {self.img}'
        if x:
            string += f'  x: {self.x}'
        if y:
            string += f'  y: {self.y}'
        if scale:
            string += f'  scale: {self.scale}'
        if drop_shadow:
            string += f'  drop_shadow: {self.drop_shadow}'
        if origin:
            string += f'  origin: {self.origin}'
        if update:
            f'  updating_this_frame: {self._update_area}'
        return string

    def __repr__(self):
        return f'SPRITE object  img: {self.img}  x: {self.x}  y: {self.y}  scale: {self.scale}  drop_shadow: {self.drop_shadow}  origin: {self.origin}  updating this frame: {self._update_area}'


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

        game.blit_image(self.font_surf, self.x + self.x_offset, self.y + self.y_offset)

    def _update(self, game, erase=False):
        if self.text != self.old_text or erase:
            current_rect = self.x + self.x_offset, self.y + self.y_offset, self.width, self.height
            game.update_screen(current_rect, self.old_rect)
            self.old_rect = current_rect
            self.old_text = self.text


class Game:
    def __init__(self, resolution, fps, title='Untitled Game', icon=None, frame=True, scale=1):
        self.current_scene = None
        self._old_scene = self.current_scene
        self._run = True
        self.default_resolution = resolution
        self._resolution = self.default_resolution
        self.framerate = fps
        self.title = title
        self._title = title
        self.frame = frame
        self.scale = scale

        self.os = system().lower()
        if self.os == 'darwin':
            self.os = 'macos'

        self.input_downs = []
        self.input_ups = []
        self.currently_pressed = []
        self.mouse_position = 0, 0
        self.quit_letters = 'q', 'u', 'i', 't'
        self.quit_progress = 0

        self.delta = 0
        self._previous_frame_total_ticks = 0

        self.file_paths = None

        self._update_screen_in = 0

        pygame.init()
        if self.default_resolution == (pygame.display.Info().current_w, pygame.display.Info().current_h):
            self.frame = False
        if self.frame:
            self.screen = pygame.display.set_mode(self._resolution)
        else:
            self.screen = pygame.display.set_mode(self._resolution, pygame.NOFRAME)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption(title)
        if icon is not None:
            pygame.display.set_icon(pygame.image.load(icon))
        self.display_resolution = self.screen.get_size()

    def ny(self, y):
        return self._resolution[1] - y

    def generate_rect(self, x, y=None, width=None, height=None):
        if type(x) == tuple:
            y, width, height = x[1], x[2], x[3]
            x = x[0]
        x *= self.scale
        y *= self.scale
        width *= self.scale
        height *= self.scale
        return pygame.Rect(x, self._resolution[1] - y - height, width, height)

    def update_screen(self, x=None, y=None, width=None, height=None, old_rect=None):
        if type(x) == tuple:
            y, width, height = x[1], x[2], x[3]
            x = x[0]

        if x is None and y is None and width is None and height is None and old_rect is None:
            pygame.display.flip()
        else:
            x *= self.scale
            y *= self.scale
            width *= self.scale
            height *= self.scale

            if old_rect is not None:
                ox = old_rect[0] * self.scale
                oy = old_rect[1] * self.scale
                owidth = old_rect[2] * self.scale
                oheight = old_rect[3] * self.scale

                # pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(x, self._resolution[1] - y - height, width, height))
                # pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(ox, self._resolution[1] - oy - oheight, owidth, oheight))

                # pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect.union(pygame.Rect(x, self._resolution[1] - y - height, width, height), pygame.Rect(old_rect[0], self._resolution[1] - old_rect[1] - old_rect[3], old_rect[2], old_rect[3])))
                pygame.display.update(pygame.Rect.union(pygame.Rect(x, self._resolution[1] - y - height, width, height), pygame.Rect(ox, self._resolution[1] - oy - oheight, owidth, oheight)))
            else:
                pygame.display.update(pygame.Rect(x, self._resolution[1] - y - height, width, height))

        # pygame.display.update()

    def blit_image(self, image, x, y):
        x *= self.scale
        y *= self.scale
        res = round(image.get_width() * self.scale), round(image.get_height() * self.scale)
        self.screen.blit(pygame.transform.smoothscale(image, res), (x, self._resolution[1] - y - res[1]))

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
        self._run = True
        # if self.current_scene is None:
        #     self.current_scene = self.sce

        mouse = pygame.mouse
        while self._run:
            self.clock.tick(self.framerate)
            t = pygame.time.get_ticks()
            self.input_ups.clear()
            self.input_downs.clear()
            self.file_paths = None

            if self.title != self._title:
                pygame.display.set_caption(self.title)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._run = False

                if event.type == pygame.DROPFILE:
                    self.file_paths = str(event.file)

                if event.type == pygame.KEYDOWN:
                    self.input_downs.append(pygame.key.name(event.key))
                    if pygame.key.name(event.key) == self.quit_letters[self.quit_progress]:
                        self.quit_progress += 1
                        if self.quit_progress == len(self.quit_letters):
                            self._run = False
                    else:
                        self.quit_progress = 0
                if event.type == pygame.KEYUP:
                    self.input_ups.append(pygame.key.name(event.key))

                if event.type == pygame.MOUSEMOTION:
                    position = mouse.get_pos()
                    self.mouse_position = position[0] // self.scale, (self._resolution[1] - position[1]) // self.scale
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
            if self.current_scene != self._old_scene:
                self.current_scene.redraw = True
                self._old_scene = self.current_scene
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

    def get_action_strength(self, button):
        if button in self.currently_pressed:
            return 1
        return 0

    def quit(self):
        self._run = False

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
                i._update_area_check(self.game)

            draw_all = False

            for i in self.stuff:
                if i._update_area:
                    draw_all = True
                    break

            if draw_all or self.redraw:
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
                    self.stuff.append(i)
                    # self.stuff.insert(position, i)  # ??? An item was inserted in the second to last slot, and not the last slot???

        def remove(self, *objects):
            for i in objects:
                self.stuff.remove(i)
                self.redraw = True

        def key_bind(self, key, value, value2, negative, key_down_list, key_up_list):
            if key in key_down_list:
                value += value2 if negative else -value2
            elif key in key_up_list:
                value -= value2 if negative else -value2
            return value


def distance(obj_1, obj_2):
    if (type(obj_1) == int or type(obj_1) == float) and (type(obj_2) == int or type(obj_2) == float):
        return abs(obj_2 - obj_1)

    x1 = obj_1[0] if type(obj_1) == tuple else (obj_1.x + obj_1._width // 2 if obj_1.origin == 'bl' else obj_1.x)
    y1 = obj_1[1] if type(obj_1) == tuple else (obj_1.y + obj_1._height // 2 if obj_1.origin == 'bl' else obj_1.y)
    x2 = obj_2[0] if type(obj_2) == tuple else (obj_2.x + obj_2._width // 2 if obj_2.origin == 'bl' else obj_2.x)
    y2 = obj_2[1] if type(obj_2) == tuple else (obj_2.y + obj_2._height // 2 if obj_2.origin == 'bl' else obj_2.y)

    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def square_distance(object_1, object_2, radius):
    if object_1[0] - radius <= object_2[0] <= object_1[0] + radius and object_1[1] - radius <= object_2[1] <= object_1[1] + radius:
        return True
    return False


def move_toward(val1, to, amount_at_a_time, velocity=False):
    # Takes one value, moves it closer by AMOUNT_AT_A_TIME until it's TO.
    # To clarify, if TO is farther away from VAL1, it'll take that much longer to get there.

    new_val = val1

    if type(val1) == int and type(to) == int:
        if to > new_val:
            new_val += amount_at_a_time
            if new_val > to:
                new_val = to
        else:
            new_val -= amount_at_a_time
            if new_val < to:
                new_val = to
        dist = normalize(new_val - val1)
        if velocity:
            return dist
        return new_val
    elif type(val1) == tuple and type(to) == tuple:
        vector = to[0] - val1[0], to[1] - val1[1]
        dist = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
        vector = normalize(vector)


        if amount_at_a_time > dist:
            amount_at_a_time = dist

        vector = vector[0] * amount_at_a_time, vector[1] * amount_at_a_time

        if velocity:
            return vector
        return val1[0] + vector[0], val1[1] + vector[1]

    else:
        raise TypeError(f'The lerp function accepts two integers or two tuples, but a {type(val1)} and a {type(to)} were given.')


def normalize(vector):
    distance2 = (vector[0] ** 2 + vector[1] ** 2) ** 0.5

    if distance2 == 0:
        return vector

    return vector[0] / distance2, vector[1] / distance2
