import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'yannimonamour'

app.config['MYSQL_HOST'] = 'us-cdbr-east-06.cleardb.net'
app.config['MYSQL_USER'] = 'bee0c3b95e7998'
app.config['MYSQL_PASSWORD'] = 'c6cd756e'
app.config['MYSQL_DB'] = 'heroku_95979b18166eb20'

mysql = MySQL(app)

# create tables
def create_tables():
    conn = MySQLdb.connect(host='us-cdbr-east-06.cleardb.net', user='bee0c3b95e7998', password='c6cd756e', database='heroku_95979b18166eb20')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE `tablelog` (`id` int(11) NOT NULL AUTO_INCREMENT,`username` varchar(50) NOT NULL,`password` varchar(255) NOT NULL,`email` varchar(100) NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3")
    conn.commit()
    conn.close()
model = pickle.load(open('model.pkl', 'rb'))
@app.route("/")

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM tablelog WHERE username = % s AND password = % s', (username, password, ))
		log = cursor.fetchone()
		if log:
			session['loggedin'] = True
			session['id'] = log['id']
			session['username'] = log['username']
			msg = 'Logged in successfully !'
			return render_template('form.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))
@app.route('/about', methods =['GET', 'POST'])
def about():
   return render_template('about.html')
@app.route('/home', methods =['GET', 'POST'])
def home():
   return render_template('about.html')
@app.route('/home', methods =['GET', 'POST'])
def help():
   return render_template('help.html')


@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'password2' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		password2 = request.form['password2']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM tablelog WHERE username = % s OR email = % s', (username, email))
		log = cursor.fetchone()
		if log:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only letters and numbers !'
		elif not username or not password or not password2 or not email:
			msg = 'Please fill out the form !'
		elif (len(password)<8):
			msg = 'password should be minimum 8 characters.'
		elif not re.search("[a-z]", password):
			msg = 'Password must contain uppercase and lowercase letter'
		elif not re.search("[A-Z]", password):	
			msg = 'Password must contain at least one capital letter'
		elif not re.search("[0-9]", password):
			msg = 'Password must contain at least one number'
		elif not re.search("[!\#$%&/?@}]", password):
		#elif not re.search("[_@$]", password):
			msg = 'Password must contain a special character'
		elif request.form['password'] != request.form['password2']:
			msg=('Passwords don\'t match.')
		else:
			cursor.execute('INSERT INTO tablelog VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)
# def hello():
#     return render_template('form.html')

@app.route("/predict", methods=['POST'])
def predict():
    sex = int(request.form['sex'])
    age = int(request.form['age'])
    height = int(request.form['height'])
    weight = int(request.form['weight'])
    systolic= int(request.form['systolic'])
    diastolic= int(request.form['diastolic'])
    hr = int(request.form['hr'])
    bmi = float(request.form['bmi'])
    prediction = model.predict([[sex, age, height, weight, systolic, diastolic, hr,bmi]])
    output = round(prediction[0], 2)
    if (prediction[0] == 0):
         prediction = "Normal"
    elif(prediction[0] == 1):
         prediction = "Prehypertension - Please be carefull and talk to your provider about your result"
    elif(prediction[0] == 2):
         prediction = " abnormal - Hypertension stage 1 - Please talk to your provider about your result"
    else:
         prediction = "abnormal - Hypertension stage 2 - Please talk to your provider about your result"

    return render_template('form.html', prediction_text=f'This is your report: You are {age} year-old, you are {height} cm tall, you weight {weight} kg, your blood presure is {systolic}/{diastolic} mmHg, Your heart rate is {hr} b/m, your body mass is {bmi} kg/m².  your result is: {prediction}')
	

 
if __name__ == '__main__':
    app.run()