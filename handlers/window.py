import curses
import re 
import time 

from helpers import consts
from types import FunctionType


class Window:
	def __init__(self, stdscr):
		self.window = stdscr
	
	def update_screen(self):
		self.window.doupdate()
	
	def print_str(self, *args, **kwargs):
		"""Replacement for builtin `curses.window.addstr()`. Refreshes the window immediately after the print.
		Always use this unless for some reason you need `.addstr()`.
		Use `.add_str()` if you need the same method but without the refresh.
		Use `.raw_str()` if you need the same method but with `.noutrefresh()` only.
		
		Args:
			string: The string to print.
			y: The y coordinate of the string. 
				If y is 0, it is at the top of the window.
			x: The x coordinate of the string.
				If x is p, it is at the left of the window.
			attr: The attribute of the string. Should also be a string.
				See add_str for the list of available attributes.
			quick: Whether the cursor should be moved to its initial position after the print.
		"""
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
	
	
	def wait_for_enter(
		self,
		string: str,
		wait_actions: int = 3,
		y: int = None,
		x: int = None
	):
		"""Waits for the press of enter button.
		
		Args;
			string: The string to display if the user does other actions too much.
					"Нажмите Enter чтобы продолжить" by default.
			wait_actions: Amount of actions to wait until displaying the string.
					Enter a negative number to not display the tip at all.
					3 by default.
			y: The y coordinate of the string.
			x: The x coordinate of the string.
		"""
		og_y, og_x = self.get_yx()
		tip_y, _ = self.get_max_yx()
		tip_y = y if y else tip_y
		tip_x = x if x else 1
		
		i = 0
		while True:
			i += 1
			key = self.get_key()
			
			if key in consts.next:
				# clears out the enter tip
				self.window.move(tip_y - 1, tip_x)
				self.window.clrtoeol()
				self.window.move(og_y, og_x)
				break
			elif wait_actions < 0:
				continue
			elif i == wait_actions:
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
	
	def move(self, y: int, x: int):
		self.window.move(y, x)
	
	def timeout(self, delay: int):
		self.window.timeout(delay)
