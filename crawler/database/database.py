import pymysql as mysql
import os

class DB:
	def __init__(self):
		db_info = []
		with open(os.path.dirname(__file__)+"\\database.txt", "r") as db:
			for _ in range(4):
				db_info.append(db.readline().strip())

		try:
			self.conn = mysql.connect(host=db_info[0], user=db_info[1], password=db_info[2], db=db_info[3], charset='utf8')
			self.handler = self.conn.cursor()
		except Exception as e:
			print("DB connect:", e)

	def get(self):
		return self.handler

	def select(self, query, params=()):
		try:
			self.handler.execute(query, params)
			result = self.handler.fetchall()
		except Exception as e:
			return False, e

		return True, result

	def insert(self, query, params=()):
		try:
			self.handler.execute(query, params)
			self.conn.commit()
		except Exception as e:
			return False, e

		return True, ""

	def delete(self, query, params=()):
		try:
			self.handler.execute(query, params)
			self.conn.commit()
		except Exception as e:
			return False, e

		return True, ""

	def close(self):
		self.conn.close()