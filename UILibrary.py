import pickle
import os
import sys

# ---------------------------------------------------------

txt_save_folder = r''


# ---------------------------------------------------------
# With this library, you can edit a dictionary, which will save its information, even if you close and rerun the python script.
# It accomplishes this through a pickle file, which has to be saved somewhere.
# If the variable above is left as an empty string, it'll be saved in the current directory. Otherwise,
# it'll be saved in the folder above. (no slash at the end)

def large_number_formatter(number, type='notation', decimal_places=2):
    num = str(number)
    length = len(num)
    thousands = (len(num) - 1) // 3
    if type == ',':
        for i in range(thousands):
            i += 1
            num = num[:length - i * 3] + ',' + num[length - i * 3:]
        return num
    else:
        notations = 'K', 'M', 'B', 'T', 'Q'
        return str(round(number / 10 ** (thousands * 3), decimal_places)) + notations[thousands - 1]


def check_type(val, validation):
    if validation == int:
        try:
            int(val)
            return True
        except ValueError:
            pass
    elif validation == float:
        try:
            float(val)
            return True
        except ValueError:
            pass
    return False


if txt_save_folder != '':
    txt_save_folder += '/'


class _SavedInfo:
    def __init__(self, file_name):
        self.path = txt_save_folder + file_name + '.pkl'
        self.stuff = {}
        with open(self.path, 'a'):
            pass
        if os.path.getsize(self.path) > 0:
            with open(self.path, 'rb') as f:
                self.stuff = pickle.load(f)

    def clear(self):
        self.stuff.clear()
        self._update()

    def __getitem__(self, item):
        return self.stuff[item]

    def _update(self):
        with open(self.path, 'wb') as f:
            f.truncate(0)
            pickle.dump(self.stuff, f, pickle.HIGHEST_PROTOCOL)

    def __setitem__(self, key, value):
        self.stuff[key] = value
        self._update()


class UI:
    class ProgressBar:
        def __init__(self, ui_class):
            self._progress = 0
            self._total = 0
            self._percent = 0
            self.style = ui_class.style

        def update(self, progress, total, description='', length=50):
            if total == 0:
                print('\r' + description + self.style['progress_bar_done'] + ' Done!')
            else:
                percent = int(progress / total * length)
                if percent != self._percent:
                    print('\r' + f"{description} {self.style['progress_bar_color']}{self.style['progress_bar'] * percent}{self.style['reset']}{' ' * (100 - percent)} {percent}%", end='')
                    if progress >= total:
                        print('\r' + description + self.style['progress_bar_done'] + ' Done!')
                    self._percent = percent

    class _OptionsList:
        """Used for making lists, of options!"""

        def __init__(self, ui_class, options=()):
            self.options = []
            self.ui_class = ui_class
            self.style = self.ui_class.style
            for i in options:
                self.add(i)

        def error_print(self, text):
            print(self.style['error'] + text + '\n')

        def add(self, option, option_func=None):
            if option_func is None:
                self.options.append((str(option), option))
            else:
                self.options.append((str(option), option_func))

        def show(self):
            for index, i in enumerate(self.options):
                index += 1
                print(f"{self.style['options_list_number']}{index}{self.style['options_list_separator']}{self.style['normal_output_color']}{str(i[0])}")

            while True:
                try:
                    inp = input(f"{self.style['bold_formatting']}{self.style['ask_color']}Choice: {self.style['reset']}{self.style['user_input']}")
                    if inp == '/help':
                        print(self.style['normal_output_color'] + 'Listed above are different options; simply type the number to the left of the option you want to select.\n')
                        continue
                    elif inp == '':
                        return self.options[0][1]
                    inp = int(inp)
                    self.options[inp - 1]  # Python will try to run this line. If it raises an error, we'll know that something is wrong.

                    if inp == 0:
                        raise IndexError
                    return self.options[inp - 1][1]
                except (IndexError, ValueError):
                    self.error_print('Your choice must correspond to one of the options above!')

    class Colors:
        def __init__(self):
            self.reset = '\033[0m'

            self.white = '\33[97m'
            self.gray = '\33[37m'
            self.black = ''

            self.red = '\33[31m'
            self.orange = '\33[36m'
            self.yellow = '\33[33m'
            self.green = '\33[32m'
            self.blue = '\33[34m'
            self.purple = '\33[35m'

            self.bold = '\33[1m'
            self.underline = '\33[4m'
            self.italic = '\33[3m'
            self.strikethrough = '\33[9m'

            self.full_rectangle = '█'
            self.rectangles = {'Upper 1/2': '▀', '1/8': '▁', '1/4': '▂', '3/8': '▃', '1/2': '▄', '5/8': '▅', '3/4': '▆',
                               '7/8': '▇', '1': '█', 'l7/8': '▉', 'l3/4': '▊', 'l5/8': '▋', 'l1/2': '▌', 'l3/8': '▍',
                               'l1/4': '▎', 'l1/8': '▏', 'r1/2': '▐', 'light': '░', 'medium': '▒', 'dark': '▓',
                               'u1/8': '▔', 'r1/8': '▕'}

    def __init__(self, txt_name=None):
        if txt_name is not None:
            self.save_info = _SavedInfo(txt_name)
        self.colors = self.Colors()
        self.style = {'ask_color': self.colors.yellow, 'options_list_number': self.colors.yellow, 'options_list_separator': ' - ', 'progress_bar': self.colors.full_rectangle,
                      'progress_bar_color': self.colors.yellow, 'progress_bar_done': self.colors.green, 'normal_output_color': '\033[0m', 'user_input': self.colors.reset,
                      'error': self.colors.red, 'bold_formatting': self.colors.bold, 'reset': self.colors.reset}
        self.progress_bar = self.ProgressBar(self)

    def quit(self):
        sys.exit()

    def set_default(self, name, default_value):
        if name not in self.save_info.stuff:
            self.save_info[name] = default_value

    def OptionsList(self, options=()):
        return self._OptionsList(self, options)

    def error_print(self, text):
        print(self.style['error'] + text + '\n')

    def ask(self, question, validation=str, extra=None, end=': '):
        while True:
            add = ''
            if validation == 'y/n' or validation == 'yn':
                add += ' (y/n)'
            inp = input(self.style['bold_formatting'] + self.style['ask_color'] + question + add + end + self.colors.reset + self.style['user_input'])
            if inp == '/help':
                if validation == str or validation == 'str':
                    mes = 'Your answer can be pretty much anything.'
                elif validation == int or validation == 'int':
                    mes = 'Your answer should be an integer.'
                elif validation == float or validation == 'float':
                    mes = 'Your answer should be a float value. Any normal number (decimals included) pretty much.'
                elif validation == 'y/n' or validation == 'yn':
                    mes = """Your answer should just be a lowercase "y" for yes, or a lowercase "n" for no. y or n, that's it."""
                elif validation == tuple or validation == 'tuple':
                    if extra == int or extra == 'int':
                        idk = 'integers'
                    elif extra == float or extra == 'float':
                        idk = 'floats'
                    else:
                        idk = 'strings'
                    mes = f"""This one's a bit more tricky. You probably need to provide multiple answers (not necessarily, but more than likely), in this case {idk}.
Separate them with spaces, include a backslash directly before one ("...\\ ...") to ignore it."""
                else:
                    mes = "The validation is something else, you're on your own for this one!"
                print(self.style['normal_output_color'] + mes + '\n')
                continue

            if validation == str or validation == 'str':
                return inp
            elif validation == int or validation == 'int':
                if check_type(inp, int):
                    return int(inp)
                else:
                    self.error_print(f'Your answer must be an integer')
            elif validation == float or validation == 'float':
                if check_type(inp, float):
                    return float(inp)
                else:
                    self.error_print(f'Your answer must be a float')
            elif validation == 'y/n' or validation == 'yn':
                if inp == 'y':
                    return True
                elif inp == 'n':
                    return False
                else:
                    self.error_print('Your response should be either "y" or "n".')
            elif validation == tuple or validation == 'tuple':
                inp += ' '
                inp2 = []
                previous = 0
                try:
                    for index, i in enumerate(inp):
                        if i == ' ' and index > 0:
                            if inp[index - 1] != '\\':
                                part = inp[previous:index]
                                previous = index + 1
                                if extra == str or extra == 'str':
                                    inp2.append(int(part))
                                    continue
                                if extra == int or extra == 'int':
                                    if check_type(part, int):
                                        inp2.append(int(part))
                                        continue
                                if extra == float or extra == 'float':
                                    if check_type(part, float):
                                        inp2.append(float(part))
                                        continue
                                raise ValueError
                    print(inp2)
                    return tuple(inp2)
                except ValueError:
                    self.error_print('The values must be integers')
            else:
                while True:
                    try:
                        return validation[0](inp)
                    except validation[1]:
                        self.error_print(validation[2])
