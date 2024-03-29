import curses
import story

from handlers import Window, WindowTasks
from sys import argv


class Reincarnation:
	def start(self):
		curses.wrapper(self._redirect)
	
	def _redirect(self, stdscr):
		self.window = Window(stdscr)
		self.wintasks = WindowTasks(self.window)
		self._main()
	
	def _main(self):
		if "-d" in argv:
			start_messages = [("debug", 1)]
		else:
			start_messages = story.start_messages
		
		self.window.clear()
		
		for message in start_messages:
			self.wintasks.execute_task(message)
		
		while True:
			self.window.get_key()
