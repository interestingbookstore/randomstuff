from PyBookEngine import *
from random import shuffle, randint

res = 1920, 1080
# res = 3840, 2160
scale = res[1] / 2160
xres, yres = res
background = 37, 38, 42

g = Game(res, 60, 'MasterMind', scale=scale)

s = g.Scene(g)
s.background = background

circles = separate_sprite_sheet('mastermind_sprites.png', 4, 4)
gray, red, green, blue, orange, purple, yellow = circles[:7]
colors = red, blue, purple, green, orange, yellow
correct = separate_sprite_sheet(circles[12], 4)
semi = separate_sprite_sheet(circles[13], 4)
wrong = separate_sprite_sheet(circles[14], 4)

circle_size = 220
circle_normal_scale = circle_size / 256
circle_mini_scale = 0.7
x_circle_gap = 50
y_circle_gap = 75
y_offset = circle_size // 2 + 40
#  The default res is 3840, everything is scaled down (or up) from there.
x_offset = 3840 // 2 - round(circle_size + x_circle_gap * 1.5) - round(circle_size * 0.5)

# The whole giant 4 by 6 grid of circles to play with
grid_circles = []
for y in reversed(range(6)):
    circle_group = []
    for x in range(4):
        circle_group.append(Sprite(gray, x_offset + (circle_size + x_circle_gap) * x, y_offset + (circle_size + y_circle_gap) * y, circle_normal_scale * circle_mini_scale, origin='m'))
    grid_circles.append(circle_group)

for i in grid_circles:
    s.add(i)

# All six circles to sample in
guess_bottom_y = y_offset + (circle_size + y_circle_gap) * 5
drag_circles = []
drag_x_offset = 1300
drag_y_offset = guess_bottom_y
drag_circle_gap = 50
for x in range(2):
    for y in range(3):
        drag_circles.append(Sprite(circles[1 + x + y * 2], x_offset + drag_x_offset + x * (circle_size + drag_circle_gap), drag_y_offset + y * (-circle_size - drag_circle_gap), circle_normal_scale, origin='m'))

for i in drag_circles:
    s.add(i)


# These functions are later called to update the four current circles for the actual game and the choose answer scene respectively
def update_circles():
    global old_bar
    for index, i in enumerate(current_bar):
        if i != old_bar[index]:
            if i is None:
                grid_circles[guess][index].img = gray
                grid_circles[guess][index].scale = circle_normal_scale * circle_mini_scale
            else:
                grid_circles[guess][index].img = colors[i]
                grid_circles[guess][index].scale = circle_normal_scale
    old_bar = current_bar.copy()


def update_circles2():
    global old_bar
    for index, i in enumerate(current_bar):
        if i != old_bar[index]:
            if i is None:
                choose_circles[index].img = gray
                choose_circles[index].scale = circle_normal_scale * circle_mini_scale
            else:
                choose_circles[index].img = colors[i]
                choose_circles[index].scale = circle_normal_scale
    old_bar = current_bar.copy()


# General variables, and such
answer = 0, 0, 0, 0
tmp_circle = None

guess = 0
drag_circle_color_index = None
drag_circle_column_index = None
drop_circle_column_index = None
drag_type = None
swap_image = None

current_bar = [None, None, None, None]
old_bar = current_bar.copy()
cursor_type = 'normal'
old_cursor_type = 'normal'

responses = []

# Response circles  ------------------------------------------------------------------
response_offset = 400
response_gap = 60
circle_closer_together = 10
mini_circle_size = (circle_size - response_gap - circle_closer_together * 2) // 2
mini_circle_scaling = mini_circle_size / (circle_size / 2)

# ----  v  --------  Opening Scene  --------------------  v  --------------------------  v  ----

s2 = g.Scene(g)
g.current_scene = s2
s2.background = s.background

# The four empty spots the the player drags circles into
choose_circle_y = 1200
choose_circles = []

for x in range(4):
    choose_circles.append(Sprite(gray, x_offset + (circle_size + x_circle_gap) * x, choose_circle_y, circle_normal_scale * circle_mini_scale, origin='m'))
for i in choose_circles:
    s2.add(i)

# All six circles to sample in
choose_drag_circles = []

for x in range(2):
    for y in range(3):
        choose_drag_circles.append(Sprite(circles[1 + x + y * 2], x_offset + drag_x_offset + x * (circle_size + drag_circle_gap), drag_y_offset + y * (-circle_size - drag_circle_gap), circle_normal_scale, origin='m'))

for i in choose_drag_circles:
    s2.add(i)


@s2.game_update
def game_update(delta):
    global answer, tmp_circle, drag_circle_color_index, drag_circle_column_index, drop_circle_column_index, drag_type, current_bar, old_bar, guess, guess_bottom_y, cursor_type, old_cursor_type

    # ----------  Cursor  --------------------------------------------------
    cursor_type = 'normal'
    for index, i in enumerate(choose_drag_circles):
        if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
            cursor_type = 'hand'
            break
    else:
        for index, i in enumerate(choose_circles):
            if current_bar[index] is not None:
                if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
                    cursor_type = 'hand'
                    break

    if cursor_type != old_cursor_type:
        if cursor_type == 'hand':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif cursor_type == 'normal':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        old_cursor_type = cursor_type

    # ----------  Check  --------------------------------------------------
    if g.just_pressed('return') == 1:
        for index, i in enumerate(current_bar):
            if i is None:
                current_bar[index] = randint(0, 5)
        update_circles2()
        g.current_scene = s
        answer = tuple(current_bar)
        current_bar = [None, None, None, None]
        old_bar = [None, None, None, None]

    # ----------  Keyboard 0-6 keys  --------------------------------------------------
    for index, i in enumerate(choose_circles):
        for j in range(7):
            if g.is_pressed(str(j)) and (distance(i, g.mouse_position) <= (circle_size * scale) / 2 / scale):
                current_bar[index] = None if j == 0 else colors.index(circles[j])
                update_circles2()
        if (g.is_pressed('backspace') or g.is_pressed('delete')) and (distance(i, g.mouse_position) <= (circle_size * scale) / 2 / scale):
            current_bar[index] = None
            update_circles2()

    # ----------  Released left click  --------------------------------------------------
    if g.just_pressed('left') == -1:
        if (drop_circle_column_index is not None) and (drag_circle_color_index is not None):
            if drag_type == 'swap' and (drop_circle_column_index != drag_circle_column_index):
                current_bar[drop_circle_column_index], current_bar[drag_circle_column_index] = drag_circle_color_index, current_bar[drop_circle_column_index]
            else:
                current_bar[drop_circle_column_index] = drag_circle_color_index
            drag_circle_color_index = None
            drop_circle_column_index = None
            drag_circle_column_index = None
            drag_type = None
        else:
            if drag_type == 'swap':
                current_bar[drag_circle_column_index] = None
                drag_circle_color_index = None
                drop_circle_column_index = None
                drag_circle_column_index = None
                drag_type = None
        update_circles2()


    # ----------  Just pressed left click  --------------------------------------------------
    elif g.just_pressed('left') == 1:
        for index, i in enumerate(choose_drag_circles):
            if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
                drag_type = 'sample'
                tmp_circle = Sprite(i.img, i.x, i.y, i.scale, origin='m')
                s2.add(tmp_circle)
                drag_circle_color_index = index
                break
        else:
            for index, i in enumerate(choose_circles):
                if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
                    if current_bar[index] is not None:
                        drag_type = 'swap'
                        tmp_circle = Sprite(i.img, i.x, i.y, i.scale, origin='m')
                        s2.add(tmp_circle)
                        drag_circle_color_index = colors.index(i.img)
                        drag_circle_column_index = index
                        current_bar[index] = None
                        update_circles2()
                        break

    # ----------  Moving with left click  --------------------------------------------------
    if g.is_pressed('left'):
        if tmp_circle in s2:
            drop_circle_column_index = None
            tmp_circle.x = g.mouse_position[0]
            tmp_circle.y = g.mouse_position[1]
            distances = []
            for i in choose_circles:
                distances.append(distance(tmp_circle, i))
            if (closest := min(distances)) <= (500 if drag_type == 'sample' else 150):
                drop_circle_column_index = distances.index(closest)
                tmp_circle.x, tmp_circle.y = choose_circles[distances.index(closest)].x, choose_circles[distances.index(closest)].y
    else:
        if tmp_circle in s2:
            s2.remove(tmp_circle)
            drop_circle_column_index = None


# ----------  End of Scene  --------------------------------------------------
setup_new_scene = False
won = False
win_type = 'win'
time_since_setup_new_scene = 0
reached_final_height = [False, False, False, False]
all_bars = [current_bar.copy() for i in range(6)]
target_animate_position = 0, 0
upper_bar_selection = 0
tmp_circle_starting_speed = 30
tmp_circle_speed = tmp_circle_starting_speed
tmp_circle_speed_increase = 1


@s.game_update
def game_update(delta):
    print('a', end='')
    global tmp_circle, drag_circle_color_index, drag_circle_column_index, drop_circle_column_index, drag_type, current_bar, old_bar
    global guess, guess_bottom_y, cursor_type, old_cursor_type, setup_new_scene, time_since_setup_new_scene, reached_final_height, won
    global upper_bar_selection, all_bars, win_type, target_animate_position, tmp_circle_speed

    # ------------
    if win_type == 'win':
        new_height = guess_bottom_y + 150
    else:
        new_height = guess_bottom_y - 150

    if setup_new_scene:
        if won:
            time_since_setup_new_scene += delta
            for index, i in enumerate(grid_circles[guess]):
                if abs(i.y - guess_bottom_y) < abs(i.y - new_height):
                    dist = abs(i.y - guess_bottom_y)
                else:
                    dist = abs(i.y - new_height)
                dist *= 0.2
                dist += 5
                if not reached_final_height[index]:
                    if time_since_setup_new_scene > 0.1 * index:
                        i.y = move_toward(i.y, new_height, dist)
                        if i.y == new_height:
                            reached_final_height[index] = True
                else:
                    i.y = move_toward(i.y, guess_bottom_y, dist)
        else:
            reached_final_height = [True, True, True, True]
        for i in grid_circles[guess]:
            if (i.y != guess_bottom_y) or (not all(reached_final_height)) or (not reached_final_height[0]):
                break
        else:
            setup_new_scene = False
            guess_bottom_y = y_offset + (circle_size + y_circle_gap) * 5
            for i in drag_circles:
                i.y += ((circle_size + y_circle_gap) // 2) * guess
            time_since_setup_new_scene = 0
            reached_final_height = [False, False, False, False]
            g.current_scene = s2
            for i in grid_circles:
                for j in i:
                    j.img = gray
                    j.scale = mini_circle_scaling
            guess = 0
            for i in responses:
                s.remove(i)
            responses.clear()
            current_bar = list(answer)
            old_bar = current_bar.copy()
            update_circles2()
            win_type = 'win'

    # ----------  Cursor  --------------------------------------------------
    cursor_type = 'normal'
    for index, i in enumerate(drag_circles):
        if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
            cursor_type = 'hand'
            break
    else:
        for index, j in enumerate(grid_circles[:guess]):
            for i in j:
                if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
                    cursor_type = 'hand'
                    break
        for index, i in enumerate(grid_circles[guess]):
            if current_bar[index] is not None:
                if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
                    cursor_type = 'hand'
                    break

    if cursor_type != old_cursor_type:
        if cursor_type == 'hand':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif cursor_type == 'normal':
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        old_cursor_type = cursor_type

    # ----------  Check  --------------------------------------------------
    if g.is_pressed('return'):
        if g.just_pressed('r') == 1:
            setup_new_scene = True
    if g.just_pressed('return') == 1 and all(hi is not None for hi in current_bar):
        # -----  Get list of responses  ----------
        response = []
        remaining_current_bar = current_bar.copy()
        remaining = list(answer)
        for index, i in enumerate(current_bar):
            if i == answer[index]:
                response.append(2)
                remaining_current_bar.remove(i)
                remaining.remove(i)
        for index, i in enumerate(remaining_current_bar):
            if i in remaining:
                response.append(1)
                remaining.remove(i)
        for i in range(4 - len(response)):
            response.append(0)

        # -----  Randomize them, to not give any clues!  ----------
        shuffle(response)

        # Go through each response individually, getting the image for it here
        for index, i in enumerate(response):
            if i == 2:
                response_image = correct[index]
            elif i == 1:
                response_image = semi[index]
            else:
                continue  # remove this line to display image
                response_image = wrong[index]

            # Get the x and y offsets, from the left side of where they're placed
            response_x_offset = x_offset - circle_size // 2 - response_offset
            response_y_offset = guess_bottom_y

            if index == 0:  # top left
                response_x_offset += circle_closer_together
                response_y_offset += (mini_circle_size + response_gap) // 2 - circle_closer_together
            elif index == 1:  # top right
                response_x_offset += mini_circle_size + response_gap - circle_closer_together
                response_y_offset += (mini_circle_size + response_gap) // 2 - circle_closer_together
            elif index == 2:  # bottom left
                response_x_offset += circle_closer_together
                response_y_offset -= (mini_circle_size + response_gap) // 2 - circle_closer_together
            elif index == 3:  # bottom right
                response_x_offset += mini_circle_size + response_gap - circle_closer_together
                response_y_offset -= (mini_circle_size + response_gap) // 2 - circle_closer_together
            resp_sprite = Sprite(response_image, response_x_offset, response_y_offset, mini_circle_scaling, origin='m')
            responses.append(resp_sprite)
            s.add(resp_sprite)

        if all(i == 2 for i in response):
            won = True
            setup_new_scene = True
        elif guess == 5:
            win_type = 'lose'
            setup_new_scene = True
        else:
            for i in drag_circles:
                i.y -= (circle_size + y_circle_gap) // 2
            all_bars[guess] = current_bar.copy()
            guess += 1
            upper_bar_selection = guess
            current_bar = [None, None, None, None]
            old_bar = [None, None, None, None]
            guess_bottom_y = y_offset + (circle_size + y_circle_gap) * (5 - guess)












    # ----------  Keyboard 0-6 keys  --------------------------------------------------
    for index, i in enumerate(grid_circles[guess]):
        for j in range(7):
            if g.is_pressed(str(j)) and (distance(i, g.mouse_position) <= (circle_size * scale) / 2 / scale):
                current_bar[index] = None if j == 0 else colors.index(circles[j])
                update_circles()
        if (g.is_pressed('backspace') or g.is_pressed('delete')) and (distance(i, g.mouse_position) <= (circle_size * scale) / 2 / scale):
            current_bar[index] = None
            update_circles()

    if g.just_pressed('up') == 1 and upper_bar_selection > 0:
        upper_bar_selection -= 1
        current_bar = all_bars[upper_bar_selection].copy()
        update_circles()
    if g.just_pressed('down') and upper_bar_selection < guess:
        upper_bar_selection += 1
        current_bar = all_bars[upper_bar_selection].copy()
        update_circles()

    # ----------  Released left click  --------------------------------------------------
    if g.just_pressed('left') == -1:
        if (drop_circle_column_index is not None) and (drag_circle_color_index is not None):
            if drag_type == 'swap' and (drop_circle_column_index != drag_circle_column_index):
                current_bar[drop_circle_column_index], current_bar[drag_circle_column_index] = drag_circle_color_index, current_bar[drop_circle_column_index]
            else:
                current_bar[drop_circle_column_index] = drag_circle_color_index
            drag_circle_color_index = None
            drop_circle_column_index = None
            drag_circle_column_index = None
            drag_type = None
        else:
            if drag_type == 'swap':
                current_bar[drag_circle_column_index] = None
                drag_circle_color_index = None
                drop_circle_column_index = None
                drag_circle_column_index = None
                drag_type = None
        update_circles()


    # ----------  Just pressed left click  --------------------------------------------------
    elif g.just_pressed('left') == 1:
        for index, i in enumerate(drag_circles):
            if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
                drag_type = 'sample'
                tmp_circle = Sprite(i.img, i.x, i.y, i.scale, origin='m')
                s.add(tmp_circle)
                drag_circle_color_index = index
                break
        else:
            for j in grid_circles[:guess]:
                for i in j:
                    if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
                        drag_type = 'sample'
                        tmp_circle = Sprite(i.img, i.x, i.y, i.scale, origin='m')
                        s.add(tmp_circle)
                        drag_circle_color_index = colors.index(i.img)
                        break
            for index, i in enumerate(grid_circles[guess]):
                if distance(g.mouse_position, i) <= (circle_size * scale) / 2 / scale:
                    if current_bar[index] is not None:
                        drag_type = 'swap'
                        tmp_circle = Sprite(i.img, i.x, i.y, i.scale, origin='m')
                        target_animate_position = i.x, i.y
                        # tmp_circle.rect_expansion_amount = 300
                        s.add(tmp_circle)
                        drag_circle_color_index = colors.index(i.img)
                        drag_circle_column_index = index
                        current_bar[index] = None
                        update_circles()
                        break

    # ----------  Moving with left click  --------------------------------------------------
    if g.is_pressed('left'):
        if tmp_circle in s:
            drop_circle_column_index = None
            target_animate_position = g.mouse_position
            distances = []
            for i in grid_circles[guess]:
                distances.append(distance(g.mouse_position, i))
            if (closest := min(distances)) <= (500 if drag_type == 'sample' else 150):
                drop_circle_column_index = distances.index(closest)
                target_animate_position = grid_circles[guess][distances.index(closest)].x, grid_circles[guess][distances.index(closest)].y
            target_velocity = move_toward((tmp_circle.x, tmp_circle.y), target_animate_position, tmp_circle_speed, True)
            tmp_circle.velocity = move_toward(tmp_circle.velocity, target_velocity, 40)
            if (tmp_circle.x, tmp_circle.y) == target_animate_position:
                tmp_circle_speed = tmp_circle_starting_speed
            else:
                tmp_circle_speed += tmp_circle_speed_increase
            # if tmp_circle_speed > tmp_circle.current_speed:
            #     tmp_circle_speed = tmp_circle.current_speed
    else:
        if tmp_circle in s:
            s.remove(tmp_circle)
            drop_circle_column_index = None


g.run_game()
