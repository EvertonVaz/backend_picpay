import sqlite3

def get_db_connection():
	with sqlite3.connect("../picpay.db") as conn:
		conn.row_factory = sqlite3.Row
		yield conn

conn = next(get_db_connection())

def create_user_table():
	if conn is None:
		return
	cursor = conn.cursor()
	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			full_name TEXT NOT NULL,
			email TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL,
			user_type TEXT NOT NULL,
			document TEXT NOT NULL UNIQUE,
			balance REAL NOT NULL
		)
		"""
	)
	conn.commit()

def create_transaction_table():
	if conn is None:
		return
	cursor = conn.cursor()
	cursor.execute(
		"""
		CREATE TABLE IF NOT EXISTS transactions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			payer_id INTEGER NOT NULL,
			payee_id INTEGER NOT NULL,
			value REAL NOT NULL,
			status TEXT NOT NULL,
			created_at TEXT NOT NULL
		)
		"""
	)
	conn.commit()

if __name__ == "__main__":
	create_transaction_table()
	create_user_table()
