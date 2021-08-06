from PyBookEngine import *
from PIL import Image, ImageFilter
from pathlib import Path
from sys import exit

maximum_resolution = 1820, 980
background_blur_amount = 2
background_reduced_brightness_multiplier = 2
background_blur_animation = False
background_blur_animation_length = 5
background_blur_animation_frames_per_second = 20
image_drop_shadow_size = 40
save_file_path = f'{str(Path.home())}/Downloads/\name-cropped.png'

g = Game(maximum_resolution, 60, False, 'Image Cropping Tool')
s = g.Scene(g)

g.screen.fill((20, 22, 27))
info_text = Text('Drag an image file into this window', 'Roboto-Medium.ttf', 30, (255, 255, 255, 150), maximum_resolution[0] // 2 - 230, maximum_resolution[1] // 2 - 15)
info_text._draw(g, s, g.screen, maximum_resolution)
pygame.display.flip()
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.DROPFILE:
            g.file_paths = str(event.file)
            print(g.file_paths)
            im_path = g.file_paths
            im = Image.open(g.file_paths)
            im2 = im.resize(fit_image(im.size, maximum_resolution))
            scaling = fit_image(im.size, maximum_resolution)[0] / im.size[0]
            resx, resy = im2.size

            pygame.display.set_mode((resx, resy))
            g.res = resx, resy
            g.current_scene = s
            run = False

first_time = True

final_image = Sprite(im2, 0, 0, drop_shadow=image_drop_shadow_size)
s.add(final_image)

selection_start = 0, 0

points = []


def lower_brightness(image, amount):
    source = image.split()
    r = source[0].point(lambda i: i / amount)
    g = source[1].point(lambda i: i / amount)
    b = source[2].point(lambda i: i / amount)
    return Image.merge('RGB', (r, g, b))


def crop_normal_image(x=None, y=None, w=None, h=None):
    global final_image
    global crop_x
    global crop_y
    global crop_w
    global crop_h

    if x is None:
        x = final_image.x
    if y is None:
        y = final_image.y
    if w is None:
        w = final_image.width
    if h is None:
        h = final_image.height

    if w < 0:
        w *= -1
        x -= w
    if h < 0:
        h *= -1
        y -= h

    if w != 0 and h != 0:
        im3 = im2.crop((x, resy - y - h, x + w, resy - y))
        final_image.img = im3
        final_image.x = x
        final_image.y = y

        crop_x = x // scaling
        crop_y = y // scaling
        crop_w = w // scaling
        crop_h = h // scaling


if background_blur_animation:
    blur_step_images = [lower_brightness(im2, background_reduced_brightness_multiplier * (20 / background_blur_animation_frames_per_second) * amount / 10 / background_blur_animation_length + 1)
                            .filter(ImageFilter.GaussianBlur(round(background_blur_amount * (maximum_resolution[0] * maximum_resolution[1] / 3000000) * amount * (20 / background_blur_animation_frames_per_second) / background_blur_animation_length)))
                        for amount in range(1, round(background_blur_animation_frames_per_second * background_blur_animation_length) + 1)]

move_distance_start = 0, 0
move_distance_x = 0
move_distance_y = 0
move_distance_width = 0
move_distance_height = 0

crop_x = 0
crop_y = 0
crop_w = 0
crop_h = 0

moving = -1

t = Text('', 'Roboto-Regular.ttf', 15, (255, 255, 255), resx - 100, 5)
s.add(t)


@s.game_update
def game_update(delta):
    global first_time
    global selection_start
    global points
    global move_distance_start
    global move_distance_x
    global move_distance_y
    global move_distance_width
    global move_distance_height
    global moving
    global move_snap

    if g.just_pressed('left') and first_time:
        if not background_blur_animation:
            amount = round(background_blur_animation_frames_per_second * background_blur_animation_length)
            s.set_background(lower_brightness(im2, background_reduced_brightness_multiplier * (20 / background_blur_animation_frames_per_second) * amount / 10 / background_blur_animation_length + 1)
                             .filter(ImageFilter.GaussianBlur(round(background_blur_amount * (maximum_resolution[0] * maximum_resolution[1] / 3000000) * amount * (20 / background_blur_animation_frames_per_second) / background_blur_animation_length))))
        selection_start = g.mouse_position
    if g.is_pressed('left') and (first_time or first_time == -1):
        first_time = -1

        if background_blur_animation:
            if g_amount := s.animate(0, round(background_blur_animation_frames_per_second * background_blur_animation_length) - 1, background_blur_animation_length):
                s.set_background(blur_step_images[g_amount])

        precise = 1
        snap = 1
        reflect = False

        if g.is_pressed('left shift'):
            precise = 0.5
        if g.is_pressed('left ctrl'):
            snap = 10
        if g.is_pressed('left alt'):
            reflect = True

        distance_x = round((g.mouse_position[0] - selection_start[0]) * precise / snap) * snap
        distance_y = round((g.mouse_position[1] - selection_start[1]) * precise / snap) * snap
        if not reflect:
            crop_normal_image(selection_start[0], selection_start[1], distance_x, distance_y)
        else:
            crop_normal_image(selection_start[0] - distance_x, selection_start[1] - distance_y, distance_x * 2, distance_y * 2)

        t.text = f'{final_image.width}, {final_image.height}'

    elif first_time == -1:
        first_time = False
        points = [(selection_start[0], selection_start[1])]
        t.text = ''

    if not first_time:
        if g.just_pressed('return'):
            name = im_path.split('/')[-1].split('.')[0]
            im.crop((crop_x, resy - crop_y - crop_h, crop_x + crop_w, resy - crop_y)).save(save_file_path.replace('\name', name))

        if g.just_pressed('left') == 1:
            do_stuff = True
            if s.dist(g.mouse_position, (final_image.x, final_image.y)) <= 60:
                moving = 1  # Bottom-left
            elif s.dist(g.mouse_position, (final_image.x + final_image.width, final_image.y)) <= 60:
                moving = 3  # Bottom-right
            elif s.dist(g.mouse_position, (final_image.x, final_image.y + final_image.height)) <= 60:
                moving = 6  # Top-left
            elif s.dist(g.mouse_position, (final_image.x + final_image.width, final_image.y + final_image.height)) <= 60:
                moving = 8  # Top-right
            elif (final_image.x <= g.mouse_position[0] <= final_image.x + final_image.width) and s.dist(g.mouse_position[1], final_image.y) <= 60:
                moving = 2  # Bottom
            elif s.dist(g.mouse_position[0], final_image.x) <= 60 and (final_image.y <= g.mouse_position[1] <= final_image.y + final_image.height):
                moving = 4  # Left
            elif s.dist(g.mouse_position[0], final_image.x + final_image.width) <= 60 and (final_image.y <= g.mouse_position[1] <= final_image.y + final_image.height):
                moving = 5  # Right
            elif (final_image.x <= g.mouse_position[0] <= final_image.x + final_image.width) and s.dist(g.mouse_position[1], final_image.y + final_image.height) <= 60:
                moving = 7  # Top
            elif (final_image.x <= g.mouse_position[0] <= final_image.x + final_image.width) and (final_image.y <= g.mouse_position[1] <= final_image.y + final_image.height):
                moving = 9  # Area
            else:
                do_stuff = False

            if do_stuff:
                move_distance_start = g.mouse_position
                move_distance_x = final_image.x
                move_distance_y = final_image.y
                move_distance_width = final_image.dim[0]
                move_distance_height = final_image.dim[1]

        elif g.just_pressed('left') == -1:
            moving = False

        if g.is_pressed('left'):
            if moving:
                distance_x = g.mouse_position[0] - move_distance_start[0]
                distance_y = g.mouse_position[1] - move_distance_start[1]

                show_dimensions = True
                move_distance_x2 = move_distance_x
                move_distance_y2 = move_distance_y

                if g.is_pressed('left shift'):
                    distance_x = distance_x // 2
                    distance_y = distance_y // 2
                if g.is_pressed('left ctrl'):
                    distance_x = round(distance_x / 10) * 10 + (10 - int(str(move_distance_width)[-1]))
                    distance_y = round(distance_y / 10) * 10 + (10 - int(str(move_distance_height)[-1]))
                if g.is_pressed('left alt'):
                    move_distance_x2 -= distance_x
                    move_distance_y2 -= distance_y
                    distance_x *= 2
                    distance_y *= 2

                if moving == 1:  # Bottom-left
                    crop_normal_image(move_distance_x2 + distance_x, move_distance_y2 + distance_y, move_distance_width - distance_x, move_distance_height - distance_y)
                elif moving == 2:  # Bottom
                    crop_normal_image(move_distance_x, move_distance_y2 + distance_y, move_distance_width, move_distance_height - distance_y)
                elif moving == 3:  # Bottom-right
                    crop_normal_image(move_distance_x2, move_distance_y2 + distance_y, move_distance_width + distance_x, move_distance_height - distance_y)
                elif moving == 4:  # Left
                    crop_normal_image(move_distance_x2 + distance_x, move_distance_y, move_distance_width - distance_x, move_distance_height)
                elif moving == 5:  # Right
                    crop_normal_image(move_distance_x2, move_distance_y, move_distance_width + distance_x, move_distance_height)
                elif moving == 6:  # Top-left
                    crop_normal_image(move_distance_x2 + distance_x, move_distance_width, move_distance_width - distance_x, move_distance_height + distance_y)
                elif moving == 7:  # Top
                    crop_normal_image(move_distance_x, move_distance_y2, move_distance_width, move_distance_height + distance_y)
                elif moving == 8:  # Top-right
                    crop_normal_image(move_distance_x2, move_distance_y2, move_distance_width + distance_x, move_distance_height + distance_y)
                elif moving == 9:  # Area
                    crop_normal_image(g.constrict_to_screen(move_distance_x2 + distance_x, 'x', move_distance_width), g.constrict_to_screen(move_distance_y2 + distance_y, 'y', move_distance_height))
                    show_dimensions = False

                if show_dimensions:
                    t.text = f'{final_image.width}, {final_image.height}'
        else:
            t.text = ''


g.run_game()
