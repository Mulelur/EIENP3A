import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import json
from functions.func import validate_password, is_valid_email
from faker import Faker

# Create an instance of Faker
fake = Faker()


class DBManager:
    def __init__(self, database='EIENP3A', host="weblinnkdb.ceuqepbib5y4.eu-north-1.rds.amazonaws.com", user="rOUrDHAm"):
        self.connection = mysql.connector.connect(
            user=user, 
            password='w&1E7ZER0gZ0lSJ^on%WIHrh',
            host=host, # name of the mysql service as set in the docker compose file
            database=database,
            auth_plugin='mysql_native_password'
        )
        self.cursor = self.connection.cursor()

    
    def populate_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS users')
        self.cursor.execute('DROP TABLE IF EXISTS bus_schedules')
        self.cursor.execute('DROP TABLE IF EXISTS bus')
        self.cursor.execute('DROP TABLE IF EXISTS schedule')
        self.cursor.execute('CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))')
        self.cursor.execute('CREATE TABLE bus_schedules (id INT AUTO_INCREMENT PRIMARY KEY, res_name VARCHAR(255), schedule_time DATE, available_seats INT, bus_name VARCHAR(255))')
        self.cursor.execute('CREATE TABLE bus (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))')
        self.cursor.execute('CREATE TABLE schedule (id INT AUTO_INCREMENT PRIMARY KEY, bus_name VARCHAR(255),  res_name VARCHAR(255),  user_id INT, time DATE)')

        
        bus_names = [fake.company() for _ in range(1, 5)]
        query = 'INSERT INTO bus (id, name) VALUES (%s, %s);'
        data = [(i, name) for i, name in enumerate(bus_names, start=1)]
        self.cursor.executemany(query, data)

        res_names = ["Amberfield", "Park Village", "Park Square", "Good year", "SunTrust", "GreenWays"]

        # # Insert names into the res table
        # query = 'INSERT INTO res (id, name) VALUES (%s, %s);'
        # data = [(i, name) for i, name in enumerate(res_names, start=1)]
        # self.cursor.executemany(query, data)

        self.connection.commit()
    
    def query_titles(self):
        self.cursor.execute('SELECT title FROM blog')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec
    
    def username_exists(self, username):
            self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = self.cursor.fetchone()

            return existing_user
    
    def create_user(self, username, password):
        self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        self.connection.commit()

    def retrieve_user(self, username, password):
        self.cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = self.cursor.fetchone()
        return user

    def update_available_seats(self, schedule_time, res_name, available_seats):
            book_query = 'INSERT INTO bus_schedules (schedule_time, res_name, available_seats) VALUES (%s, %s, %s)'
            self.cursor.execute(book_query, (schedule_time, res_name, available_seats - 1))

    def current_available_seats(self, res_name):
            available_seats_query = 'SELECT available_seats FROM bus_schedules WHERE res_name = %s'
            self.cursor.execute(available_seats_query, (res_name,))

            available_seats = self.cursor.fetchone()

            return available_seats

server = Flask(__name__)
conn = None

@server.route('/')
def listBlog():
    global conn
    if not conn:
        conn = DBManager()
        conn.populate_db()
    

    # response = ''
    # for c in rec:
    #     response = response  + '<div>   Hello  ' + c + '</div>'
    # return response
    return render_template('index.html')

@server.route('/booking')
def booking():
    # global conn
    # if not conn:
    #     conn = DBManager(password_file='/run/secrets/db-password')
    #     conn.populate_db()
    
    return render_template('booking.html')

# 
@server.route('/signup')
def signup():
    username = request.form["email"]
    password = request.form["password"]
    password_confirm = request.form["confirmPassword"]

    if password != password_confirm:
        # Password and password confirmation do not match
        print("Password and password confirmation do not match.")
        return {
            "isBase64Encoded": True,
            "statusCode": 400,
            'body': json.dumps({"success": False, "message": "Password and password confirmation do not match."}),
        }

    if not is_valid_email(username):
        return {
            "isBase64Encoded": True,
            "statusCode": 400,
            'body': json.dumps({"success": False, "message": "Email is not a valid email address"}),
        }

    if not validate_password(password):
        # Password does not meet the requirements
        return {
            "isBase64Encoded": True,
            "statusCode": 400,
            'body': json.dumps({"success": False, "message": "Password does not meet the requirements"}),
        }

    try:
        global conn
        if not conn:
            conn = DBManager()
            existing_user = conn.username_exists(username)

            if existing_user:
                # Username already exists, return False for failed signup
                print("Username already exists. Please choose a different username.")
                return {
                    "isBase64Encoded": True,
                    "statusCode": 400,

                    'body': json.dumps({"success": False, "error": "Username already exists. Please choose a different username."}),
                }
            else:
                # Insert new user into the database
                conn.create_user(username, password)
                print("Signup successful!")
                return {
                    "isBase64Encoded": True,
                    "statusCode": 201,

                    'body': json.dumps({"success": True, "message": "Account created successfully!"}),
                }

    except Exception as e:
        # Handle any exceptions that may occur
        print("Error: ", e)
        return {
            "isBase64Encoded": True,
            "statusCode": 500,
            'body': json.dumps({"success": False, "message": "Something went wrong, please try again"}),
        }
    


@server.route('/login', methods=['POST', 'GET'])
def login():
    if request.methods == 'POST':
        username = request.form["email"]
        password = request.form["password"]

        try:
            # test connection
            global conn
            if not conn:
                conn = DBManager()
                user = conn.retrieve_user(username, password)

                if user:
                    # User found, return True for successful login
                    print("Login successful!")
                    userId = user[0]
                    userName = user[1]

                    return {
                        "isBase64Encoded": True,
                        "statusCode": 200,

                        'body': json.dumps({"success": True, "message": "Login successful!", "data": {
                            "userId": userId,
                            "uername": userName,
                        }}),
                    }
                else:
                    # User not found, return False for failed login
                    print("Invalid username or password.")
                    return {
                        "isBase64Encoded": True,
                        "statusCode": 400,

                        'body': json.dumps({"success": False, "message": "Invalid username or password."}),
                    }

        except Exception as e:
            # Handle any exceptions that may occur
            print("Error: ", e)
            return {
                "isBase64Encoded": True,
                "statusCode": 500,
                'body': json.dumps({"success": False, "message": "Something went wrong, please try again."}),
            }
    else:
        return render_template('login.html')


@server.route('/book_schedule', methods=['POST'])
def book_schedule():
    if request.method == 'POST':
        schedule_time = request.form['schedule_time']
        resName = request.form['resName']

        # Get the current available seats for the resource
        global conn
        if not conn:
            conn = DBManager()
        
            available_seats = conn.current_available_seats(resName)

            if available_seats:
                available_seats = available_seats[0]
            else:
                available_seats = 0

            if available_seats <= 0:
                return f"No available seats for {resName}."

            # Perform the booking logic and update the available seats
            conn.update_available_seats(schedule_time, resName, available_seats)


            return f"The schedule at {schedule_time} for {resName} has been booked successfully. {available_seats - 1} seat(s) remaining."
    else: 
        return render_template('booking.html')

if __name__ == '__main__':
    server.run()