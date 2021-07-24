from PygameFuncLibrary import *
from FontOrganizer import *
import time
from PIL import Image, ImageFilter, ImageEnhance

resolution = 2100, 880

im = Image.open('Bill frame full.png')
im2 = im.resize(fit_image(im.size, resolution))

im_blur = ImageEnhance.Brightness(im2).enhance(0.2)
im_blur = im_blur.filter(ImageFilter.GaussianBlur(20))

resx, resy = im2.size

g = Game((resx, resy), 60, False, 'Crop Image Tool')
s = g.Scene(g)
g.current_scene = s
s.set_background(im_blur)

first_time = True

g_im = Sprite(im2, 0, 0)
s.add(g_im)

selection_start = 0, 0


@s.game_update
def game_update():
    global first_time
    global selection_start

    if g.just_pressed('left') == 1 and first_time:
        first_time = False
        s.set_background(im_blur)
        selection_start = g.mouse_position
    if g.is_pressed('left'):
        w = g.mouse_position[0] - selection_start[0]
        h = g.mouse_position[1] - selection_start[1]
        x = selection_start[0]
        y = selection_start[1]
        if w < 0:
            w *= -1
            x -= w
        if h < 0:
            h *= -1
            y -= h

        if abs(w) > 0 and abs(h) > 0:
            im3 = im2.crop((x, resy - y - h, x + w, resy - y))
            # print(f'im_blur2 = im_blur.crop(({r.x}, {resy - r.y} - {h}, {r.x + w}, {resy - r.y}))')
            # g_im.img = im_blur2
            # im_blur2.show()
            g_im.update(im3)
            g_im.x = x
            g_im.y = y

        # g_im.crop = r.x, r.y, w, h


g.run_game()
