from PIL import Image, ImageDraw, ImageFont
from colorsys import hsv_to_rgb

# --------------------------------------------------------------------
txt_name = 'PythonPoint - Test1.txt'

font_shorts = {'Roboto': 'Fonts/Roboto/Roboto-Bold.ttf'}


# This is the only thing you should edit (or replace with an input() based solution, if you'd like).
# Everything below is the actual code (including the resolution variable, which is editable through the txt document.)
# --------------------------------------------------------------------

def color_convert(*color):
    color = list(color)
    transparency = 255
    if len(color) == 1:
        color = list(color[0])
    if len(color) == 4:
        transparency = color.pop(3)
    color = list(hsv_to_rgb(color[0] / 10, color[1] / 10, color[2] / 10))
    for index, i in enumerate(color):
        color[index] = round(i * 255)
    color.append(transparency)
    return tuple(color)


resolution = (1920, 1080)
d_background_color = (255, 255, 255, 255)

with open(txt_name, 'r') as f:
    instructions = f.read().split('\n\n')

for index, i in enumerate(instructions):  # Split the sections by line
    instructions[index] = i.split('\n')

first_stuff = False
for i in instructions[0]:
    i = i.split('-')
    if len(i) == 2:
        resolution = (int(i[0]), int(i[1]))
        first_stuff = True
    elif len(i) == 3:
        if len(i) == 3:
            d_background_color = color_convert(int(i[0]), int(i[1]), int(i[2]), 255)
        else:
            d_background_color = color_convert(int(i[0]), int(i[1]), int(i[2]), int(i[3]))
        first_stuff = True

if first_stuff:
    instructions.pop(0)


def convert(y):
    return resolution[1] - y


def process_pos(offset_info, size=(0, 0)):
    size = (size[0], -size[1])
    half_size = (size[0] // 2, size[1] // 2)

    if offset_info[0] == 'bottom_left' or offset_info[0] == 'bl':
        pos = [int(offset_info[1]), int(offset_info[2])]
        anchor = 'ld'
    elif offset_info[0] == 'bottom_right' or offset_info[0] == 'br':
        pos = [resolution[0] - int(offset_info[1]), int(offset_info[2])]
        pos[0] -= size[0]
        anchor = 'rd'
    elif offset_info[0] == 'top_left' or offset_info[0] == 'tl':
        pos = [int(offset_info[1]), resolution[1] - int(offset_info[2])]
        pos[1] += size[1]
        anchor = 'la'
    elif offset_info[0] == 'top_right' or offset_info[0] == 'tr':
        pos = [resolution[0] - int(offset_info[1]), resolution[1] - int(offset_info[2])]
        pos[0] -= size[0]
        pos[1] += size[1]
        anchor = 'ra'
    elif offset_info[0] == 'middle' or offset_info[0] == 'm':
        pos = [resolution[0] // 2 + int(offset_info[1]), resolution[1] // 2 + int(offset_info[2])]
        pos[0] -= half_size[0]
        pos[1] += half_size[1]
        anchor = 'mm'
    elif offset_info[0] == 'top' or offset_info[0] == 't':
        pos = [resolution[0] // 2 + int(offset_info[1]), resolution[1] - int(offset_info[2])]
        pos[0] -= half_size[0]
        anchor = 'ma'
    elif offset_info[0] == 'left' or offset_info[0] == 'l':
        pos = [int(offset_info[1]), resolution[1] // 2 + int(offset_info[2])]
        pos[1] += half_size[1]
        anchor = 'lm'
    elif offset_info[0] == 'right' or offset_info[0] == 'r':
        pos = [resolution[0] - int(offset_info[1]), resolution[1] // 2 + int(offset_info[2])]
        pos[0] -= size[0]
        pos[1] += half_size[1]
        anchor = 'rm'
    elif offset_info[0] == 'bottom' or offset_info[0] == 'b':
        pos = [resolution[0] // 2 + int(offset_info[1]), int(offset_info[2])]
        pos[0] -= half_size[0]
        anchor = 'ma'
    else:
        if len(offset_info) == 2:
            pos = [int(offset_info[0]), int(offset_info[1])]
            anchor = 'ld'
        else:
            text = f'Given anchor "{offset_info[0]}" within input {offset_info}.\nAnchors must be either t, tr, r, br, b, bl, l, tl, or m (middle). All of these can also be written out (e.g. top_left, right)'
            raise ValueError(text)
    pos[1] -= size[1]
    pos = tuple(pos)
    return pos, anchor


for slide_index, slide in enumerate(instructions):  # Actually iterate through and generate stuff
    im = Image.new('RGBA', resolution, d_background_color)
    for element in slide:
        parts = element.split('::')

        extension = parts[0][-4:]
        if len(parts) == 1:
            parts = parts[0].replace(' ', '').split('=')
            for s2i, slide2 in enumerate(instructions):
                for e2i, element2 in enumerate(slide2):
                    parts2 = element2.split('::')
                    le = len(parts2[0])
                    if len(parts2) == 2:
                        if parts[0] in instructions[s2i][e2i]:
                            instructions[s2i][e2i] = parts2[0] + '::' + parts2[1].replace(parts[0], parts[1])
        elif extension == '.png' or extension == '.jpg':
            scale = 1
            pos = (0, 0)
            img = Image.open(parts[0])

            paras = []
            for parameter_group in parts[1].split(', '):
                para = parameter_group.split('-')
                if len(para) == 1:
                    scale = float(para[0])
                else:
                    paras.append(para)
            size = img.size
            img = img.resize((round(size[0] * scale), round(size[1] * scale)))
            size = img.size
            for para in paras:
                pos = process_pos(para, size)[0]
            im.paste(img, (pos[0], convert(pos[1])))
        else:
            font = font_shorts['Roboto']
            size = 30
            pos = (0, 0)
            anchor = 'ld'
            color = (0, 0, 0)
            wrap_length = 1200
            for parameter_group in parts[1].split(', '):
                para = parameter_group.split('-')
                if para[0] in font_shorts:
                    font = font_shorts[para[0]]
                    size = int(para[1])
                elif not para[0].isdigit() or len(para) == 2:
                    pos, anchor = process_pos(para)
                elif len(para) == 1:
                    wrap_length = int(para[0]) * 20
                else:
                    color = (float(para[0]), float(para[1]), float(para[2]))

            fnt = ImageFont.truetype(font, size)
            d = ImageDraw.Draw(im)
            color = color_convert(color)
            texts = []
            tmp_line = []
            for word in parts[0].split(' '):
                tmp_line.append(word)
                if d.textsize(' '.join(tmp_line), fnt)[0] > wrap_length:
                    texts.append(' '.join([i for i in tmp_line[:-1]]))
                    tmp_line = [word]
            if len(texts) == 0:
                texts = [' '.join([i for i in tmp_line])]

            d.multiline_text((pos[0], convert(pos[1])), '\n'.join(texts), anchor=anchor, font=fnt, fill=color)

    im.show()
