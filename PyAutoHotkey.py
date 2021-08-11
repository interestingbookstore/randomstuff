from pynput import keyboard
from pynput.keyboard import Key, Controller as _kc
from pynput.mouse import Button, Controller as _mc
import tkinter as tk
from time import sleep

# -----  Used exclusively for getting screen resolution  --------------------------------------
_root = tk.Tk()
_yres = _root.winfo_screenheight()
# -----  to move the origin to the bottom left of the screen  ---------------------------------

_kc = _kc()
_mc = _mc()


def do_nothing(*args):
    pass


def wait(seconds):
    sleep(seconds)


class PyAutoHotkey:
    def __init__(self):
        self.on_press_function = do_nothing
        self.on_release_function = do_nothing
        self._key_names = {Key.ctrl: 'ctrl', Key.alt: 'alt', Key.shift: 'shift', Key.cmd: 'windows'}
        self._inv_key_names = {v: k for k, v in self._key_names.items()}

    def on_press(self, function):
        self.on_press_function = function

    def on_release(self, function):
        self.on_release_function = function

    def init_listener(self):
        def on_press(key):
            key2 = str(key)
            if "'" in key2:
                key2 = key2.strip("'")
            else:
                if key in self._key_names:
                    key2 = self._key_names[key]
                else:
                    print(f'Key {key} not valid key!')
                    pass

            self.on_press_function(key2)

        def on_release(key):
            key2 = str(key)
            if "'" in key2:
                key2 = key2.strip("'")
            else:
                if key in self._key_names:
                    key2 = self._key_names[key]
                else:
                    print(f'Key {key} not valid key!')
                    pass

            self.on_release_function(key2)

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    def _convert_key(self, key):
        if key == 'left':
            return 'm', Button.left
        elif key == 'right':
            return 'm', Button.right
        elif key in self._inv_key_names:
            return self._inv_key_names[key]
        else:
            return key

    def move_mouse(self, x, y, time=0):
        if time == 0:
            _mc.move(x, -y)

    def set_mouse(self, x, y, time=0, constant=False, res=100):
        y = _yres - y
        if time == 0:
            _mc.position = x, y
        else:
            start_x, start_y = _mc.position
            xdis, ydis = x - start_x, y - start_y
            for i in range(1, res + 1):
                if i != res:
                    _mc.position = start_x + xdis / res * i, start_y + ydis / res * i
                    if constant:
                        sleep(time / res)
                    else:
                        sleep(time)
                else:
                    _mc.position = x, y

    def get_mouse_position(self):
        return _mc.position[0], _yres - _mc.position[1]

    def drag_mouse(self, x, y, button='left', time=0, constant=False, res=100):
        self.press(button)
        self.set_mouse(x, y, time, constant, res)
        self.release(button)

    def press(self, *keys):
        for i in keys:
            i = self._convert_key(i)
            if type(i) == tuple:
                _mc.press(i[1])
            else:
                _kc.press(i)

    def release(self, *keys):
        for i in keys:
            i = self._convert_key(i)
            if type(i) == tuple:
                _mc.release(i[1])
            else:
                _kc.release(i)

    def tap(self, *keys):
        for i in keys:
            self.press(i)
        for i in keys:
            self.release(i)

    def scroll(self, *amount):
        if len(amount) == 1:
            print('hi')
            _mc.scroll(0, amount[0])
        elif len(amount) == 2:
            _mc.scroll(amount[0], amount[1])
        else:
            raise Exception(f'The scroll function takes either one (for vertical scrolling) or two (for vertical and horizontal scrolling) parameters, but {len(amount)} were given.')
