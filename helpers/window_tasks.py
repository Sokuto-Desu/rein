import re

from typing import FunctionType
from .window import Window


class WindowTasks:
	def __init__(self, window: Window):
		self.window = window
	
	def execute_task(self, task: list | dict):
		"""Executes a task given in a list or a dict, depending on do you want to use keyword arguments or not.
		
		Args:
			string: The string that will be printed. 
					Always printed first unless not provided (None).
			wait_after_str: Time to wait after printing the string. 
					0 to not wait.
			select: A tuple or list of options. 
					None to skip.
			task_after_select: Either a dictionary of user's selection and arguments for this method 
					or a function that takes Window and str (selected option) as arguments. 
					Will be executed after user's selection (see `select`). None to skip. 
			final: a function that takes Window as an argument and will be executed in the (almost) very end of current task.
					None to skip.
			wait_for_enter: Amount of actions to wait until displaying the tip for enter. 
					None to not wait for user's input.
			newline_amount: Amount of newlines at the end of the string to set.
					0 to not set any newlines.
		Returns:
			Selected option if `select` is provided. Else nothing.
		"""
		if isinstance(task, dict):
			return self.raw_execute_task(**task)
		else:
			return self.raw_execute_task(*task)
	
	def raw_execute_task(
		self, 
		string: str = None, 
		wait_after_str: int | float = 0, 
		select: tuple | list = None, 
		task_after_select: dict | FunctionType = None,
		final: FunctionType = None,
		wait_for_enter: int | float = 1,
		newline_amount: int = 1
	):
		if not any((string, select, final)):
			return 
		
		if string:
			attribute = None
			
			start, end, formatted_string, attribute = self.format_string(string)
			
			result = start + formatted_string + end
			
			self.window.print_str(result, attr=attribute)
		
		time.sleep(wait_after_str)
		
		if select:
			wait_for_enter = None
			selected_option = self.window.make_option_select(select)
			
			if task_after_select:
				if callable(task_after_select):
					return_value = task_after_select(self.window, selected_option)
				else:
					task_option = task_after_select.get(selected_option)
					return_value = self.execute_task(task_option)
			else:
				return_value = selected_option
			
			if final:
				final(self.window)
			return return_value
		
		if final:
			final(self.window)
		
		if wait_for_enter:
			self.window.show_enter_tip(wait_actions=wait_for_enter)
	
	def format_string(self, string):
		start_newline_amount = 0
		if re.search(r"^\d\/\d.\/", string):
			start_newline_amount = int(string[0])
			string = string[2:]
		
		end_newline_amount = 0
		# searches for a digit in the beginning of the string
		if re.search(r"^\d.\/", string):
			end_newline_amount = int(string[0])
			string = string[1:]
		
		attribute = None
		# searches for a character and / in the beginning of the string
		if re.search(r"^.\/", string):
			attribute = self._check_formatting(string)
			string = string[2:]
		
		start_newlines = "\n" * start_newline_amount
		end_newlines = "\n" * end_newline_amount
		
		return start_newlines, end_newlines, string, attribute
	
	def _check_formatting(self, string):
		if string.startswith("*/"):
			return "bold"
		elif string.startswith("+/"):
			return "standout"
		elif string.startswith("-/"):
			return "dim"
		elif string.startswith(">/"):
			return "reverse"
		elif string.startswith("_/"):
			return "underline"
		else:
			print(f'Wrong string formatting: "{string}"\nString left unformatted.')
			return None
