import random
import sys

from database import SqliteHandler
from helpers import consts

sql = SqliteHandler("data/main.db")

actions = {
	"laugh": "Вы смогли рассмешить самих богов своим способом смерти",
	"dice": "Вы - везунчик! Богам стало скучно, и бросив игральную кость они выбрали именно вас для перерождения"
}
raw_predeath_action = random.choice(
	list(
		actions.items()
	)
)

predeath_action = raw_predeath_action[1]

sql.dict_create("player_info")

def id_choose(window, wintasks):
	unique_id = ""
	for _ in range(10):
		unique_id += str(random.randint(1, 9))
	
	inserted = sql.dict_insert(
		"player_info", 
		{
			"id": unique_id,
			"predeath": raw_predeath_action[0]
		}
	)
	
	if inserted  == "TRUNCATED":
		window.clear()
		wintasks.raw_execute_task(
			"*/В пизду иди, читер ебаный", 
			enter_tip="Нажмите Enter чтобы соснуть хуйца", 
			print_speed=1
		)
		sys.exit()
	
	window.clear()

def world_choose(window, wintasks, world):
	sql.dict_insert("player_info", "world", world)

def name_choose(window, wintasks, name):
	sql.dict_insert("player_info", "name", name)

# "2*/" is custom string formatting. see handlers/window_tasks.py
# note: i have no idea why but crap doesnt work if you enter a tuple with only string in it (like `('abc',)`)
# interpreter just starts freaking out, so do NOT use a tuple if there is only a singular string
# instead pass just a string 
start_messages = (
	"*/...",
	"2*/Поздравляем!",
	f"2*/{predeath_action}.",
	"2*/Благодаря этому вы получаете возможность переродиться в другом мире со сверхспособностями и Системой!",
	# "(я ебал писать это всё) ",
	"2*/Вы сохраняете все свои воспоминания, личность и опыт прошлой жизни.",
	(
		"22*/Согласны ли вы?",
		["ДА", "НЕТ"],
		{
			"ДА": "2*/Отлично!", 
			"НЕТ": (
				"2*/Отказ не принимается :-). ",
				"*/Ваша душа в любом случае уйдет в другое тело и вы переродитесь, однако боги предоставили вам возможность сохранить воспоминания и выбрать место назначения."
			)
		},
		id_choose
	),
	"*/Вы можете выбрать мир для своего перерождения.",
	(
		"12*/Пожалуйста, выберите:",
		[world[0] for world in consts.available_worlds],
		world_choose,
		lambda w, t: w.print_str("\n\n")
	)
)
