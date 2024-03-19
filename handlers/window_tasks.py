import re
import time

from types import FunctionType
from .window import Window
from helpers import consts


class WindowTasks:
	def __init__(self, window: Window):
		self.window = window
	
	def execute_task(self, task: list | dict):
		"""Executes a task given in a list or a dict, depending on do you want to use keyword arguments or not.
		
		Args:
			string: The string that will be printed. 
					Every string is printed gradually unless print_speed as 0 is provided.
					Always printed first unless not provided (None).
			select: A list of options. Do not use a tuple.
					None to skip.
			task_after_select: Either a dictionary of user's selection and arguments for this method 
					or a function that takes Window and str (selected option) as arguments. 
					Will be executed after user's selection (see `select`). 
					None to skip. 
			final: A function that takes Window as an argument 
					and will be executed in the (almost) very end of current task.
					None to skip.
			formatting: Formatting for the string. 
					Follows this pattern: 
						(n)(m)(w/b)eX/
					where 
						n is the amount of newlines at the end
						m is the amount of newlines at the start 
						w is the seconds to wait after select and final function
						b is the seconds to wait before select
						e is the amount of actions to wait until displaying enter tip 
						X is the attribute (see `_check_formatting`).
					Parentheses are optional for n, m, and e, with some exceptions. See comments for `format_string` for more info.
					Formatting can be put at the beginning of `string`. 
					Usually more convenient, but you still can pass a parameter.
			print_speed: The speed of printing text.
					0 to print immediately.
			enter_tip: A string that will be used when displaying enter tip.
		Returns:
			Selected option or return value of task_after_select if `select` is provided. Else nothing.
		"""
		if isinstance(task, dict):
			return self.raw_execute_task(**task)
		elif isinstance(task, str):
			return self.raw_execute_task(string=task)
		else:
			if not all(
				isinstance(string, str)
				for string in task
			):
				return self.raw_execute_task(*task)
			else:
				for string in task:
					self.raw_execute_task(string=string)
	
	def raw_execute_task(
		self, 
		string: str = None, 
		select: list = None, 
		task_after_select: dict | FunctionType = None,
		final: FunctionType = None,
		formatting: str = "",
		print_speed: int = 30,
		enter_tip: str = "Нажмите Enter чтобы продолжить"
	):
		if not any((string, select, final)):
			return 
		
		# if any sign of formatting crap in `string`
		if in_str_formatting := re.search("[0-9/()]*[_>+.*-]*\/", string):
			formatting = in_str_formatting.group()
			# deletes the formatting part
			string = string[len(formatting):]
		
		# for loop is used to break out of if condition without interrupting the whole function
		for _ in [0]:
			if string:
				# in case string is multilined
				if "\n" in string:
					strings = string.split("\n")
					
					for task in strings:
						task = task.strip("\t")
						self.execute_task(task)
					
					format_attrs = self.format_string(formatting)
					
					continue
				
				format_attrs = self.format_string(formatting)
				
				start = format_attrs.get("start_newlines")
				end = format_attrs.get("end_newlines")
				formatted_string = start + string + end
				
				# waits for the user input (30 ms by default) and proceeds
				self.window.timeout(print_speed)
				
				pressed_enter = False
				
				# prints out every character in the string
				for character in formatted_string:
					attribute = format_attrs.get("attribute")
					self.window.print_str(character, attr=attribute)
					
					if not pressed_enter:
						key = self.window.get_key()
						if key in consts.next:
							pressed_enter = True
				
				# sets the default delay for get_key()
				self.window.timeout(-1)
		
		enter_actions = format_attrs.get("enter_actions")
		
		if select:
			enter_actions = None
			
			wait_before_select = format_attrs.get("wait_before_select")
			time.sleep(wait_before_select)
			
			selected_option = self.window.make_option_select(select)
			
			if not task_after_select:
				return_value = selected_option
			else:
				# if its a function call it
				if callable(task_after_select):
					return_value = task_after_select(self.window, self, selected_option)
				# if a dict get selected option from it and execute
				elif isinstance(task_after_select, dict):
					task_args = task_after_select.get(selected_option)
					return_value = self.execute_task(task_args)
				else:
					raise ValueError("No idea what u doin here: " + task_after_select)
			
			if final:
				final(self.window, self)
			
			return return_value
		
		# "if final: ..." is repeated because in "if select: ..." there is a return
		if final:
			final(self.window, self)
		
		wait_final = format_attrs.get("wait_final")
		time.sleep(wait_final)
		
		if enter_actions:
			self.window.wait_for_enter(string=enter_tip, wait_actions=enter_actions)
	
	def format_string(self, string) -> dict:
		start_newline_amount = 0
		end_newline_amount = 0
		wait_before_select = 0.2
		wait_final = 0
		enter_actions = 2
		attribute = None
		
		# format example: 3
		# should only be one number 
		if newline_numbers := re.search(r"^((?!\()\d(?!\))(?!\d))", string):
			newline_numbers = newline_numbers.group()
			
			start_newline_amount = int(newline_numbers[0])
			
			numbers_len = len(newline_numbers)
			string = string[numbers_len:]
		# format example: 12
		# should only be two numbers, both have separate meanings
		elif newline_numbers := re.search(r"^(\d\d)", string):
			newline_numbers = newline_numbers.group()
			
			start_newline_amount = int(newline_numbers[0])
			end_newline_amount = int(newline_numbers[1])
			
			numbers_len = len(newline_numbers)
			string = string[numbers_len:]
		# format examples: (1)(234), (23)(1)
		# should always be enclosed with parentheses
		# note: this finds ALL occurences of newline numbers and considers only first two
		# singular ones are above
		elif newline_numbers := re.findall(r"(\(\d+\))", string):
			stripped_end = newline_numbers[0].strip("()")
			stripped_start = newline_numbers[1].strip("()")
			
			end_newline_amount = int(stripped_end)
			start_newline_amount = int(stripped_start)
			
			numbers_len = len("".join(newline_numbers))
			string = string[numbers_len:]
		else:
			# see matched_enter_number
			numbers_len = 5
		
		# format examples: (2.45/3), (9/1.5), (300.5/2350.25)
		# should always be enclosed with parentheses
		if wait_numbers := re.search(r"\((\d+(\.\d+)?)/(\d+(\.\d+)?)\)", string):
			wait_numbers = wait_numbers.group().strip("()")
			splitted_wait_numbers = wait_numbers.split("/")
			
			# yes, first number is final wait time and second is before selection 
			# sorry, its just more convenient ¯\_(ツ)_/¯
			wait_final = float(splitted_wait_numbers[0])
			wait_before_select = float(splitted_wait_numbers[1])
		
		# format example: 3, (2)
		# does not support two, three and etc digit numbers
		# should be put right before attribute
		if matched_enter_number := re.findall(r"\(?\d\)?", string):
			# checks if there is only newline numbers in the string
			# (i dont understand it myself i just know what does it do)
			if not (
				(len(matched_enter_number) <= 2 and numbers_len <= 4) or
				(len(re.findall(r"(\(\d+\))", string)) <= 2)
			):
				enter_actions = int(matched_enter_number[-1])
			else:
				pass
		
		# searches for a non-word character (and _) and /
		# format examples: */, _/, (+/)
		# should be put at the very end
		if matched_attr := re.search(r"(\(?[*_>+-]|_\)?\/)", string):
			attribute = self._check_formatting(matched_attr.group())
		
		start_newlines = "\n" * start_newline_amount
		end_newlines = "\n" * end_newline_amount
		
		return {
			"start_newlines": start_newlines, 
			"end_newlines": end_newlines, 
			"wait_final": wait_final,
			"wait_before_select": wait_before_select,
			"enter_actions": enter_actions, 
			"attribute": attribute
		}
	
	def _check_formatting(self, string):
		if "*" in string:
			return "bold"
		elif "+" in string:
			return "standout"
		elif "-" in string:
			return "dim"
		elif ">" in string:
			return "reverse"
		elif "_" in string:
			return "underline"
		else:
			self.window.print_str(f'\n\nWrong string formatting: "{string}"\nString left unformatted.\n\n')
			return None
