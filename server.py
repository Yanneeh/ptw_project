# Flask
from flask import Flask, request, url_for, redirect, render_template, session, jsonify

# Cryptography
from passlib.hash import sha256_crypt

import datetime
import requests

# User libraries
from data import db
from func import predict_restock, is_logged_in, random_key

app = Flask('app')
app.secret_key = 'SECRET'

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

# Dashboard voor
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
					'producten': [],
				}

				producten = db.fetch_data('producten')
				verkoop = db.fetch_data('verkoop')

				for product in producten:
					if product['automaat_id'] == id:

						# print(verkoop)
						#
						# for item in verkoop:

						# records = [
						# 	[0, 3, 2, 3, 4, 1],
						# 	[2, 4, 1, 8, 2, 3],
						# 	[6, 8, 4, 12, 3, 10],
						# 	[4, 6, 7, 3, 6, 6],
						# 	[9, 7, 20, 16, 12, 13],
						# 	[4, 6, 7, 3, 6, 6],
						# 	[4, 6, 7, 3, 6, 6]
						# ]
						# 												#
						# day = datetime.datetime.today().weekday()
						#
						# prediction = predict_restock(records, day, )


						data['producten'].append({
							'id': product['id'],
							'naam': product['naam'],
							'laatst_bijgevuld': product['laatst_bijgevuld'],
							'voorraad': product['stock'],
							'prediction': 'not implemented'
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


@app.route('/stock/update/<int:product_id>/<int:automaat_id>', methods=["POST"])
@is_logged_in
def update_stock(product_id, automaat_id):
	if request.method == "POST":

		print(request.form)

		val = request.form.get('val')
		date = datetime.date.today()

		db.execute_cmd(f"UPDATE producten SET stock='{val}', laatst_bijgevuld='{date}' WHERE id='{product_id}';")

		db.commit_execution()

		return redirect(url_for('automaat', id=automaat_id))

@app.route('/checkout', methods=["POST"])
def checkout():
	if request.method == "POST":
		data = request.get_json()

		# INPUT:
		# Product id, automaat id, API KEY

		id = data['id']
		api_key = data['api_key']

		return {'status': 'succes'}

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('login'))

app.run(host='0.0.0.0', debug=True, port=8080)
