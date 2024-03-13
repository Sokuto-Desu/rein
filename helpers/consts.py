import curses

# curses.KEY_ENTER and alternatives
next: tuple = (343, 10, 13)
# curses.KEY_D where D is direction
right: int = 261
left: int = 260
up: int = 259
down: int = 258

bold: int = curses.A_BOLD
underline: int = curses.A_UNDERLINE
dim: int = curses.A_DIM
standout: int = curses.A_STANDOUT
reverse: int = curses.A_REVERSE

available_worlds = (
	("Jujutsu Kaisen", "Магическая битва"),
	("Naruto", "Наруто")
)
