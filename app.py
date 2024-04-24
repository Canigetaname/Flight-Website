from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import pymysql

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

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user_data = users.get(user_id)
        if user_data:
            return render_template('profile.html', user_id=user_id, user_data=user_data)
    return redirect(url_for('login'))

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
            'full_name': full_name
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

app.run(debug=True)
