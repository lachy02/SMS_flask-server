from flask import Flask, render_template, redirect, url_for, request, session
from flask_table import Table, Col
from flask_mail import Mail, Message
import hashlib
import os
import dateparser
import csv

app = Flask(__name__)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'localhost',
    MAIL_PORT = 587,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'my_username@gmail.com',
))

mail = Mail(app)


app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw" # secret key for sessions


users = {               # table of all allowed EU's
    'admin':'admin',
    'lachlan':'mod',
}

customer_list = []


class ItemTable(Table): # used to create html table for main page
    LName = Col('Last Name')
    FName = Col('First Name')
    Time = Col('Time')

def is_user(username, password): # function to check that EU has correct login details
    global user_auth
    for key in users: # check through usernames in the users dict
        if key == username:
            if users[key] == password: # check is the entered passwaor matches
                return True # user is a valid user
    return False # user is not a valid user


def get_file(date): # parses date and retrieves customers for entered day, returns in 2D dict
    details = None
    global customer_list
    customer_list = []
    file_name = date + ".txt" # sets file name
    try:
        with open("static/dates/" + file_name) as csv_file: #opens file as csv_file
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader: # sorts through each row in the file
                customer_list.append(dict(LName = row[1], FName = row[0], Time = row[2], Email = row[3])) # appends to customer_list
            return customer_list
    except:
        return None # if file does not exist


def sort_customers(customer): #complex algorithm used to sort customers based on time of appointment
    for i in range(len(customer)):
        minimum = i
        for j in range(i+1, len(customer)):
            if customer[j]['Time'] < customer[minimum]['Time']:
                minimum = j
        customer[minimum], customer[i] = customer[i], customer[minimum]
        return customer



@app.route("/") # NOTE: auto firts app that flask runs, redirects auto to login app
def move():
    return redirect(url_for("login"))  # NOTE: redirects to /login app


@app.route("/login", methods=['GET','POST']) # NOTE: login page
def login():
    error = None
    if request.method == 'POST':  # NOTE: check if EU has clicked login on page
        if is_user(request.form['username'], request.form['password']): # NOTE: checks if EU is correct
            session["logged_in"] = True # NOTE: sets the session to logged in, allows the EU to continue to the main page without being redirected
            return redirect(url_for('main')) # NOTE: is correct redicects EU to main page
        else: # NOTE: if the password and username are incorrect
            error = "Incorrect username or password" # NOTE: sets error message for EU on login page
    return render_template('login.html', error=error) # NOTE: renders loginpage template for EU


@app.route("/logout") #when EU clicks logout button is redirected to this page
def logout():
    session.pop("logged_in", None) #removes EU's session
    return redirect(url_for('login')) # moves EU to login page





@app.route("/main", methods=['GET', 'POST']) # NOTE: main page
def main():
    if session.get("logged_in") == True:
        table = None
        date = None
        if request.method == 'POST':
            if request.form['date'] != "":
                date = dateparser.parse(request.form['date'], settings = {'DATE_ORDER': 'DMY'}).strftime("%Y-%m-%d")
                items = sort_customers(get_file(date))
                table = ItemTable(items)
        return render_template("main.html", table = table)
            #sort_contacts(people)
    else:
        return redirect(url_for('login'))

@app.route("/send", methods=['GET','POST'])
def send():
    with mail.connect() as conn:
        for usr in customer_list:
            message = 'Hi, %s! Just a reminder that you have an appointment on the %s at %s. Thanks!' %(FName, date, Time)
            subject = 'Hair Cut Reminder'
            msg = Message(recipients=Email,
                          body=message,
                          subject=subject)
            conn.send(msg)

    return redirect(url_for('logout'))



if __name__ == "__main__":
    app.run(debug=False)
