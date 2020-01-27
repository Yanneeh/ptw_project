# Flask
from flask import Flask, request, url_for, redirect, render_template, session, jsonify, abort

# Cryptography
from passlib.hash import sha256_crypt

import datetime
from pprint import pprint

# User libraries
from data import db
from func import predict_restock, is_logged_in, random_key

app = Flask('app')
app.secret_key = 'SECRET' # Verander dit!!!

# Landing page
@app.route('/')
def index():
	if session.get('logged_in'):
		return redirect(url_for('dashboard'))
	return render_template('index.html')


# Inloggen
@app.route('/login', methods=["GET", "POST"])
def login():
	if request.method == "POST":

		users = db.fetch_data('beheerders')

		print(users)

		for user in users:
			if request.form.get('email') == user['email']:
				if request.form.get('password') == user['wachtwoord']:

					session['logged_in'] = True
					session['id'] = user['id']
					session['naam'] = user['naam']

					return redirect(url_for('dashboard'))

		err = 'Email of wachtwoord onjuist.'
		return render_template('login.html', err=err)
	else:
		return render_template('login.html')

# Dashboard voor alle automaten
@app.route('/dashboard')
@is_logged_in
def dashboard():

	data = []

	automaten = db.fetch_data('automaten')

	for automaat in automaten:
		if automaat['beheerder_id'] == session['id']:
			data.append({
				'id': automaat['id'],
				'naam': automaat['naam'],
				'locatie': automaat['locatie'],
				'api_key': automaat['api_key']
			})

	return render_template('dashboard.html', data=data)

# Specifiek automaat
@app.route('/automaat/<int:id>')
@is_logged_in
def automaat(id):

	automaten = db.fetch_data('automaten')

	for automaat in automaten:
		if automaat['id'] == id:
			if automaat['beheerder_id'] == session['id']:
				data = {
					'id': automaat['id'],
					'naam': automaat['naam'],
					'locatie': automaat['locatie'],
					'api_key': automaat['api_key'],
					'producten': []
				}

				producten = db.fetch_data('producten')
				verkoop = db.fetch_data('verkoop')

				for product in producten:

					if product['automaat_id'] == id:

						records = [[], [], [], [], [], [], []]

						for item in verkoop:

							if item['product_id'] == product['id']:
								# print(item)

								records[item['dag_nummer']].append(int(item['aantal']))

						for record in records:
							if len(record) == 0:
								records = [
								    [0, 3, 2, 3, 4, 1],
								    [2, 4, 1, 8, 2, 3],
								    [6, 8, 4, 12, 3, 10],
								    [4, 6, 7, 3, 6, 6],
								    [9, 7, 20, 16, 12, 13],
								    [4, 6, 7, 3, 6, 6],
								    [4, 6, 7, 3, 6, 6],
								]

						# pprint(records)

						day = datetime.datetime.today().weekday()

						prediction = predict_restock(records, day, product['stock'])

						if prediction[0] == 0:
							prediction = f"maandag over {prediction[1]} weken"

						if prediction[0] == 1:
							prediction = f"dinsdag over {prediction[1]} weken"

						if prediction[0] == 2:
							prediction = f"woensdag over {prediction[1]} weken"

						if prediction[0] == 3:
							prediction = f"donderdag over {prediction[1]} weken"

						if prediction[0] == 4:
							prediction = f"vrijdag over {prediction[1]} weken"

						if prediction[0] == 5:
							prediction = f"zaterdag over {prediction[1]} weken"

						if prediction[0] == 6:
							prediction = f"zondag over {prediction[1]} weken"

						data['producten'].append({
							'id': product['id'],
							'naam': product['naam'],
							'laatst_bijgevuld': product['laatst_bijgevuld'],
							'voorraad': product['stock'],
							'prediction': prediction
						})

				return render_template('automaat.html', data=data)

	return abort(401)

# Voeg nieuwe automaat toe aan database.
@app.route('/automaat/new', methods=["POST"])
@is_logged_in
def new_vm():
	if request.method == "POST":

		naam = request.form.get('naam')
		locatie = request.form.get('locatie')
		beheerder_id = session['id']
		api_key = random_key(20)

		db.execute_cmd(f"INSERT INTO automaten (naam, beheerder_id, locatie, api_key) VALUES ('{naam}', '{beheerder_id}', '{locatie}', '{api_key}');")

		db.commit_execution()

		return redirect(url_for('dashboard'))

# Voeg nieuw product toe aan database.
@app.route('/product/new/<int:vm_id>', methods=["POST"])
@is_logged_in
def new_product(vm_id):
	if request.method == "POST":

		naam = request.form.get('naam')
		voorraad = request.form.get('voorraad')
		date = datetime.date.today()

		db.execute_cmd(f"INSERT INTO producten (stock, naam, laatst_bijgevuld, automaat_id) VALUES ('{voorraad}', '{naam}', '{date}', '{vm_id}');")

		db.commit_execution()

		return redirect(url_for('automaat', id=vm_id))

# Update de voorraad van een product.
@app.route('/stock/update/<int:product_id>/<int:automaat_id>', methods=["POST"])
@is_logged_in
def update_stock(product_id, automaat_id):
	if request.method == "POST":

		print(request.form)

		val = request.form.get('val')
		date = datetime.date.today()

		if int(val) < 0:
			val = 0

		db.execute_cmd(f"UPDATE producten SET stock='{val}', laatst_bijgevuld='{date}' WHERE id='{product_id}';")

		db.commit_execution()

		return redirect(url_for('automaat', id=automaat_id))

@app.route('/checkout', methods=["POST"])
def checkout():
	if request.method == "POST":

		# INPUT:
		# Product id, automaat id, API KEY

		product_id = int(request.args.get('product_id'))
		automaat_id = int(request.args.get('automaat_id'))
		api_key = str(request.args.get('API_key'))

		automaten = db.fetch_data('automaten')

		for automaat in automaten:

			# Vind de automaat met meegegeven automaat id.
			if automaat['id'] == automaat_id:

				# Check of de API key die meegegeven is overeenkomt met de API key in de database.
				if automaat['api_key'] == api_key:

					print('authenticated')

					producten = db.fetch_data('producten')

					for product in producten:

						# Vind een product met megegeven product id.
						if product['id'] == product_id:

							val = product['stock'] - 1

							if val < 0:
								val = 0

							db.execute_cmd(f"UPDATE producten SET stock='{val}' WHERE id='{product_id}';")

							verkoop = db.fetch_data('verkoop')
							day = datetime.datetime.today().weekday()
							date = datetime.date.today()

							for item in verkoop:
								if item['product_id'] == product_id:
									if item['datum'] == datetime.date.today():
										print(item)

										stock = item['aantal'] + 1

										db.execute_cmd(f"UPDATE verkoop SET aantal='{stock}' WHERE product_id='{product_id}';")

										db.commit_execution()

										return {'status': 'succes'}

							db.execute_cmd(f"INSERT INTO verkoop (product_id, aantal, dag_nummer, datum) VALUES ('{product_id}', '{1}', '{day}', '{date}');")

							db.commit_execution()

							return {'status': 'succes'}

		return abort(401)
	return abort(404)

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('login'))

app.run(host='0.0.0.0', debug=True, port=8080)
