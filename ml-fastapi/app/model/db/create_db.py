import sqlite3

def main():
	connection = sqlite3.connect('magnitogorsk.db')
	cursor = connection.cursor()
	cursor.execute("""
		CREATE TABLE offers (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			type TEXT,
			district TEXT,
			adress TEXT,
			floor TEXT,
			total_square REAL,
			living_square REAL,
			kitchen_square REAL, 
			price INTEGER
			)
		""")
	connection.close()

if __name__ == '__main__':
	main()