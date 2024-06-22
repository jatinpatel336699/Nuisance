<<<<<<< HEAD
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_cors import cross_origin
import sklearn
import pickle
import pandas as pd
import sqlite3
import re
import requests
import datetime
from datetime import date

app = Flask(__name__)
model = pickle.load(open("Flight_Price_Prediction_Random_Forest_new.pkl", "rb"))

def get_airlines():
    conn = sqlite3.connect('flights2.db')
    c = conn.cursor()
    c.execute('SELECT AIRLINES FROM airlines')
    airlines = [row[0] for row in c.fetchall()]
    conn.close()
    return airlines

def get_airports():
    conn = sqlite3.connect('flights2.db')
    c = conn.cursor()
    c.execute('SELECT name FROM airports')
    airports = [row[0] for row in c.fetchall()]
    conn.close()
    return airports


@app.route("/")
@cross_origin()
def home():
    airlines2 = get_airlines()
    airports2 = get_airports()
    return render_template('home_new.html', airlines=airlines2, airports=airports2)
    #return render_template("home.html")


@app.route("/predict", methods=["GET", "POST"])
@cross_origin()
def predict():
    if request.method == "POST":
        try:

            # Date_of_Journey
            date_dep = request.form["Dep_Time"]
            Journey_day = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").day)
            Journey_month = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").month)
            Journey_year = int(pd.to_datetime(date_dep, format = "%Y-%m-%dT%H:%M").year)
        
            # print("Journey Date : ",Journey_day, Journey_month)

            # Departure
            Dep_hour = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").hour)
            Dep_min = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").minute)
            # print("Departure : ",Dep_hour, Dep_min)
            
            
            # Arrival
            #date_arr = request.form["Arrival_Time"]
            #Arrival_hour = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").hour)
            #Arrival_min = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").minute)
            # print("Arrival : ", Arrival_hour, Arrival_min)

            # Duration
            #dur_hour = abs(Arrival_hour - Dep_hour)
            #dur_min = abs(Arrival_min - Dep_min)
            # print("Duration : ", dur_hour, dur_min)

            # Total Stops
            Total_stops = int(request.form["stops"])
            # print(Total_stops)
            
            

    ###############################################################################################################
            conn = sqlite3.connect('flights2.db')
            c = conn.cursor()
            
            airline = request.form['airline']
            c.execute('SELECT * FROM airlines WHERE AIRLINES=?', (airline,))
            airline_data = c.fetchone()
            if airline_data:
                airline_name = airline_data[1]  # Assuming the first column is the ID
                rating = airline_data[2]
                avg_price = airline_data[3]
            else:
                # If the airline is not found in the database, set default values
                airline_name = None
                rating = 0
                avg_price = 0


            # Source
            source = request.form["Source"]
            c.execute('SELECT * FROM airports WHERE name=?', (source,))
            source_data = c.fetchone()
            if source_data:
                source_name = source_data[1]  # Assuming the first column is the ID
            else:
                # If the source airport is not found in the database, set default values
                source_name = None

            #print(source_name)
            # Destination
            destination = request.form["Destination"]
            c.execute('SELECT * FROM airports WHERE name=?', (destination,))
            destination_data = c.fetchone()
            if destination_data:
                destination_name = destination_data[1]  # Assuming the first column is the ID
   

            else:
                # If the destination airport is not found in the database, set default values
                destination_name = None
                
            
            c.execute('''
                SELECT Duration_Hour, Duration_Minutes
                FROM flights 
                WHERE Source = ? AND Destination = ? AND Total_Stops = ?
                ORDER BY Duration_Hour, Duration_Minutes ASC
                LIMIT 1
            ''', (source, destination, Total_stops))
            
            flight_data = c.fetchone()
            
            
            
            if flight_data:
                dur_hour = flight_data[0]
                dur_min = flight_data[1]
            else:
                return render_template('home_new.html', prediction_text = "No flights found for the given criteria.", airlines = get_airlines(), airports = get_airports())
            
            Arrival_hour = Dep_hour + dur_hour
            Arrival_min = Dep_min + dur_min
            
            if Arrival_min>=60:
                Arrival_hour += Arrival_min//60
                Arrival_min = Arrival_min%60
            
            if Arrival_hour >= 24:
                Arrival_hour = Arrival_hour % 24
                
                
            
    #############################################################################################################
            inputs = [Total_stops,
                rating, 
                Journey_day,
                Journey_month,
                Journey_year,
                dur_hour,
                dur_min,
                Dep_hour,
                Dep_min,
                Arrival_hour,
                Arrival_min,
                avg_price]
            
            c.execute('SELECT Airlines FROM airlines')
            #airlines = c.fetchall()
            airlines = [row[0] for row in c.fetchall()]

                
            c.execute('SELECT name FROM airports')
            #airports = c.fetchall()
            airports = [row[0] for row in c.fetchall()]
            # Close the database connection
            conn.close()
            #airlines = pd.read_csv('Airlines.csv')['Airlines'].tolist()
            
            #airlines2 = ["Airlines_"+airline for airline in airlines]
            
            #airports = pd.read_csv('Airports.csv')['Airports'].tolist()
            
            #source = ["Sources_"+airport for airport in airports]
            
            #destination = ["Destinations_"+airport for airport in airports]
            
            dynamic_variables = {}
            #print(airports)
            for airline in airlines:
                if airline==airline_name:
                    value = 1
                else:
                    value = 0
                    
                dynamic_variables[airline] = value
                inputs.append(dynamic_variables[airline])
                
                
            #print(source_name)
            
            for sources in airports:
                if sources == source_name:
                    value = 1
                else:
                    value = 0
                dynamic_variables[sources] = value
                inputs.append(dynamic_variables[sources])
              
                    
            for destinations in airports:
                if destinations == destination_name:
                    value = 1
                else:
                    value = 0
                dynamic_variables[destinations] = value
                inputs.append(value)
                
            
            print(len(inputs))
            print(len(airlines))
            print(2*len(airports))
            
            print('*'*10)
            print(inputs)
            print('*'*10)
                    
            prediction = model.predict([inputs])
            
            print(prediction)
            output = round(prediction[0], 2)
            return render_template('home_new.html', prediction_text="Your Flight price is Rs. {}".format(output), airlines=airlines, airports=airports)
        except Exception as e:
            print(e)
            #return render_template('home.html', prediction_text="Your Flight price is Rs. {}".format(output))

        return redirect(url_for('home_new.html')) 
        #return render_template('home_new.html')      



@app.route('/real2')
def home2():
    airlines = get_airlines()
    airports = get_airports()
    today = date.today()
    return render_template('flight_search.html' ,airlines=airlines, airports=airports, today = today)

@app.route('/search_flights', methods=['POST'])
def search_flights():
    if request.method == 'POST':
        # Retrieve form data
        source = request.form['origin']
        destination = request.form['destination']
        departure_date = request.form['departure_date']
        
        conn = sqlite3.connect('flights2.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM airports WHERE name=?', (source,))
        source_data= c.fetchone()
        if source_data:
            source_name = source_data[1]  # Assuming the second column is the name
        else:
            source_name = None
                    
        c.execute('SELECT * FROM airports WHERE name=?', (destination,))
        destination_data = c.fetchone()
        if destination_data:
            destination_name = destination_data[1]  # Assuming the second column is the name
        else:
            destination_name = None
                    
        api_key = "jAi4JCgGQtXtyHFkQtbq1pAxAJWrMAjt"
        api_secret = "PsrrYe5wdYvJj9vz"  # You need to provide the actual API secret

        conn.commit()
        conn.close()
        # Get access token
        access_token = get_access_token(api_key, api_secret)
        
        # Call function to search for flights
        flights = search_future_flights(access_token, source_name, destination_name, departure_date)
        
        
        if flights:
            flight_info_list = []
            #print(len(flights))
            print(flights)
           
            for flight in flights['data']:
                
                total_price = flight['price']['total']
                segment = flight['itineraries'][0]['segments'][0]
                airline_code = segment['carrierCode']
                flight_number = segment['carrierCode'] + segment['number']
                #print(flight_number)
                source = segment['departure']['iataCode']
                #print(source)
                destination = segment['arrival']['iataCode']
                #print(destination)
                departure_time = convert_arrival_time(segment['departure']['at'])
                arrival_time = convert_arrival_time(segment['arrival']['at'])
                duration = segment['duration']
                
            
                conn = sqlite3.connect('flights2.db')
                c = conn.cursor()
                c.execute('SELECT AIRLINE FROM airline_codes WHERE IATA=?', (airline_code,))
                airline = c.fetchone()
                
                if airline:
                    airline = airline[0]
                else:
                    airline = "Other"
                
                c.execute('SELECT Airport FROM airports2 WHERE IATA = ?', (source,))
                source_airport = c.fetchone()[0]

                c.execute('SELECT Airport FROM airports2 WHERE IATA = ?', (destination,))
                
                destination_airport = c.fetchone()
                if destination_airport:
                    destination_airport = destination_airport[0]
                
                match = re.match(r'PT(\d+H)?(\d+M)?', duration)
                dur_hour = int(match.group(1)[:-1] if match.group(1) else '0')
                dur_min = int(match.group(2)[:-1] if match.group(2) else '0')
                
                duration = convert_duration(segment['duration'])
                
                Total_stops = len(flight['itineraries'][0]['segments']) - 1

                flight_info = {
                    'airline_code': airline_code,
                    'flight_number': flight_number,
                    'airline_name': airline,
                    'source': source_airport,
                    'destination': destination_airport,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'duration': duration,
                    'stops': Total_stops,
                    'total_price': total_price,
                    'price_prediction': None
                }
                
                flight_info_list.append(flight_info)
            
            if (len(flight_info_list)==0):
                return render_template('real-flights.html', flights = [])
            return render_template('real-flights.html', flights=flight_info_list)
        else:
            return render_template('real-flights.html', flights = flight_info_list)
            return "Error: Failed to retrieve flight information"
    else:
        return render_template('flight_search.html')

@app.route('/predict2', methods=['POST'])
def predict2():
    data = request.json
    airline_name = data['flightNumber']
    departure_time = data['departureTime']
    arrival_time = data['arrivalTime']
    airline_code = data['airlineCode']
    stops = data['stops']
    duration = data['duration']
    #total_price = data['totalPrice']
    
    conn = sqlite3.connect('flights2.db')
    c = conn.cursor()
    
    c.execute('SELECT AIRLINE FROM airline_codes WHERE IATA=?', (airline_code,))
    airline = c.fetchone()
    if airline:
        airline = airline[0]

    
    print(airline)
    
    c.execute('SELECT * FROM airlines WHERE Airlines=?', (airline,))
    airline_data = c.fetchone()
    if airline_data:
        airline = airline_data[1]
        rating = airline_data[2]
        avg_price = airline_data[3]
    else:
        rating = 0
        avg_price = 0

    Journey_day = pd.to_datetime(departure_time).day
    Journey_month = pd.to_datetime(departure_time).month
    Journey_year = pd.to_datetime(departure_time).year
    
    Dep_hour = pd.to_datetime(departure_time).hour
    Dep_min = pd.to_datetime(departure_time).minute
    Arrival_hour = pd.to_datetime(arrival_time).hour
    Arrival_min = pd.to_datetime(arrival_time).minute
    
    match = re.match(r'(\d+) hours (\d+) minutes', duration)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))

    dur_hour = hours
    dur_min = minutes
    
    inputs = [
        stops,
        rating,
        Journey_day,
        Journey_month,
        Journey_year,
        dur_hour,
        dur_min,
        Dep_hour, 
        Dep_min,
        Arrival_hour,
        Arrival_min,
        avg_price
    ]
    
    c.execute('SELECT Airlines FROM airlines')
    #airlines = c.fetchall()
    airlines = [row[0] for row in c.fetchall()]
    
    conn.close()
    conn = sqlite3.connect('flights2.db')
    c = conn.cursor()
    c.execute('SELECT Airport FROM airports2')
    #airports = c.fetchall()
    airports = [row[0] for row in c.fetchall()]

    print(airlines)
    for airline_ in airlines:
        if airline_ == airline:
            inputs.append(1)
        else:
            inputs.append(0)
    
    
    print(data['source'])
    print(data['destination'])
    print(len(data['destination']))
    for source_ in airports:
        value = 0
        if source_ == data['source']:
           value = 1
        inputs.append(value)
        
    print(airports)
    for destination_ in airports:
        value = 0
        if destination_ == data['destination']:
            value = 1
        inputs.append(value)

    print("Inputs: ", inputs)
    print(len(inputs))
    model = pickle.load(open("Flight_Price_Prediction_Random_Forest_new.pkl", "rb"))
    prediction = model.predict([inputs])
    
    conn.close()
    
    return jsonify(price_prediction=prediction[0])

def get_access_token(api_key, api_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": api_secret
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None



def convert_duration(duration):
    if not duration.startswith('PT'):
        raise ValueError("Invalid duration format")

    duration = duration[2:]  # Strip the 'PT' prefix
    hours = 0
    minutes = 0

    # Check if duration contains hours
    if 'H' in duration:
        hours = int(duration.split('H')[0])
        duration = duration.split('H')[1]

    # Check if duration contains minutes
    if 'M' in duration:
        minutes = int(duration.split('M')[0])

    total_minutes = hours * 60 + minutes
    return f"{hours} hours {minutes} minutes"
    hours = 0
    minutes = 0
    if 'H' in duration:
        hours = int(duration.split('H')[0][2:])
    if 'M' in duration:
        minutes = int(duration.split('M')[0].split('H')[-1])
    return f"{hours} hours {minutes} minutes"

# Convert arrival time to datetime object
def convert_arrival_time(arrival_time):
    parsed_time = datetime.datetime.strptime(arrival_time, "%Y-%m-%dT%H:%M:%S")
    # Format the parsed time to only display hour and minute
    formatted_time = parsed_time.strftime("%d %B, %Y at %I:%M %p")  # %I for 12-hour format, %p for AM/PM
    return formatted_time


def search_future_flights(access_token, origin, destination, departure_date):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": 1,
        "nonStop": {"true", "false"},
        "max": 250
    } 
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

if __name__ == "__main__":
=======
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_cors import cross_origin
import sklearn
import pickle
import pandas as pd
import sqlite3
import re
import requests
import datetime
from datetime import date

app = Flask(__name__)
model = pickle.load(open("Flight_Price_Prediction_Random_Forest_new.pkl", "rb"))

def get_airlines():
    conn = sqlite3.connect('flights2.db')
    c = conn.cursor()
    c.execute('SELECT AIRLINES FROM airlines')
    airlines = [row[0] for row in c.fetchall()]
    conn.close()
    return airlines

def get_airports():
    conn = sqlite3.connect('flights2.db')
    c = conn.cursor()
    c.execute('SELECT name FROM airports')
    airports = [row[0] for row in c.fetchall()]
    conn.close()
    return airports


@app.route("/")
@cross_origin()
def home():
    airlines2 = get_airlines()
    airports2 = get_airports()
    return render_template('home_new.html', airlines=airlines2, airports=airports2)
    #return render_template("home.html")


@app.route("/predict", methods=["GET", "POST"])
@cross_origin()
def predict():
    if request.method == "POST":
        try:

            # Date_of_Journey
            date_dep = request.form["Dep_Time"]
            Journey_day = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").day)
            Journey_month = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").month)
            Journey_year = int(pd.to_datetime(date_dep, format = "%Y-%m-%dT%H:%M").year)
        
            # print("Journey Date : ",Journey_day, Journey_month)

            # Departure
            Dep_hour = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").hour)
            Dep_min = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").minute)
            # print("Departure : ",Dep_hour, Dep_min)
            
            
            # Arrival
            #date_arr = request.form["Arrival_Time"]
            #Arrival_hour = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").hour)
            #Arrival_min = int(pd.to_datetime(date_arr, format="%Y-%m-%dT%H:%M").minute)
            # print("Arrival : ", Arrival_hour, Arrival_min)

            # Duration
            #dur_hour = abs(Arrival_hour - Dep_hour)
            #dur_min = abs(Arrival_min - Dep_min)
            # print("Duration : ", dur_hour, dur_min)

            # Total Stops
            Total_stops = int(request.form["stops"])
            # print(Total_stops)
            
            

    ###############################################################################################################
            conn = sqlite3.connect('flights2.db')
            c = conn.cursor()
            
            airline = request.form['airline']
            c.execute('SELECT * FROM airlines WHERE AIRLINES=?', (airline,))
            airline_data = c.fetchone()
            if airline_data:
                airline_name = airline_data[1]  # Assuming the first column is the ID
                rating = airline_data[2]
                avg_price = airline_data[3]
            else:
                # If the airline is not found in the database, set default values
                airline_name = None
                rating = 0
                avg_price = 0


            # Source
            source = request.form["Source"]
            c.execute('SELECT * FROM airports WHERE name=?', (source,))
            source_data = c.fetchone()
            if source_data:
                source_name = source_data[1]  # Assuming the first column is the ID
            else:
                # If the source airport is not found in the database, set default values
                source_name = None

            #print(source_name)
            # Destination
            destination = request.form["Destination"]
            c.execute('SELECT * FROM airports WHERE name=?', (destination,))
            destination_data = c.fetchone()
            if destination_data:
                destination_name = destination_data[1]  # Assuming the first column is the ID
   

            else:
                # If the destination airport is not found in the database, set default values
                destination_name = None
                
            
            c.execute('''
                SELECT Duration_Hour, Duration_Minutes
                FROM flights 
                WHERE Source = ? AND Destination = ? AND Total_Stops = ?
                ORDER BY Duration_Hour, Duration_Minutes ASC
                LIMIT 1
            ''', (source, destination, Total_stops))
            
            flight_data = c.fetchone()
            
            
            
            if flight_data:
                dur_hour = flight_data[0]
                dur_min = flight_data[1]
            else:
                return render_template('home_new.html', prediction_text = "No flights found for the given criteria.", airlines = get_airlines(), airports = get_airports())
            
            Arrival_hour = Dep_hour + dur_hour
            Arrival_min = Dep_min + dur_min
            
            if Arrival_min>=60:
                Arrival_hour += Arrival_min//60
                Arrival_min = Arrival_min%60
            
            if Arrival_hour >= 24:
                Arrival_hour = Arrival_hour % 24
                
                
            
    #############################################################################################################
            inputs = [Total_stops,
                rating, 
                Journey_day,
                Journey_month,
                Journey_year,
                dur_hour,
                dur_min,
                Dep_hour,
                Dep_min,
                Arrival_hour,
                Arrival_min,
                avg_price]
            
            c.execute('SELECT Airlines FROM airlines')
            #airlines = c.fetchall()
            airlines = [row[0] for row in c.fetchall()]

                
            c.execute('SELECT name FROM airports')
            #airports = c.fetchall()
            airports = [row[0] for row in c.fetchall()]
            # Close the database connection
            conn.close()
            #airlines = pd.read_csv('Airlines.csv')['Airlines'].tolist()
            
            #airlines2 = ["Airlines_"+airline for airline in airlines]
            
            #airports = pd.read_csv('Airports.csv')['Airports'].tolist()
            
            #source = ["Sources_"+airport for airport in airports]
            
            #destination = ["Destinations_"+airport for airport in airports]
            
            dynamic_variables = {}
            #print(airports)
            for airline in airlines:
                if airline==airline_name:
                    value = 1
                else:
                    value = 0
                    
                dynamic_variables[airline] = value
                inputs.append(dynamic_variables[airline])
                
                
            #print(source_name)
            
            for sources in airports:
                if sources == source_name:
                    value = 1
                else:
                    value = 0
                dynamic_variables[sources] = value
                inputs.append(dynamic_variables[sources])
              
                    
            for destinations in airports:
                if destinations == destination_name:
                    value = 1
                else:
                    value = 0
                dynamic_variables[destinations] = value
                inputs.append(value)
                
            
            print(len(inputs))
            print(len(airlines))
            print(2*len(airports))
            
            print('*'*10)
            print(inputs)
            print('*'*10)
                    
            prediction = model.predict([inputs])
            
            print(prediction)
            output = round(prediction[0], 2)
            return render_template('home_new.html', prediction_text="Your Flight price is Rs. {}".format(output), airlines=airlines, airports=airports)
        except Exception as e:
            print(e)
            #return render_template('home.html', prediction_text="Your Flight price is Rs. {}".format(output))

        return redirect(url_for('home_new.html')) 
        #return render_template('home_new.html')      



@app.route('/real2')
def home2():
    airlines = get_airlines()
    airports = get_airports()
    today = date.today()
    return render_template('flight_search.html' ,airlines=airlines, airports=airports, today = today)

@app.route('/search_flights', methods=['POST'])
def search_flights():
    if request.method == 'POST':
        # Retrieve form data
        source = request.form['origin']
        destination = request.form['destination']
        departure_date = request.form['departure_date']
        
        conn = sqlite3.connect('flights2.db')
        c = conn.cursor()
        
        c.execute('SELECT * FROM airports WHERE name=?', (source,))
        source_data= c.fetchone()
        if source_data:
            source_name = source_data[1]  # Assuming the second column is the name
        else:
            source_name = None
                    
        c.execute('SELECT * FROM airports WHERE name=?', (destination,))
        destination_data = c.fetchone()
        if destination_data:
            destination_name = destination_data[1]  # Assuming the second column is the name
        else:
            destination_name = None
                    
        api_key = "jAi4JCgGQtXtyHFkQtbq1pAxAJWrMAjt"
        api_secret = "PsrrYe5wdYvJj9vz"  # You need to provide the actual API secret

        conn.commit()
        conn.close()
        # Get access token
        access_token = get_access_token(api_key, api_secret)
        
        # Call function to search for flights
        flights = search_future_flights(access_token, source_name, destination_name, departure_date)
        
        
        if flights:
            flight_info_list = []
            #print(len(flights))
            print(flights)
           
            for flight in flights['data']:
                
                total_price = flight['price']['total']
                segment = flight['itineraries'][0]['segments'][0]
                airline_code = segment['carrierCode']
                flight_number = segment['carrierCode'] + segment['number']
                #print(flight_number)
                source = segment['departure']['iataCode']
                #print(source)
                destination = segment['arrival']['iataCode']
                #print(destination)
                departure_time = convert_arrival_time(segment['departure']['at'])
                arrival_time = convert_arrival_time(segment['arrival']['at'])
                duration = segment['duration']
                
            
                conn = sqlite3.connect('flights2.db')
                c = conn.cursor()
                c.execute('SELECT AIRLINE FROM airline_codes WHERE IATA=?', (airline_code,))
                airline = c.fetchone()
                
                if airline:
                    airline = airline[0]
                else:
                    airline = "Other"
                
                c.execute('SELECT Airport FROM airports2 WHERE IATA = ?', (source,))
                source_airport = c.fetchone()[0]

                c.execute('SELECT Airport FROM airports2 WHERE IATA = ?', (destination,))
                
                destination_airport = c.fetchone()
                if destination_airport:
                    destination_airport = destination_airport[0]
                
                match = re.match(r'PT(\d+H)?(\d+M)?', duration)
                dur_hour = int(match.group(1)[:-1] if match.group(1) else '0')
                dur_min = int(match.group(2)[:-1] if match.group(2) else '0')
                
                duration = convert_duration(segment['duration'])
                
                Total_stops = len(flight['itineraries'][0]['segments']) - 1

                flight_info = {
                    'airline_code': airline_code,
                    'flight_number': flight_number,
                    'airline_name': airline,
                    'source': source_airport,
                    'destination': destination_airport,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'duration': duration,
                    'stops': Total_stops,
                    'total_price': total_price,
                    'price_prediction': None
                }
                
                flight_info_list.append(flight_info)
            
            if (len(flight_info_list)==0):
                return render_template('real-flights.html', flights = [])
            return render_template('real-flights.html', flights=flight_info_list)
        else:
            return render_template('real-flights.html', flights = flight_info_list)
            return "Error: Failed to retrieve flight information"
    else:
        return render_template('flight_search.html')

@app.route('/predict2', methods=['POST'])
def predict2():
    data = request.json
    airline_name = data['flightNumber']
    departure_time = data['departureTime']
    arrival_time = data['arrivalTime']
    airline_code = data['airlineCode']
    stops = data['stops']
    duration = data['duration']
    #total_price = data['totalPrice']
    
    conn = sqlite3.connect('flights2.db')
    c = conn.cursor()
    
    c.execute('SELECT AIRLINE FROM airline_codes WHERE IATA=?', (airline_code,))
    airline = c.fetchone()
    if airline:
        airline = airline[0]

    
    print(airline)
    
    c.execute('SELECT * FROM airlines WHERE Airlines=?', (airline,))
    airline_data = c.fetchone()
    if airline_data:
        airline = airline_data[1]
        rating = airline_data[2]
        avg_price = airline_data[3]
    else:
        rating = 0
        avg_price = 0

    Journey_day = pd.to_datetime(departure_time).day
    Journey_month = pd.to_datetime(departure_time).month
    Journey_year = pd.to_datetime(departure_time).year
    
    Dep_hour = pd.to_datetime(departure_time).hour
    Dep_min = pd.to_datetime(departure_time).minute
    Arrival_hour = pd.to_datetime(arrival_time).hour
    Arrival_min = pd.to_datetime(arrival_time).minute
    
    match = re.match(r'(\d+) hours (\d+) minutes', duration)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))

    dur_hour = hours
    dur_min = minutes
    
    inputs = [
        stops,
        rating,
        Journey_day,
        Journey_month,
        Journey_year,
        dur_hour,
        dur_min,
        Dep_hour, 
        Dep_min,
        Arrival_hour,
        Arrival_min,
        avg_price
    ]
    
    c.execute('SELECT Airlines FROM airlines')
    #airlines = c.fetchall()
    airlines = [row[0] for row in c.fetchall()]
    
    conn.close()
    conn = sqlite3.connect('flights2.db')
    c = conn.cursor()
    c.execute('SELECT Airport FROM airports2')
    #airports = c.fetchall()
    airports = [row[0] for row in c.fetchall()]

    print(airlines)
    for airline_ in airlines:
        if airline_ == airline:
            inputs.append(1)
        else:
            inputs.append(0)
    
    
    print(data['source'])
    print(data['destination'])
    print(len(data['destination']))
    for source_ in airports:
        value = 0
        if source_ == data['source']:
           value = 1
        inputs.append(value)
        
    print(airports)
    for destination_ in airports:
        value = 0
        if destination_ == data['destination']:
            value = 1
        inputs.append(value)

    print("Inputs: ", inputs)
    print(len(inputs))
    model = pickle.load(open("Flight_Price_Prediction_Random_Forest_new.pkl", "rb"))
    prediction = model.predict([inputs])
    
    conn.close()
    
    return jsonify(price_prediction=prediction[0])

def get_access_token(api_key, api_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": api_secret
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None



def convert_duration(duration):
    if not duration.startswith('PT'):
        raise ValueError("Invalid duration format")

    duration = duration[2:]  # Strip the 'PT' prefix
    hours = 0
    minutes = 0

    # Check if duration contains hours
    if 'H' in duration:
        hours = int(duration.split('H')[0])
        duration = duration.split('H')[1]

    # Check if duration contains minutes
    if 'M' in duration:
        minutes = int(duration.split('M')[0])

    total_minutes = hours * 60 + minutes
    return f"{hours} hours {minutes} minutes"
    hours = 0
    minutes = 0
    if 'H' in duration:
        hours = int(duration.split('H')[0][2:])
    if 'M' in duration:
        minutes = int(duration.split('M')[0].split('H')[-1])
    return f"{hours} hours {minutes} minutes"

# Convert arrival time to datetime object
def convert_arrival_time(arrival_time):
    parsed_time = datetime.datetime.strptime(arrival_time, "%Y-%m-%dT%H:%M:%S")
    # Format the parsed time to only display hour and minute
    formatted_time = parsed_time.strftime("%d %B, %Y at %I:%M %p")  # %I for 12-hour format, %p for AM/PM
    return formatted_time


def search_future_flights(access_token, origin, destination, departure_date):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": 1,
        "nonStop": {"true", "false"},
        "max": 250
    } 
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

if __name__ == "__main__":
>>>>>>> dfc51ce40cf6aea1ea3dfd097c79f17aa0ad21c7
    app.run(debug=True)