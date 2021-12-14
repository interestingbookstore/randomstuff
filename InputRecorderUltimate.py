from pynput import mouse, keyboard
from pynput.mouse import Button, Controller
from time import perf_counter, sleep

# Made by interestingbookstore
# Github: https://github.com/interestingbookstore/randomstuff
# -----------------------------------------------------------------------
# Version released on December 13 2021
# ---------------------------------------------------------

m = Controller()

class InputRecorder:
	def __init__(self):
		self.inputs = []
		self._input_mode = 'normal'
		self._t1 = None
		self._previous_pos = None
	
	def record(self):
		self.inputs.clear()

		self._t1 = perf_counter()
		self._previous_pos = 0, 0
		def on_move(x, y):
			t = perf_counter()
			self.inputs.append((t - self._t1, 'm', (x - self._previous_pos[0], y - self._previous_pos[1])))
			self._t1 = t
			self._previous_pos = x, y
		
		def on_click(x, y, button, pressed):
			# the x and y coordinates seem to already be handled by on_move, so they can just be ignored here
			t = perf_counter()
			self.inputs.append((t - self._t1, 'l' if button == Button.left else 'r', 'down' if pressed else 'up'))
			self._t1 = t
		
		def on_press(key):  # If escape is pressed, stop the listeners
			if key == keyboard.Key.esc:
				mouse_listener.stop()
				keyboard_listener.stop()
		
		with mouse.Listener(on_move=on_move, on_click=on_click) as mouse_listener, keyboard.Listener(on_press=on_press) as keyboard_listener:
			mouse_listener.join()
			keyboard_listener.join()
	
	def play(self, fast_mode=None, fast_mode_release_delay=0.02):
		#  fast_mode: If not set to a float value, ignores the individial mouse movements and timings and simply teleports the mouse around with a fixed delay, which is defined by this value.
		#  fast_mode_release_delay specifies the (typically) brief period between a mouse button being pressed and it being released, which might be neccessary for some interactions to register.
		#     Note, fast mode doesn't support holding down a mouse button. It simply taps the button whenever it should press it down.

		if self._input_mode == 'fast' and not fast_mode:
			raise Exception('Fast Mode is kept is kept disabled, but loaded recording only contains data for fast mode.')

		first_mouse_movement = True
		if not fast_mode:
			for (delay, input_type, info) in self.inputs:
				sleep(delay)
				if input_type == 'm':
					if first_mouse_movement:
						m.position = info
						first_mouse_movement = False
					else:
						m.move(info[0], info[1])
				elif input_type == 'l':
					if info == 'down':
						m.press(Button.left)
					elif info == 'up':
						m.release(Button.left)
					else:
						raise Exception('Invalid mouse action given')
				elif input_type == 'r':
					if info == 'down':
						m.press(Button.right)
					elif info == 'up':
						m.release(Button.right)
					else:
						raise Exception('Invalid mouse action given')
		else:
			if self._input_mode == 'normal':
				i2 = []
				mouse_pos = [0, 0]
				for (delay, input_type, info) in self.inputs:
					if input_type == 'm':
						mouse_pos[0] += info[0]
						mouse_pos[1] += info[1]
					elif info == 'down':
						i2.append((input_type, tuple(mouse_pos)))
			else:
				i2 = self.inputs
			for index, (button, pos) in enumerate(i2):
				if first_mouse_movement:
					print(f'pos: {pos}')
					m.position = pos
					first_mouse_movement = False
				else:
					m.move(pos[0], pos[1])
				if index != len(i2) - 1:
					sleep(fast_mode)
				m.press(Button.left if button == 'l' else Button.right)
				sleep(fast_mode_release_delay)
				m.release(Button.left if button == 'l' else Button.right)

	
	def save(self, filename, save_for_fast_mode=False, shorten=None):
		# filename: name of file (or path to file), no extension at the end
		# shorten: Whether or not the delays should be rounded. False if not, otherwise an integer defining how many digits after the decimal point to include.
		with open(f'{filename + ("" if filename.endswith(".inrec") else ".inrec")}', 'w') as f:
			i2 = []
			if not save_for_fast_mode:
				for (delay, input_type, info) in self.inputs:
					i2.append(f"""{round(delay, shorten) if shorten is not None else delay} {input_type} {str(info).strip('()').replace("'", '').replace(',', '')}""")
			else:
				mouse_pos = [0, 0]
				for (delay, input_type, info) in self.inputs:
					if input_type == 'm':
						mouse_pos[0] += info[0]
						mouse_pos[1] += info[1]
					elif info == 'down':
						i2.append((f'{input_type} {mouse_pos[0]} {mouse_pos[1]}'))
						mouse_pos = [0, 0]

			f.writelines('\n'.join(i2))
	
	def load(self, filename):
		# TODO: Add better file format checking
		self.inputs.clear()
		with open(f'{filename + ("" if filename.endswith(".inrec") else ".inrec")}') as f:
			t = f.read().split('\n')
			if t[0].isdigit():  # If it's in "normal" mode
				self._input_mode = 'normal'
				for line in t:
					delay, input_type, info = line.split(' ', 2)
					if input_type == 'm':
						info = tuple(int(i) for i in info.split(' '))
					self.inputs.append((float(delay), input_type, info))
			else:
				self._input_mode = 'fast'
				for line in t:
					button, pos = line.split(' ', 1)
					pos = pos.split(' ')
					print(f'Button pos: {button} {pos}')
					self.inputs.append((button, (int(pos[0]), int(pos[1]))))
