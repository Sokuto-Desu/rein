import curses
import re 
import time 

from . import consts
from types import FunctionType

# note: this code does not use anything from vars.py as it would lead to circular import error
# note 2: nvm

class Window:
	def __init__(self, stdscr):
		self.window = stdscr
	
	def update_screen(self):
		self.window.doupdate()
	
	def print_str(self, *args, **kwargs):
		self.add_str(*args, **kwargs)
		self.window.refresh()
	
	def raw_str(self, *args, **kwargs):
		self.add_str(*args, **kwargs)
		self.window.noutrefresh()
	
	def add_str(
		self, 
		string: str, 
		y: int = None, 
		x: int = None, 
		attr: str = None,
		quick: bool = False
	):
		if quick:
			og_y, og_x = self.get_yx()
		
		attributes = {
			"bold": consts.bold,
			"underline": consts.underline,
			"dim": consts.dim,
			"standout": consts.standout,
			"reverse": consts.reverse
		}
		
		_attr = 0
		if attr:
			_attr = attributes.get(attr.lower())
		
		if y and x:
			self.window.addstr(y, x, string, _attr)
		else:
			self.window.addstr(string, _attr)
		
		if quick:
			self.move(og_y, og_x)
	
	def make_option_select(
		self, 
		options: tuple | list, 
		y: int = None, 
		x: int = None
	):
		selected_row = 0
		
		if not any((y, x)):
			y, x = self.get_yx()
		
		self._print_select(options, selected_row, y, x)
		
		while True:
			key = self.get_key()
			
			if key == consts.up and selected_row > 0:
				selected_row -= 1
			elif key == consts.down and selected_row < len(options) - 1:
				selected_row += 1
			elif key in consts.next:
				break
			
			self._print_select(options, selected_row, y, x)
		
		return options[selected_row]
	
	def _print_select(
		self, 
		options: tuple | list, 
		selected_row: int, 
		y: int, 
		x: int
	):
		for index, row in enumerate(options):
			cy = y + index
			if x == 0:
				cx = 1 
			else:
				cx = x
			
			if index == selected_row:
				self.print_str(row, cy, cx, attr="reverse")
			else:
				self.print_str(row, cy, cx)
	
	
	def show_enter_tip(
		self,
		string: str = "Нажмите Enter чтобы продолжить",
		wait_actions: int = 3,
		y: int = None,
		x: int = None
	):
		i = 0
		og_y, og_x = self.get_yx()
		while True:
			i += 1
			key = self.get_key()
			
			if key in consts.next:
				break 
			elif i == wait_actions:
				tip_y, _ = self.get_max_yx()
				tip_y = y if y else tip_y
				tip_x = x if x else 1
				self.print_str(string, tip_y - 1, tip_x, attr="standout", quick=True)
				self.window.move(og_y, og_x)
	
	def get_yx(self):
		return self.window.getyx()
	
	def get_max_yx(self):
		return self.window.getmaxyx()
	
	def get_key(self):
		curses.flushinp()
		return self.window.getch()
	
	def clear(self):
		self.window.clear()
	
	def move(self, y, x):
		self.window.move(y, x)
