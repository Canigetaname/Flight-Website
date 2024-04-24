
from flask import Flask, render_template, request, redirect, url_for
from models import User, Booking, Airport

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/airports')
def airports():
    airports = Airport.query.all()
    return render_template('airports.html', airports=airports)

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/bookings')
def bookings():
    bookings = Booking.query.all()
    return render_template('bookings.html', bookings=bookings)

@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        city = request.form['city']
        country = request.form['country']
        new_airport = Airport(code, name, city, country)
        db.session.add(new_airport)
        db.session.commit()
        return redirect(url_for('airports'))
    return render_template('add_airport.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        new_user = User(username, password, email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('add_user.html')

@app.route('/add_booking', methods=['GET', 'POST'])
def add_booking():
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        passenger_id = request.form
