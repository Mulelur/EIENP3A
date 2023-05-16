from flask import Flask, render_template, request, redirect, url_for
import sqlite3 
import os

currentdirectory = os.path.dirname(os.path.abspath(__file__))

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
        return render_template("home.html")

@app.route("/home", methods = ["POST"])
def myhome():
     EMAIL = request.form["email"]
     PASSWORD = request.form["password"]
     connection = sqlite3.connect(currentdirectory + "\database.db")
     cursor = connection.cursor()
     query1 = "SELECT username, password from Users Details WHERE username = '{un}' AND password = '{pw}'".format(un = EMAIL, pw = PASSWORD)
     
     rows = cursor.execute(query1)
     rows = rows.fetchall()
     if len(rows) == 1:
          return render_template("book.html")
     else:
          return redirect("/signup")
     
@app.route("/signup", methods = ["GET", "POST"])
def signup():
     if request.method == "POST":
          EMAIL = request.form["email"]
          PASSWORD = request.form["password"]
          NUMBER = request.form["number"]
          ADDRESS = request.form["address"]
          connection = sqlite3.connect(currentdirectory + "\database.db")
          cursor = connection.cursor()
          query1 = "INSERT INTO Users Details VALUES(?,?,?,?)", (EMAIL, PASSWORD, NUMBER, ADDRESS)
          cursor.execute(query1)
          connection.commit()
          return redirect("/home")
     
     return render_template("signup.html")

          

@app.route("/book", methods = ["POST", "GET"])
def book():
     if request.method == "POST":
      DESTINATION = request.form["destination"]
      TIME = request.form["time"]
      connection = sqlite3.connect(currentdirectory + "\database.db")
      cursor = connection.cursor()
      query1 = ("INSERT INTO bookings VALUES(?, ?)",(DESTINATION, TIME))
      cursor.execute(query1)
      connection.commit()
      return render_template("confirmation.html")
     
     return render_template("book.html")
     


@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")

if __name__ =="__main__":
    app.run(debug=True)
