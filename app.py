from flask import Flask, render_template

app = Flask(__name__)

# Sample data (replace with actual data fetched from the database)
sample_airports = [
    {'code': 'JFK', 'name': 'John F. Kennedy International Airport', 'city': 'New York', 'country': 'USA'},
    {'code': 'LAX', 'name': 'Los Angeles International Airport', 'city': 'Los Angeles', 'country': 'USA'},
    {'code': 'LHR', 'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK'},
]

sample_flights = [
    {'number': 'ABC123', 'departure_airport': 'JFK', 'arrival_airport': 'LAX'},
    {'number': 'DEF456', 'departure_airport': 'LAX', 'arrival_airport': 'LHR'},
    {'number': 'GHI789', 'departure_airport': 'LHR', 'arrival_airport': 'JFK'},
]

# Define routes and controller functions
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view_airports')
def view_airports():
    # Logic to fetch airports from the database
    airports = sample_airports  # Replace with actual data fetched from the database
    return render_template('view_airports.html', airports=airports)

@app.route('/view_flights')
def view_flights():
    # Logic to fetch flights from the database
    flights = sample_flights  # Replace with actual data fetched from the database
    return render_template('view_flights.html', flights=flights)

# Add more routes and controller functions as needed

if __name__ == '__main__':
    app.run(debug=True)
