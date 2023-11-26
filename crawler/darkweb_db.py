import pymysql as mysql
import os


class DB:
	def __init__(self):
		db_info = []
		with open(os.getcwd()+"\\crawler\\database\\database.txt", "r") as db:
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
		try:
			self.conn.close()
		except Exception as e:
			return False, e

		return True, ""


def check_initialization(db):
	try:
		query = "SELECT * FROM last_scan ORDER BY scan_time DESC LIMIT 1;"
		result, rows = db.select(query)
		if not result:
			raise Exception(rows)
	except Exception as e:
		return False, e
	return True, rows

def insert_pending(db, data):
	try:
		query = "INSERT INTO pending(domain, url, remain_time, deadline, description, uploaded_date, updated_date) VALUES (%s, %s, %s, %s, %s, %s, %s);"
		params = (data["domain"], data["url"], data["remain_time"], data["deadline"], data["description"], data["uploaded_date"], data["updated_date"])
		result, err = db.insert(query, params)
		if not result:
			raise Exception(err)
	except Exception as e:
		return False, e

	return True, ""

def update_last_scan(db, last_domain):
	try:
		query = "INSERT INTO last_scan(domain) VALUES (%s);"
		params = (last_domain)
		result, err = db.insert(query, params)
		if not result:
			raise Exception(err)
	except Exception as e:
		return False, e

	return True, ""

def select_all_pending(db):
	try:
		query = "SELECT * FROM pending ORDER BY uploaded_date DESC;"
		result, rows = db.select(query)
		if not result:
			raise Exception(rows)
	except Exception as e:
		return False, e
	return True, rows

def delete_post(db, domain):
	try:
		query = "DELETE FROM pending WHERE domain=%s;"
		params = (domain)
		result, err = db.delete(query, params)
		if not result:
			raise Exception(err)
	except Exception as e:
		return False, e
	return True, ""

def db_close(db):
	result, err = db.close()
	if not result:
		return False, err
	return True, ""
