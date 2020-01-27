import re
from functools import wraps
from flask import session
import random
import string

# Check if 'logged_in' is in session. If so, the user is logged in by the server.
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('login'), 302, {'status': {'error': 'Please log in'}})
	return wrap

def avg(lst):
	# Retourneert het afgeronde gemiddelde van een lijst.
	if len(lst) > 0:
		return int(sum(lst) / len(lst))
	return 0

def random_key(stringLength=6):
	"""Generate a random string of letters and digits """
	lettersAndDigits = string.ascii_letters + string.digits
	return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


def predict_restock(records, day, stock):

	"""
	Input:
		Records:
			Beschrijving:
				Verkoopcijfers van een product, gesorteerd per dag.
				Waar index 0 maandag betekent, dinsdag index 1 enz. tot zondag index 6.

			Datatype: list (2d).

			Voorbeeld:
				[[2, 4, 6], [2, 5, 1], ... , [1, 4, 6]]

		Day:
			Beschrijving:
				Het nummer van de huidige dag. Waar index 0 maandag betekent, dinsdag index 1 enz. tot zondag index 6.

			Datatype: int.

		Stock:
			Beschrijving:
				Hoeveelheid producten op dit moment aanwezig is in het apparaat.

			Datatype: int.

	Output:
		Return type: tuple.

		Return values:
			index 0:
				Beschrijving:
					De dag van de week dat een product bijgevuld moet worden.

				Datatype: int

			index 1:
				Beschrijving:
					Het aantal weken in de toekomst dat product bijgevuld moet worden.

				Datatype: int.

			index 2:
				Beschrijving:
					De hoeveelheid producten die nog in de automaat zitten met bijvullen.

				Datatype: int.

		Voorbeeld:
			(4, 0, 2)

			index 0: Bijvullen op vrijdag.
			index 1: Bijvullen in huidige week.
			index 2: Twee producten over in de automaat

	"""

	week = 0

	while (stock - avg(records[day])) >= 0:

		if day == len(records) -1:
			stock -= avg(records[day])

			day = 0
			week += 1
		else:
			stock -= avg(records[day])

			day += 1


	return (day-1), week, stock

#---------- Examples ----------#

# records = [
#     [0, 3, 2, 3, 4, 1],
#     [2, 4, 1, 8, 2, 3],
#     [6, 8, 4, 12, 3, 10],
#     [4, 6, 7, 3, 6, 6],
#     [9, 7, 20, 16, 12, 13],
#     [4, 6, 7, 3, 6, 6],
#     [4, 6, 7, 3, 6, 6],
# ]
#
# import datetime
#
# day = datetime.datetime.today().weekday()
#
# print(predict_restock(records, day, 100))
