from flask import Flask, render_template, redirect, url_for, request, session
#from flask_table import Table, Col
import hashlib
import os
import dateparser

app = Flask(__name__)


app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"


users = {
    'admin':'admin',
    'lachlan':'mod',
}



def is_user(username, password):
    global user_auth
    for key in users:
        if key == username:
            if users[key] == password:
                return True
    return False


#def sort_contacts(people):




@app.route("/") # NOTE: auto firts app that flask runs, redirects auto to login app
def move():
    return redirect(url_for("login"))  # NOTE: redirects to /login app


@app.route("/login", methods=['GET','POST']) # NOTE: login page
def login():
    error = None
    if request.method == 'POST':  # NOTE: check if user has clicked login on page
        if is_user(request.form['username'], request.form['password']): # NOTE: checks if usr is correct
            session["logged_in"] = True
            return redirect(url_for('main')) # NOTE: is correct redicects usr to main page
        else:
            error = "Incorrect username or password"
    return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for('login'))





@app.route("/main", methods=['GET', 'POST']) # NOTE: main page
def main():
    customers = None
    if session.get("logged_in") == True:
        date = None
        if request.method == 'POST':
            date = dateparser.parse(request.form['date'], settings = {'DATE_ORDER': 'DMY'}).strftime("%Y-%m-%d")
            file_name = date + ".txt"
            file = open("static/dates/" + date, 'r')
            customers = file.read()
            file.close()
        return render_template("main-page.html", customers=customers)
            #sort_contacts(people)
    else:
        return redirect(url_for('login'))






if __name__ == "__main__":
    app.run(debug=True)
