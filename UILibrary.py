# ---------------------------------------------------------

txt_save_folder = r''

# ---------------------------------------------------------
# With this library, you can edit a dictionary, which will save its information, even if you close and rerun the python script.
# It accomplishes this through a pickle file, which has to be saved somewhere.
# If the variable above is left as an empty string, it'll be saved in the current directory. Otherwise,
# it'll be saved in the folder above. (no slash at the end)

import pickle
import os


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

    def __getitem__(self, item):
        return self.stuff[item]

    def _update(self):
        with open(self.path, 'wb') as f:
            f.truncate(0)
            pickle.dump(self.stuff, f, pickle.HIGHEST_PROTOCOL)

    def __setitem__(self, key, value):
        self.stuff[key] = value
        self._update()


class OptionsList:
    """Used for making lists, of options!"""

    def __init__(self, uiclass):
        self.options = []
        self.uiclass = uiclass

    def error_print(self, text):
        print(self.uiclass.style['ERROR'] + text + '\n')

    def add(self, name, function):
        self.options.append((name, function))

    def run(self):
        for index, i in enumerate(self.options):
            index += 1
            print(f"{self.uiclass.style['HEADER']}{index}{self.uiclass.style['LIST_SEP']}{self.uiclass.style['TEXT']}{i[0]}")

        while True:
            try:
                inp = input(f"{self.uiclass.style['HEADER2']}Choice:{self.uiclass.style['USER_INPUT']} ")
                if inp == '/help':
                    print(self.uiclass.style['TEXT'] + 'Listed above are different options. Simple type the number to the left of the option you want to select.\n')
                    continue
                inp = int(inp)
                self.options[inp - 1]  # Python will try to run this line. If it raises an error, we'll know that something is wrong.

                if inp == 0:
                    raise IndexError
                break
            except (IndexError, ValueError):
                self.error_print('Your choice must correspond to one of the options above!')

        option = self.options[inp - 1][1]
        if type(option) == tuple:
            option[0](option[1])
        else:
            option()


class UI:

    def __init__(self, txt_name):
        self.save_info = _SavedInfo(txt_name)
        self.run = False
        self.steps = None
        self.style = {'HEADER': '\33[33m', 'HEADER2': '\33[34m', 'TEXT': '\033[0m', 'LIST_SEP': ' - ', 'USER_INPUT': '\033[0m', 'ERROR': '\33[31m'}
        self.repeating = False

    def on_run(self, func):  # used for decorator
        self.steps = func

    def error_print(self, text):
        print(self.style['ERROR'] + text + '\n')

    def start(self):
        self.run = True
        while self.run:
            self.steps()

    def ask(self, question, validation=str, extra=None, end=': '):
        while True:
            add = ''
            if validation == 'y/n' or validation == 'yn':
                add += ' (y/n)'
            inp = input(self.style['HEADER2'] + question + add + end + self.style['TEXT'])
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
                print(self.style['TEXT'] + mes + '\n')
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

    def repeat(self, func):  # Used for decorator
        self.repeating = True
        while self.repeating:
            func()
