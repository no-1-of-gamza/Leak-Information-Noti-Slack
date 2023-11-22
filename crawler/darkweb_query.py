import sys

from database.database import DB

db = DB()


def check_initialization():
	try:
		query = "SELECT * FROM last_scan ORDER BY scan_time DESC LIMIT 1;"
		result, rows = db.select(query)
		if not result:
			raise Exception(rows)
	except Exception as e:
		return False, e
	return True, rows

def insert_pending(data):
	params = (data["domain"], data["url"], data["remain_time"], data["deadline"], data["description"], data["uploaded_date"], data["updated_date"])

	try:
		query = "INSERT INTO pending(domain, url, remain_time, deadline, description, uploaded_date, updated_date) VALUES (%s, %s, %s, %s, %s, %s, %s);"
		result, err = db.insert(query, params)
		if not result:
			raise Exception(err)
	except Exception as e:
		return False, e

	return True, ""

def update_last_scan(last_domain):
	try:
		query = "INSERT INTO last_scan(domain) VALUES (%s);"
		params = (last_domain)
		result, err = db.insert(query, params)
		if not result:
			raise Exception(err)
	except Exception as e:
		return False, e

	return True, ""

def select_all_pending():
	try:
		query = "SELECT * FROM pending ORDER BY uploaded_date DESC;"
		result, rows = db.select(query)
		if not result:
			raise Exception(rows)
	except Exception as e:
		return False, e
	return True, rows

def delete_post(domain) -> bool:
	try:
		query = "DELETE FROM pending WHERE domain=%s"
		result, err = db.delete(query, (domain))
		if not result:
			raise Exception(err)
	except Exception as e:
		return False, e
	return True, err

def db_close():
	db.close()
