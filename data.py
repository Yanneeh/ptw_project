import psycopg2

class Database:
	"""
		A wrapper for the psycopg2 library for easy accesing a database.
		The database will connect in the constructor.
	"""
	def __init__(self, host, db, user, password, port=5432):
		self.connection = None
		try:
			print('\n')
			# connect to the PostgreSQL server
			print('Connecting to the PostgreSQL database... \n')
			self.connection = psycopg2.connect(
				host=host,
				database=db,
				user=user,
				password=password,
				port=port)

			# create a cursor
			cur = self.connection.cursor()

			# execute a statement
			print('PostgreSQL database version:')
			cur.execute('SELECT version();')

			# display the PostgreSQL database server version
			db_version = cur.fetchone()
			print(db_version[0])
			print('\n')

			# close the communication with the PostgreSQL
			cur.close()

		except (Exception, psycopg2.DatabaseError) as error:
			print(error)

	# Execute command on database.
	def execute_cmd(self, command):
		try:
			if self.connection is not None:
				# create a cursor
				cur = self.connection.cursor()

				print('Executing command... \n')
				# execute a statement
				cur.execute(command)

				# close the communication with the PostgreSQL
				cur.close()

		except(Exception, psycopg2.DatabaseError) as error:
			print(error)

	def fetch_data(self, table):
		try:
			if self.connection is not None:
				colums = []

				with self.connection.cursor() as cur:
					cur.execute("""SELECT column_name FROM information_schema.columns WHERE table_name = '{}'""".format(table))
					columns = [row[0] for row in cur]
					cur.close()

				results = []

				with self.connection.cursor() as cur:

					print('Executing command... \n')
					cur.execute(f'SELECT * FROM {table};')

					for record in cur.fetchall():
						# print(record)
						results.append(dict(zip(columns, record)))

					cur.close()

				# return data in dict format.
				return results

		except(Exception, psycopg2.DatabaseError) as error:
			print(error)

	def close_connection(self):
		try:
			if self.connection is not None:
				self.connection.close()
				self.connection = None
				print('Database connection closed.')
		except(Exception, psycopg2.DatabaseError) as error:
			print(error)

	def commit_execution(self):
		try:
			if self.connection is not None:
				print('Committing to database... \n')
				self.connection.commit()
		except(Exception, psycopg2.DatabaseError) as error:
			print(error)

#--------- Database setup ---------#

<<<<<<< HEAD
db = Database('localhost', 'postgres', 'postgres', 'Y=c@2002')
=======
db = Database('localhost', 'automaat_systeem', 'yannick', '')
>>>>>>> ef8bcc0631e87fcc569985ffed62b6a0c56c4e58


#----------- Examples -----------#

# naam = 'yannick'
# email = 'yvandiermen@gmail.com'
# wachtwoord = 'test123'

# db.execute_cmd(f"INSERT INTO beheerders (naam, email, wachtwoord) VALUES ('{naam}', '{email}', '{wachtwoord}');")

# data = db.fetch_data('beheerders')

# print(data)



# db.commit_execution()
