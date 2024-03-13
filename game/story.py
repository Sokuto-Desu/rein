import random
import sys

from helpers import consts
from db import SQL

sql = SQL()

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

def id_choose(window):
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
		window.print_str("В пизду иди, читер ебаный")
		window.show_enter_tip("Нажмите Enter чтобы соснуть хуйца")
		sys.exit()

def world_choose(window, world):
	sql.dict_insert("player_info", "world", world)

def name_choose(window, name):
	sql.dict_insert("player_info", "name", name)

# 2*/ is custom string formatting. see helpers/window.py
start_messages = [
	# i have no idea why but shit doesnt work if you enter a tuple with only string in it (like `('abc',)`)
	# interpreter just starts freaking out, so its only lists despite the poor performance
	["2*/..."],
	["2*/Поздравляем!"],
	[
		f"2*/{predeath_action}. " \
		"Благодаря этому вы получаете возможность переродиться в другом мире " \
		# "(я ебал писать это всё) " \
		"со сверхспособностями и Системой!", 
	],
	["2*/Вы сохраняете все свои воспоминания, личность и опыт прошлой жизни."],
	[
		"2*/Согласны ли вы?",
		0,
		["ДА", "НЕТ"],
		{
			"ДА": ["2/2*/Отлично!"], 
			"НЕТ": [
				"2/2*/Отказ не принимается :-). Ваша душа в любом случае уйдет в другое тело и вы переродитесь, " \
				"однако боги предоставили вам возможность сохранить воспоминания и выбрать место назначения."
			]
		},
		lambda w: id_choose(w) and w.clear()
	],
	[
		"2*/Вы можете выбрать мир для своего перерождения. " \
		"Пожалуйста, выберите:",
		0,
		[world[0] for world in consts.available_worlds],
		world_choose,
		lambda w: w.print_str("\n\n")
	]
]

