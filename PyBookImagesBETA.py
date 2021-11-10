from PIL import Image, ImageDraw, ImageFont



# Made by interestingbookstore
# Github: https://github.com/interestingbookstore/randomstuff
# -----------------------------------------------------------------------
# Version released on November 10 2021
# ---------------------------------------------------------



def r(start, stop):
    if start > stop:
        for i in range(stop, start + 1):
            yield i
    else:
        for i in range(start, stop + 1):
            yield i


class PyBookImage:
    def __init__(self, *params):
        parameter_sizes = 1, 2, 3
        if len(params) not in parameter_sizes:
            Exception('Parameters can either be "{path to image}" or (width, height, background=(0, 0, 0, 0))')
        if len(params) == 1:
            self.im = Image.open(params[0])
            self.resx, self.resy = self.im.size
        else:
            if len(params) == 2:
                params = params[0], params[1], (0, 0, 0, 0)
            width, height, background = params
            self.resx, self.resy = width, height
            self.im = Image.new('RGBA', (width, height), background).convert('RGBA')
        self.img = self.im.load()
        self.d = ImageDraw.Draw(self.im)

    def __getitem__(self, item):
        return self.img[item[0], item[1]]

    def __setitem__(self, key, value):
        self.img[key] = value

    def normalize_y(self, y):
        if type(y) == tuple:
            return y[0], self.resy - y[1] - 1
        return self.resy - y - 1

    def fill(self, color):
        self.im.paste(color, (0, 0, self.resx, self.resy))

    def add_point(self, x, y, color, image=None, set=False):
        if image is None:
            image = self.img

        y = self.normalize_y(y)
        if 0 <= x < self.resx and 0 <= y < self.resy:
            if set:
                image[x, y] = color
            else:
                if len(color) == 4:
                    nt = color[3]
                    color = color[:3]
                else:
                    nt = 255
                old = image[x, y]
                ot = old[3]
                old = old[:3]
                st = nt + ot
                new = [0, 0, 0, 0]
                for index, i in enumerate(color):
                    new[index] = round(old[index] * (ot - nt) / 255 + color[index] * nt)
                new[3] = st
                for index, i in enumerate(new):
                    if i > 255:
                        new[index] = 255

                image[x, y] = tuple(new)

        if image != self.img:
            return image

    def draw_line(self, start, end, thickness, color):
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

        line_im = Image.new('RGBA', (self.resx, self.resy))
        line_img = line_im.load()
        self.draw_circle(start, thickness, color, line_img)
        self.draw_circle(end, thickness, color, line_img)

        for x in r(sx2, ex2):
            for y in r(sy2, ey2):
                line_length = ((sx - ex) ** 2 + (sy - ey) ** 2) ** 0.5
                distance = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
                distance2 = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
                if distance < distance2:
                    distance_long = distance2
                    cx, cy = sx, sy
                else:
                    distance_long = distance
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
                distance = ((x - intersection_x) ** 2 + (y - intersection_y) ** 2) ** 0.5
                if distance <= thickness:
                    line_img = self.add_point(x, y, color, line_img, True)
                else:
                    distance -= thickness
                    if distance < 1:
                        line_img = self.add_point(x, y, (color[0], color[1], color[2], round(color[3] * (1 - distance))), line_img, True)
        self.im.alpha_composite(line_im, (0, 0))

    def draw_rectangle(self, x, y, width, height, color, corner_radius=0):
        if corner_radius != 0:

            if len(color) == 3:
                color = color[0], color[1], color[2], 255

            rectangle_im = Image.new('RGBA', (self.resx, self.resy))
            rectangle_img = rectangle_im.load()
            d2 = ImageDraw.Draw(rectangle_im)

            d2.rectangle((x, self.normalize_y(y) - height, x + width, self.normalize_y(y)), color)

            # ----------------------------
            origin = x + corner_radius, y + height - corner_radius
            for x2 in range(x, x + corner_radius):
                for y2 in range(y + height - corner_radius + 1, y + height + 1):
                    distance = ((x2 - origin[0]) ** 2 + (y2 - origin[1]) ** 2) ** 0.5

                    if distance <= corner_radius:
                        rectangle_img[x2, self.normalize_y(y2)] = color
                    else:
                        distance -= corner_radius
                        if distance < 1:
                            rectangle_img[x2, self.normalize_y(y2)] = color[0], color[1], color[2], round(color[3] * (1 - distance))
                        else:
                            rectangle_img[x2, self.normalize_y(y2)] = 0, 0, 0, 0
            # ----------------------------
            origin = x + width - corner_radius, y + height - corner_radius
            for x2 in range(x + width - corner_radius + 1, x + width):
                for y2 in range(y + height - corner_radius + 1, y + height + 1):
                    distance = ((x2 - origin[0]) ** 2 + (y2 - origin[1]) ** 2) ** 0.5

                    if distance <= corner_radius:
                        print(f'rectangle_img[{x2}, {self.normalize_y(y2)}] = color[0], color[1], color[2], round(color[3] * (1 - distance))')
                        print(f'x2: {x2} y2: {y2}')
                        rectangle_img[x2, self.normalize_y(y2)] = color
                    else:
                        distance -= corner_radius
                        if distance < 1:
                            print(f'rectangle_img[{x2}, {self.normalize_y(y2)}] = color[0], color[1], color[2], round(color[3] * (1 - distance))')
                            print(f'x2: {x2} y2: {y2}')
                            rectangle_img[x2, self.normalize_y(y2)] = color[0], color[1], color[2], round(color[3] * (1 - distance))
                        else:
                            rectangle_img[x2, self.normalize_y(y2)] = 0, 0, 0, 0
            # ----------------------------
            origin = x + corner_radius, y + corner_radius
            for x2 in range(x, x + corner_radius):
                for y2 in range(y, y + corner_radius):
                    distance = ((x2 - origin[0]) ** 2 + (y2 - origin[1]) ** 2) ** 0.5

                    if distance <= corner_radius:
                        rectangle_img[x2, self.normalize_y(y2)] = color
                    else:
                        distance -= corner_radius
                        if distance < 1:
                            rectangle_img[x2, self.normalize_y(y2)] = color[0], color[1], color[2], round(color[3] * (1 - distance))
                        else:
                            rectangle_img[x2, self.normalize_y(y2)] = 0, 0, 0, 0
            # ----------------------------
            origin = x + width - corner_radius, y + corner_radius
            for x2 in range(x + width - corner_radius + 1, x + width):
                for y2 in range(y, y + corner_radius):
                    distance = ((x2 - origin[0]) ** 2 + (y2 - origin[1]) ** 2) ** 0.5

                    if distance <= corner_radius:
                        rectangle_img[x2, self.normalize_y(y2)] = color
                    else:
                        distance -= corner_radius
                        if distance < 1:
                            rectangle_img[x2, self.normalize_y(y2)] = color[0], color[1], color[2], round(color[3] * (1 - distance))
                        else:
                            print(f'rrrrrrrrrrectangle_img[{x2}, {self.normalize_y(y2)}] = color[0], color[1], color[2], round(color[3] * (1 - distance))')
                            print(f'x2: {x2} y2: {y2}')
                            rectangle_img[x2, self.normalize_y(y2)] = 0, 0, 0, 0
            # ----------------------------

            self.im.alpha_composite(rectangle_im)

    def draw_lines(self, points, thickness, color, close=False):
        if close:
            points.append(points[0])

        line_im = Image.new('RGBA', (self.resx, self.resy))
        line_img = line_im.load()

        lines = [(i, points[index - 1]) for index, i in enumerate(points)]

        for i in lines:
            start, end = i
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

            self.draw_circle(start, thickness, color, line_img)
            self.draw_circle(end, thickness, color, line_img)

            for x in r(sx2, ex2):
                for y in r(sy2, ey2):
                    line_length = ((sx - ex) ** 2 + (sy - ey) ** 2) ** 0.5
                    distance = ((x - sx) ** 2 + (y - sy) ** 2) ** 0.5
                    distance2 = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
                    if distance < distance2:
                        distance_long = distance2
                        cx, cy = sx, sy
                    else:
                        distance_long = distance
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
                    distance = ((x - intersection_x) ** 2 + (y - intersection_y) ** 2) ** 0.5
                    if distance <= thickness:
                        line_img = self.add_point(x, y, color, line_img, True)
                    else:
                        distance -= thickness
                        if distance < 1:
                            line_img = self.add_point(x, y, (color[0], color[1], color[2], round(color[3] * (1 - distance))), line_img, False)
        self.im.alpha_composite(line_im, (0, 0))
        # for point, point2 in lines:
        #     point = point[0], self.normalize_y(point[1])
        #     im_negative = line_im.crop((point[0] - thickness, point[1] - thickness, point[0] + thickness, point[1] + thickness))
        #     source = im_negative.split()
        #     a = source[3].point(lambda i: 255 - i)
        #     im_negative = Image.merge('RGBA', (source[0], source[1], source[2], a))
        #
        #     im_negative.save('aaahi.png')

    def draw_square(self, origin, radius, fill):
        for x in r(origin[0] - radius, origin[0] + radius):
            for y in r(origin[1] - radius, origin[1] + radius):
                self.add_point(x, y, fill)

    def draw_circle(self, origin, radius, fill, image=None):
        if len(fill) == 3:
            fill = fill[0], fill[1], fill[2], 255
        origin = origin[0], origin[1]

        for x in r(origin[0] - radius, origin[0] + radius):
            for y in r(origin[1] - radius, origin[1] + radius):
                distance = ((x - origin[0]) ** 2 + (y - origin[1]) ** 2) ** 0.5

                if distance <= radius:
                    self.add_point(x, y, fill, image)
                else:
                    distance -= radius
                    if distance < 1:
                        self.add_point(x, y, (fill[0], fill[1], fill[2], round(fill[3] * (1 - distance))), image)

    def draw_text(self, text, x, y, size, font, color, anchor='m'):
        if anchor == 'tl':
            anchor = 'lt'
        elif anchor == 't':
            anchor = 'mt'
        elif anchor == 'tr':
            anchor = 'rt'
        elif anchor == 'l':
            anchor = 'lm'
        elif anchor == 'm':
            anchor = 'mm'
        elif anchor == 'r':
            anchor = 'rm'
        elif anchor == 'bl':
            anchor = 'ls'
        elif anchor == 'b':
            anchor = 'ms'
        elif anchor == 'br':
            anchor = 'rs'

        font = ImageFont.truetype(font, size)
        self.d.text(self.normalize_y((x, y)), text, color, font, anchor)

    def save(self, path):
        if '.' not in path:  # It's lazy, and not perfect, I'll get back to it.
            path += '.png'
        self.im.save(path)
