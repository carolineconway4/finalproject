from flask import Flask, render_template, request, flash, session, redirect
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import re
from flask_mail import Mail, Message
import os

from helpers import usd

app = Flask(__name__)
app.secret_key = "super secret key"

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")

# Set password for password-protected knitter page
password = "KnitByCC123!"

#set up for using mail
app.config["MAIL_DEFAULT_SENDER"] = "knit.by.cc@gmail.com"
app.config["MAIL_PASSWORD"] = os.environ.get("password")
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "KnitByCC"
mail = Mail(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


#definte store route
@app.route("/store")
def store():
    return render_template("store.html")

#define about us route
@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

#define contact us route
@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route("/dogsweaters", methods=["GET", "POST"])
def dogsweaters():

    # show order page and form
    if request.method == "GET":
        return render_template("dogsweater.html")

    if request.method == "POST":

        # check primary color inputted
        if not request.form.get("Color1"):

            # flash error message if no primary color inputted
            flash('Must include primary color!')
            return render_template("dogsweater.html")

        # check secondary color inputted
        if not request.form.get("Color2"):

            # flash error message if no secondary color inputted
            flash('Must include secondary color!')
            return render_template("dogsweater.html")

        try:
            #if user_id has been established, add order to cart
            if session["user_id"] != []:
                # add order to cart
                description = 'The primary color is {} and the secondary color is {}. The measurements are - Neck: {} in, Chest: {} in, Length: {} in.'.format(
                    request.form.get("Color1"), request.form.get("Color2"), str(request.form.get("Neck")), str(request.form.get("Chest")), str(request.form.get("BodyLength")))
                db.execute("INSERT INTO cart(session_id, item, description, quantity, price) VALUES(?, ?, ?, ?, ?)", session["user_id"], "dog sweater", description, request.form.get("Quantity"), "60")

                # tell user order was added to cart
                flash('Order added to cart!')
                return render_template("dogsweater.html")

            #if not logged in, tell user cannot add item to cart
            else:
                flash('Must be logged in to submit order!')
                return render_template("login.html")

        #if not logged in, tell user cannot add item to cart
        except KeyError:
            flash('Must be logged in to submit order!')
            return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    # will be post if submitting registration
    if request.method == "POST":

        # check username, password, and password confirmation provdided
        if not request.form.get("username"):
            flash("Must provide username!")
            return render_template("register.html")
        else:
            username = request.form.get("username")

        if not request.form.get("password"):
            flash("Must provide password!")
            return render_template("register.html")
        else:
            password = request.form.get("password")

        if not request.form.get("confirmation"):
            flash("Must confirm password!")
            return render_template("register.html")
        else:
            confirmation = request.form.get("confirmation")

        # check password and password confirmation match
        if password != confirmation:
            flash("Passwords must match!")
            return render_template("register.html")

        # Ensure password is at least 8 characters long
        if len(request.form.get("password")) < 8:
            flash("Password must be at least 8 characters long!")
            return render_template("register.html")

        # iterate over string to see if password contains a number
        # example of "any" with "isdigit" from https://www.delftstack.com/howto/python/how-to-check-a-string-contains-a-number-or-not-in-python/
        if any(chr.isdigit() for chr in request.form.get("password")) == False:
            flash("Password must contain a digit!")
            return render_template("register.html")

        # check to make sure the password includes a special character
        check = False
        if any(not char.isalnum() for char in request.form.get("password")):
            check = True

        if check == False:
            flash("Password must contain a special character!")
            return render_template("register.html")

        # check username not already taken
        current_usernames = []
        current_usernames = db.execute(
            "SELECT username FROM users WHERE username = ?", username)

        # if found a match for username, return error message
        if len(current_usernames) != 0:
            flash("Username already taken@")
            return render_template("register.html")

        # once user confirmed, add to database
        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)",
                   username, generate_password_hash(password))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to log in
        return render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password!")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("You are logged in!")
        return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/mittens", methods=["GET", "POST"])
def mittens():

    # show order page and form
    if request.method == "GET":
        return render_template("mittens.html")

    if request.method == "POST":

        # check color inputted
        if not request.form.get("Color1"):

            # flash error message if no primary color inputted
            flash('Must include color!')
            return render_template("mittens.html")

        # check size inputted
        if not request.form.get("Size"):

            # flash error message if no size inputted
            flash('Must include size!')
            return render_template("mittens.html")

        try:
            if session["user_id"] != []:
                # add order to cart
                description = 'The mitten color is {} and the size is {}.'.format(
                    request.form.get("Color1"), request.form.get("Size"))
                db.execute("INSERT INTO cart(session_id, item, description, quantity, price) VALUES(?, ?, ?, ?, ?)",
                           session["user_id"], "mittens", description, request.form.get("Quantity"), "30")

                # tell user order was added to cart
                flash('Order added to cart!')
                return render_template("mittens.html")

            #don't add to cart if user not logged in
            else:
                flash('Must be logged in to submit order!')
                return render_template("login.html")

        #don't add to cart if user not logged in
        except KeyError:
            flash('Must be logged in to submit order!')
            return render_template("login.html")


@app.route("/blankets", methods=["GET", "POST"])
def blankets():

    # show order page and form
    if request.method == "GET":
        return render_template("blanket.html")

    if request.method == "POST":

        # check color inputted
        if not request.form.get("Color1"):

            # flash error message if no primary color inputted
            flash('Must include color!')
            return render_template("blanket.html")

        # check size inputted
        if not request.form.get("Size"):

            # flash error message if no secondary color inputted
            flash('Must include size!')
            return render_template("blanket.html")

        #set prices based upon size selected
        if request.form.get("Size") == "Twin":
            price = 100

        if request.form.get("Size") == "Queen":
            price = 150

        if request.form.get("Size") == "King":
            price = 200

        try:
            if session["user_id"] != []:
                # add order to cart
                description = 'The blanket color is {} and the size is {}.'.format(
                    request.form.get("Color1"), request.form.get("Size"))
                db.execute("INSERT INTO cart(session_id, item, description, quantity, price) VALUES(?, ?, ?, ?, ?)",
                           session["user_id"], "blanket", description, request.form.get("Quantity"), price)

                # tell user order was added to cart
                flash('Order added to cart!')
                return render_template("blanket.html")

            #must be logged in to submit order
            else:
                flash('Must be logged in to submit order!')
                return render_template("login.html")

        #must be logged in to submit order
        except KeyError:
            flash('Must be logged in to submit order!')
            return render_template("login.html")


@app.route("/sweaters", methods=["GET", "POST"])
def sweaters():

    # show order page and form
    if request.method == "GET":
        return render_template("sweater.html")

    if request.method == "POST":

        # check primary color inputted
        if not request.form.get("Color1"):

            # flash error message if no primary color inputted
            flash('Must include primary color!')
            return render_template("sweater.html")

        # check secondary color inputted
        if not request.form.get("Color2"):

            # flash error message if no primary color inputted
            flash('Must include secondary color!')
            return render_template("sweater.html")

        # check size inputted
        if not request.form.get("Size"):

            # flash error message if no secondary color inputted
            flash('Must include size!')
            return render_template("sweater.html")

        try:
            if session["user_id"] != []:
                # add order to cart
                description = 'The primary color is {}, the secondary color is {}, and the size is {}.'.format(
                    request.form.get("Color1"), request.form.get("Color2"), request.form.get("Size"))
                db.execute("INSERT INTO cart(session_id, item, description, quantity, price) VALUES(?, ?, ?, ?, ?)",
                           session["user_id"], "sweater", description, request.form.get("Quantity"), "115")

                # tell user order was added to cart
                flash('Order added to cart!')
                return render_template("sweater.html")

            #must be logged in to submit order
            else:
                flash('Must be logged in to submit order!')
                return render_template("login.html")

        #must be logged in to submit order
        except KeyError:
            flash('Must be logged in to submit order!')
            return render_template("login.html")


@app.route("/hats", methods=["GET", "POST"])
def hats():

    # show order page and form
    if request.method == "GET":
        return render_template("hat.html")

    if request.method == "POST":

        # check primary color inputted
        if not request.form.get("Color1"):

            # flash error message if no primary color inputted
            flash('Must include primary color!')
            return render_template("hat.html")

        # check secondary color inputted
        if not request.form.get("Color2"):

            # flash error message if no primary color inputted
            flash('Must include secondary color!')
            return render_template("hat.html")

        # check size inputted
        if not request.form.get("Size"):

            # flash error message if no secondary color inputted
            flash('Must include size!')
            return render_template("hat.html")

        # check college inputted
        if not request.form.get("School"):

            # flash error message if no secondary color inputted
            flash('Must include school!')
            return render_template("hat.html")

        try:
            if session["user_id"] != []:
                # add order to cart
                description = 'The primary color is {}, the secondary color is {}, the size is {}, and the school is {}.'.format(
                    request.form.get("Color1"), request.form.get("Color2"), request.form.get("Size"), request.form.get("School"))
                db.execute("INSERT INTO cart(session_id, item, description, quantity, price) VALUES(?, ?, ?, ?, ?)",
                           session["user_id"], "hat", description, request.form.get("Quantity"), "25")

                # tell user order was added to cart
                flash('Order added to cart!')
                return render_template("hat.html")

            #must be logged in to submit order
            else:
                flash('Must be logged in to submit order!')
                return render_template("login.html")

        #must be logged in to submit order
        except KeyError:
            flash('Must be logged in to submit order!')
            return render_template("login.html")


@app.route("/cart", methods=["GET", "POST"])
def cart():

    if request.method == "GET":

        try:
            if session["user_id"] != []:
                # pull items from cart, increment, and display
                cart = db.execute("SELECT * FROM cart WHERE session_id = ?", session["user_id"])

                # initialize value for total price
                total_price = 0

                # calculate item price and total price
                for row in cart:
                    row["price"] = int(row["price"]) * int(row["quantity"])
                    total_price = total_price + row["price"]

                # render cart
                return render_template("cart.html", cart=cart, total_price=total_price)

            else:
                flash('Must be logged in to view cart!')
                return render_template("index.html")

        except KeyError:
            flash('Must be logged in to view cart!')
            return render_template("index.html")

    if request.method == "POST":

        # pull items from cart for user
        cart = db.execute("SELECT * FROM cart WHERE session_id = ?", session["user_id"])

        # iterate over items from cart
        for row in cart:

            # insert items in cart into projects table
            db.execute("INSERT INTO new_projects(session_id, item, quantity, price, description) VALUES(?, ?, ?, ?, ?)", session["user_id"], row["item"], row["quantity"], row["price"], row["description"])

        # delete items from cart
        db.execute("DELETE FROM cart WHERE session_id = ?", session["user_id"])

        #get user's email and send confirmation message
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        email = user[0]["username"]
        message = Message("Your order has been submitted!", recipients=[email])
        mail.send(message)

        # redirect to successful order page
        return render_template("success.html")


@ app.route("/delete", methods=["GET", "POST"])
def delete():

    #delete row associated with the delete button the user pressed
    if request.method == "POST":
        
        #get id of row the user wants to delete from cart
        id = request.form.get("Row_Delete")
        
        #delete from cart table
        db.execute("DELETE FROM cart WHERE key = ?", id)
        
        #redisplay cart page with the updated table
        return redirect("/cart")


@app.route("/knitterlocked", methods=["GET", "POST"])
def knitterlocked():

    if request.method == "GET":

        # display password to enter knitter page
        return render_template("knitterlocked.html")

    if request.method == "POST":

        # if password wrong, display error message
        if request.form.get("password") != password:
            flash("Password is incorrect")
            return redirect("/knitterlocked")

        # if password right, continue to log in page!
        else:
            return redirect("/knitterlogin")


@app.route("/knitterlogin", methods=["GET", "POST"])
def knitterlogin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username!")
            return render_template("knitterlogin.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password!")
            return render_template("knitterlogin.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM knitters WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password!")
            return render_template("knitterlogin.html")

        # Remember which user has logged in
        session["knitter_user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("You are logged in!")
        return redirect("/knitterindex")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("knitterlogin.html")


@app.route("/knitterindex", methods=["GET", "POST"])
def knitterindex():

    # populate tables for knitter index page
    if request.method == "GET":

        # get unclaimed projects
        new_projects = db.execute(
            "SELECT * FROM new_projects WHERE knitter IS NULL")
        for row in new_projects:
            row["price"] = int(row["price"]) * int(row["quantity"])
            customer = db.execute(
                "SELECT username FROM users WHERE id = ?", row["session_id"])
            row["email"] = customer[0]["username"]

        # get knitter's projects
        my_projects = db.execute(
            "SELECT * FROM new_projects WHERE knitter = ?", session["knitter_user_id"])
        for row in my_projects:
            row["price"] = int(row["price"]) * int(row["quantity"])
            customer = db.execute("SELECT username FROM users WHERE id = ?", row["session_id"])
            row["email"] = customer[0]["username"]

        return render_template("knitterindex.html", new_projects=new_projects, my_projects=my_projects)


@app.route("/knitterregister", methods=["GET", "POST"])
def knitterregister():

    # will be post if submitting registration
    if request.method == "POST":

        # check username, password, and password confirmation provdided
        if not request.form.get("username"):
            flash("Must provide username!")
            return render_template("knitterregister.html")
        else:
            username = request.form.get("username")

        if not request.form.get("password"):
            flash("Must provide password!")
            return render_template("knitterregister.html")
        else:
            password = request.form.get("password")

        if not request.form.get("confirmation"):
            flash("Must confirm password!")
            return render_template("knitterregister.html")
        else:
            confirmation = request.form.get("confirmation")

        # check password and password confirmation match
        if password != confirmation:
            flash("Passwords must match!")
            return render_template("knitterregister.html")

        # Ensure password is at least 8 characters long
        if len(request.form.get("password")) < 8:
            flash("Password must be at least 8 characters long!")
            return render_template("knitterregister.html")

        # iterate over string to see if password contains a number
        # example of "any" with "isdigit" from https://www.delftstack.com/howto/python/how-to-check-a-string-contains-a-number-or-not-in-python/
        if any(chr.isdigit() for chr in request.form.get("password")) == False:
            flash("Password must contain a digit!")
            return render_template("knitterregister.html")

        # check to make sure the password includes a special character
        check = False
        if any(not char.isalnum() for char in request.form.get("password")):
            check = True

        if check == False:
            flash("Password must contain a special character!")
            return render_template("knitterregister.html")

        # check username not already taken
        current_usernames = []
        current_usernames = db.execute(
            "SELECT username FROM knitters WHERE username = ?", username)

        # if found a match for username, return error message
        if len(current_usernames) != 0:
            flash("Username already taken!")
            return render_template("knitterregister.html")

        # once user confirmed, add to database
        db.execute("INSERT INTO knitters(username, hash) VALUES(?, ?)",
                   username, generate_password_hash(password))

        # Query database for username
        rows = db.execute(
            "SELECT * FROM knitters WHERE username = ?", username)

        # Remember which user has logged in
        session["knitter_user_id"] = rows[0]["id"]

        # Redirect user to log in
        flash("You have successfully registered as a knitter, please log in!")
        return redirect("/knitterlogin")

    else:
        return render_template("knitterregister.html")


@ app.route("/accept", methods=["GET", "POST"])
def accept():

    if request.method == "POST":
        id = request.form.get("Row_Accept")
        
        #send email telling customer their project has been accepted
        #get user's email and send confirmation message
        info = db.execute("SELECT * FROM new_projects WHERE id = ?", id)
        user_id = info[0]["session_id"]
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        email = user[0]["username"]
        message = Message("Your order has been accepted by a knitter!", recipients=[email])
        mail.send(message)

        #update table with knitter id
        db.execute("UPDATE new_projects SET knitter = ? WHERE id = ?", session["knitter_user_id"], id)

        return redirect("/knitterindex")


@ app.route("/complete", methods=["GET", "POST"])
def complete():

    if request.method == "POST":
        
        #get information of project completed
        id = request.form.get("Row_Complete")
        completed_project = db.execute("SELECT * FROM new_projects WHERE id = ?", id)

        #set values of the completed project
        session_id = completed_project[0]["session_id"]
        item = completed_project[0]["item"]
        quantity = completed_project[0]["quantity"]
        price = completed_project[0]["price"]
        description = completed_project[0]["description"]
        knitter = completed_project[0]["knitter"]

        #send email telling user their project is completed
        info = db.execute("SELECT * FROM new_projects WHERE id = ?", id)
        user_id = info[0]["session_id"]
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        email = user[0]["username"]
        message = Message("Your order has been completed!", recipients=[email])
        mail.send(message)

        #add project to completed projects table
        db.execute("INSERT INTO completed_projects(session_id, item, quantity, price, description, knitter) VALUES(?, ?, ?, ?, ?, ?)", session_id, item, quantity, price, description, knitter)
        
        #delete project from new_projects table
        db.execute("DELETE FROM new_projects WHERE id = ?", id)
        return redirect("/knitterindex")
