from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import pymysql
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test_website'

db = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    cursorclass=pymysql.cursors.DictCursor
)

flight_seats = {flight_id: [] for flight_id in range(1, 26)}

users={}

with db.cursor() as cursor:
    # Execute the query to fetch user data
    cursor.execute("SELECT * FROM users")

    # Fetch all rows
    user_rows = cursor.fetchall()

    # Populate the 'users' dictionary
    for user_row in user_rows:
        user_id = user_row['user_id']
        users[user_id] = {
            'password_hash': user_row['password_hash'],
            'username': user_row['username'],
            'email': user_row['email'],
            'contact_number': user_row['contact_number'],
            'full_name': user_row['full_name'],
            'booked_flights': user_row['booked_flights'].split(',') if user_row['booked_flights'] else []
        }


flight_info = {}

# Fetch flight data from MySQL table and populate the flight_info dictionary
with db.cursor() as cursor:
    cursor.execute("SELECT * FROM flights")
    flight_rows = cursor.fetchall()

    for row in flight_rows:
        flight_id = row['flight_id']
        flight_data = {
            'from_city': row['from_city'],
            'to_city': row['to_city'],
            'departure_time': row['departure_time'],
            'arrival_time': row['arrival_time'],
            'duration': row['duration'],
            'price': row['price'],
            'airline': row['airline'],
            'departure_date': row['departure_date']
        }
        flight_info[flight_id] = flight_data

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/flights')
def shows():
    return render_template('flights.html', flight_info=flight_info)

@app.route('/search', methods=['GET'])
def search():
    # Get the search parameters from the request
    departure_date = request.args.get('departure_date')
    from_city = request.args.get('from_city', '')
    to_city = request.args.get('to_city', '')

    results = []
    for flight_id, flight_data in flight_info.items():
        if str(flight_data['departure_date']) == departure_date \
                and ((not from_city) or (from_city.lower() in flight_data['from_city'].lower())) \
                and ((not to_city) or (to_city.lower() in flight_data['to_city'].lower())):
            results.append((flight_id, flight_data))

    if results:
        return render_template('search_results.html', results=results)
    else:
        return "<p>No flights found for the selected date and cities.</p>"  

@app.route('/book', methods=['GET'])
def book():
    search_query = request.args.get('query')
    results = []

    if search_query:
        for flight_id, flight_data in flight_info.items():
            if search_query.lower() == str(flight_id):
                results.append((flight_id, flight_data))

    return render_template('book_results.html', search_query=search_query, results=results)

@app.route('/flight/<int:flight_id>')
def flight(flight_id):
    flight_data = flight_info.get(flight_id)
    if flight_data:
        return render_template('flight.html', flight_id=flight_id, flight_data=flight_data)  # Pass show_id
    else:
        # Handle the case when show data is not found
        return render_template('show_not_found.html')

@app.route('/discussion')
def discussion():
    # Connect to the MySQL database
    db = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        # Fetch discussion data from the MySQL table
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM discussion")
            discussion_data = cursor.fetchall()

        return render_template('discussion.html', discussion_data=discussion_data)

    finally:
        db.close()

@app.route('/add_discussion_message', methods=['POST'])
def add_discussion_message():
    message = request.form.get('message')
    user_id = session.get('user_id')
    username = users.get(user_id, {}).get('username', 'Unknown')

    if message and username:
        db = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        )

        try:
            with db.cursor() as cursor:
                # Insert new message into the discussion table
                sql = "INSERT INTO discussion (user_id, username, Comment) VALUES (%s, %s, %s)"
                cursor.execute(sql, (user_id, username, message))
                db.commit()  # Commit changes

        finally:
            db.close()

    return redirect(url_for('discussion'))  # Redirect back to the discussion page

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user_data = users.get(user_id)
        if user_data:
            return render_template('profile.html', user_id=user_id, user_data=user_data)
    return redirect(url_for('login'))

@app.route('/add_to_booked/<int:flight_id>', methods=['POST'])
def add_to_booked(flight_id):
    user_id = session.get('user_id')
    flight_data = flight_info.get(flight_id)
    if user_id:
        user_data = users.get(user_id)
        if user_data:
            seat = random.randint(1,40)
            if len(flight_seats[flight_id]) == 38:
                print("Flight is fully booked!")
            elif seat not in flight_seats[flight_id]:
                flight_seats[flight_id].append(seat)
                user_data['booked_flights'].append(('Flight ID: ' + str(flight_id), 'Airline: ' + flight_data['airline'], 'Seat: ' + str(seat)))
    return redirect(url_for('flight', flight_id=flight_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        max_user_id = max(users.keys(), default=0)
        user_id = max_user_id + 1

        password_hash = request.form.get('password_hash')
        username = request.form.get('username')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')
        full_name = request.form.get('full_name')

        if any(user_data['username'] == username for user_data in users.values()):
            return render_template('register.html', username_exists=True)

        users[user_id] = {
            'password_hash': password_hash,
            'username': username,
            'email': email,
            'contact_number': contact_number,
            'full_name': full_name,
            'booked_flights': []
        }

        # Update the MySQL database with the new user data
        with db.cursor() as cursor:
            sql = "INSERT INTO users (user_id, password_hash, username, email, contact_number, full_name) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (user_id, password_hash, username, email, contact_number, full_name))
            db.commit()

        # Update the user database text file
        user_database_path = os.path.join(os.path.dirname(__file__), 'user_database.txt')
        new_data = []
        for user_id, user_data in users.items():
            user_data_str = f"{user_data['password_hash']}:{user_data['username']}:{user_data['email']}:{user_data['contact_number']}:{user_data['full_name']}"
            new_data.append(f"{user_id}:{user_data_str}\n")
        with open(user_database_path, 'w') as file:
            file.writelines(new_data)

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_failed = False

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the provided username and password match any user
        for user_id, user_data in users.items():
            if user_data['username'] == username and user_data['password_hash'] == password:
                session['user_id'] = user_id
                return redirect(url_for('home'))
        
        # If no match found, set login_failed flag to True
        login_failed = True

    return render_template('login.html', login_failed=login_failed)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

app.run(debug=True)




        