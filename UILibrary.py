import pickle
from sys import exit as s_exit, argv
from platform import system
import subprocess
from os import system as run_command
from time import time
from pathlib import Path

try:
    import pyperclip

    tk = None
except ModuleNotFoundError:
    pyperclip = None
    from tkinter import Tk

    tk = Tk()

# Made by interestingbookstore
# Github: https://github.com/interestingbookstore/randomstuff
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


# def duration_formatter(duration, hi)


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
        try:
            with open(self.path, 'rb') as f:
                self.stuff = pickle.load(f)
        except FileNotFoundError:
            with open(self.path, 'a'):
                pass

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
            self._percent = None
            self.style = ui_class.style
            self._start_time = 0

        def update(self, progress, total, description='', length=50):
            if self._percent is None:
                self._start_time = time()
            if total == 0:  # If you only have to do 0 stuff, it's impossible to not have already done it
                print('\r' + description + self.style['progress_bar_done'] + ' Done!')
            else:
                if progress == 0:
                    time_remaining = ''
                else:
                    time_remaining = f'{round((time() - self._start_time) * (total - progress) / progress)} seconds left'
                fraction = progress / total
                percent = int(fraction * 100)
                amount = int(fraction * length)
                if percent != self._percent:
                    print('\r' + f"{description} {self.style['progress_bar_color']}{self.style['progress_bar'] * amount}{self.style['reset']}{' ' * (length - amount)} {percent}%  {time_remaining}", end='')
                    self._percent = percent
                    if percent >= 100:
                        print('\r' + description + self.style['progress_bar_done'] + ' Done!' + self.style['reset'])
                        self._percent = None

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
                    if inp < 0:
                        inp += 1
                    elif inp == 0:
                        raise IndexError
                    self.options[inp - 1]  # Python will try to run this line. If it raises an error, we'll know that something is wrong.

                    return self.options[inp - 1][1]
                except (IndexError, ValueError):
                    option_names = tuple(i[0] for i in self.options)
                    inp = str(inp)
                    if inp in option_names:
                        return self.options[option_names.index(inp)][1]
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

    def __init__(self, txt_name=None, formatting=True):
        if txt_name is not None:
            self.save_info = _SavedInfo(txt_name)
        self.os = system().lower()
        if self.os == 'darwin':
            self.os = 'macos'
        self.colors = self.Colors()
        if not formatting:
            self.colors.reset = ''

            self.colors.white = ''
            self.colors.gray = ''
            self.colors.black = ''

            self.colors.red = ''
            self.colors.orange = ''
            self.colors.yellow = ''
            self.colors.green = ''
            self.colors.blue = ''
            self.colors.purple = ''

            self.colors.bold = ''
            self.colors.underline = ''
            self.colors.italic = ''
            self.colors.strikethrough = ''
        self.style = {'ask_color': self.colors.yellow, 'options_list_number': self.colors.yellow, 'options_list_separator': ' - ', 'progress_bar': self.colors.full_rectangle,
                      'progress_bar_color': self.colors.yellow, 'progress_bar_done': self.colors.green, 'normal_output_color': self.colors.reset, 'user_input': self.colors.reset,
                      'error': self.colors.red, 'bold_formatting': self.colors.bold, 'reset': self.colors.reset}
        self.progress_bar = self.ProgressBar(self)

    def quit(self):
        s_exit()

    def get_clipboard(self):
        if pyperclip is not None:
            return pyperclip.paste()
        return tk.clipboard_get()

    def set_clipboard(self, text):
        if pyperclip is not None:
            pyperclip.copy(text)
        else:
            raise ModuleNotFoundError('UILibrary doesn\'t currently support pasting to clipboard without the module "pyperclip"')

    def set_default(self, name, default_value):
        if name not in self.save_info.stuff:
            self.save_info[name] = default_value

    def get_unique_file(self, path, invalid_characters='remove'):
        if not (invalid_characters == 'remove' or invalid_characters == 'keep'):
            raise Exception(f'The invalid characters parameter should be either "remove" or "keep", but "{invalid_characters}" was given.')

        if Path(path).is_file():
            filename = '.'.join(path.split('.')[:-1])
            extension = '.' + path.split('.')[-1]

            filename_addition = ' (*)'

            num = 1
            while Path(filename + filename_addition.replace('*', str(num)) + extension).is_file():
                num += 1

            path = filename + filename_addition.replace('*', str(num)) + extension
        if invalid_characters == 'remove':
            if self.os == 'windows':
                bad_characters = r'<>:"|?*'
                for i in bad_characters:
                    if ':\\' in path:
                        path = path.split(':\\', 1)[0] + ':\\' + path.split(':\\', 1)[1].replace(i, '')
                    else:
                        path = path.replace(i, '')

        return path

    def OptionsList(self, options=()):
        return self._OptionsList(self, options)

    def error_print(self, text):
        print(self.style['error'] + text + '\n')

    def get_console_arguments(self):
        return argv[1:]

    def run_console_command(self, command):
        run_command(command)

    def open_path(self, path):
        path = path.replace('\\', '/')
        if self.os == 'windows':
            subprocess.Popen(f'explorer /select,"{path}"')
        elif self.os == 'macos':
            subprocess.Popen(['open', path])
        elif self.os == 'linux':
            run_command(f'gio open "{path}"')  # Origionally    subprocess.Popen(['xdg-open', path])    was used, but gio is faster, and it doesn't print a bunch of errors...

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
                elif validation == bool or validation == 'y/n' or validation == 'yn':
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
            elif validation == bool or validation == 'y/n' or validation == 'yn':
                if inp == 'y':
                    return True
                elif inp == 'n':
                    return False
                else:
                    self.error_print('Your response should be either "y" or "n".')
            elif validation == tuple or validation == 'tuple':
                inp = [i.strip(' ') for i in inp.split(',')]

                for i in inp:
                    if extra == 'int':
                        if not check_type(i, int):
                            self.error_print('Your response consist of one or multiple integers, separated by a comma.')
                    elif extra == 'float':
                        if not check_type(i, float):
                            self.error_print('Your response consist of one or multiple float values, separated by a comma.')
                return inp

            else:
                while True:
                    try:
                        return validation[0](inp)
                    except validation[1]:
                        self.error_print(validation[2])
