from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

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

app.run(debug=True)
