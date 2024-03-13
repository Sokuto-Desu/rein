import sqlite3

from os import getcwd

class SQL:
	def __init__(self, db_path: str="/db/data/main.db"):
		self.db_path = getcwd() + db_path
	
	def execute(self, sql: str):
		with sqlite3.connect(self.db_path) as connection:
			cursor = connection.cursor()
			cursor.execute(sql)
			return cursor
	
	def dict_create(self, table_name: str):
		self.execute(
			f"""
			CREATE TABLE IF NOT EXISTS {table_name} (
				key TEXT UNIQUE,
				value TEXT
			)
			"""
		)
		return True
	
	def dict_insert(self, table_name: str, key_or_dict, value=None):
		if not isinstance(key_or_dict, dict):
			if value == None:
				raise BadArgumentError("Nuh uh")
			sql_values = f'("{key_or_dict}", "{value}")'
		else:
			sql_values = ""
			for key, value in key_or_dict.items():
				sql_values += f'("{key}", "{value}"),'
			# removes last comma
			sql_values = sql_values[:-1]
		
		try:
			self.execute(
				f"""
				INSERT INTO {table_name}
					(key, value)
				VALUES
					{sql_values}
				"""
			)
		except sqlite3.IntegrityError:
			self.execute(
				f"""
				DELETE FROM {table_name}
				"""
			)
			return "TRUNCATED"
		
		return True
	
	def dict_select_one(self, table_name: str, where=None):
		return self.raw_dict_select(table_name, where).fetchone()
	
	def dict_select_all(self, table_name: str, where=None):
		return self.raw_dict_select(table_name, where).fetchall()
	
	def raw_dict_select(self, table_name: str, where=None):
		sql_where = f" WHERE {where}" if where else ""
		
		return self.execute(
			f"""
			SELECT *
			FROM {table_name}{sql_where}
			"""
		)
	