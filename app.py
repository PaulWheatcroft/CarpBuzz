import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/get_fisheries")
def get_fisheries():
    fisheries = mongo.db.fisheries.contact.find()
    facilities = list(mongo.db.fisheries.facilities.find())
    tickets = list(mongo.db.fisheries.tickets.find())
    payments = list(mongo.db.fisheries.payment.find())
    return render_template(
        "fisheries.html", fisheries=fisheries, facilities=facilities,
        tickets=tickets, payments=payments)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if the email address already exists
        existing_email = mongo.db.accounts.find_one(
            {"email": request.form.get("email").lower()})

        if existing_email:
            flash("That email address is already in use")
            return redirect(url_for("register"))

        register = {
            "email": request.form.get("email").lower(),
            "fname": request.form.get("fname").lower(),
            "lname": request.form.get("lname").lower(),
            "username": request.form.get("username"),
            "password": generate_password_hash(request.form.get("password")),
            "is_admin": bool(False)
        }
        mongo.db.accounts.insert_one(register)

        flash("Your account has been registered. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if the email exists
        existing_user = mongo.db.accounts.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            # check hashed passwords match
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("email")
                flash(f"Welcome {session['user']}")
                return redirect(url_for("profile", user=session["user"]))
            else:
                # Invalid password
                flash("Incorrrect email and or password")
                return redirect(url_for("login"))

        else:
            # Invalid password
            flash("Incorrrect email and or password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<user>", methods=["GET", "POST"])
def profile(user):
    username = mongo.db.accounts.find_one(
        {"email": user})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Remove all sessions cookies
    flash("You have been successfully logged out")
    session.clear()
    return redirect(url_for("login"))


@app.route("/add_fishery", methods=["GET", "POST"])
def add_fishery():
    return render_template("add_fishery.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
