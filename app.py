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
    if request.method == "POST":
        # create fishery contact dict
        fishery_contact = {
            "name": request.form.get("name"),
            "address": request.form.get("address"),
            "town": request.form.get("town"),
            "postcode": request.form.get("postcode"),
            "telephone": request.form.get("telephone"),
            "website": request.form.get("website"),
            "facebook": request.form.get("facebook")
        }
        # insert the fishery contact dict and get the inserted id
        fishery_id = mongo.db.fisheries.contact.insert_one(
            fishery_contact).inserted_id
        # get the ticket prices. Convert "" to 0
        if (request.form.get("day_dayonly") == ""):
            day_dayonly = 0.00
        else:
            day_dayonly = float(request.form.get("day_dayonly"))
        if (request.form.get("day_daynight") == ""):
            day_daynight = 0.00
        else:
            day_daynight = float(request.form.get("day_daynight"))
        if (request.form.get("lake_daynight") == ""):
            lake_daynight = 0.00
        else:
            lake_daynight = float(request.form.get("lake_daynight"))
        if (request.form.get("syndicate_daynight") == ""):
            syndicate_daynight = 0.00
        else:
            syndicate_daynight = float(request.form.get("syndicate_daynight"))
        if (request.form.get("club_dayonly") == ""):
            club_dayonly = 0.00
        else:
            club_dayonly = float(request.form.get("club_dayonly"))
        if (request.form.get("club_daynight") == ""):
            club_daynight = 0.00
        else:
            club_daynight = float(request.form.get("club_daynight"))
        if (request.form.get("season_dayonly") == ""):
            season_dayonly = 0.00
        else:
            season_dayonly = float(request.form.get("season_dayonly"))
        if (request.form.get("season_daynight") == ""):
            season_daynight = 0.00
        else:
            season_daynight = float(request.form.get("season_daynight"))
        # create tickets dict
        fishery_tickets = {
            "fishery_id": str(fishery_id),
            "day_dayonly": day_dayonly,
            "day_daynight": day_daynight,
            "lake_daynight": lake_daynight,
            "syndicate_daynight": syndicate_daynight,
            "club_dayonly": club_dayonly,
            "club_daynight": club_daynight,
            "season_dayonly": season_dayonly,
            "season_daynight": season_daynight
        }
        # insert ticket prices
        mongo.db.fisheries.tickets.insert_one(fishery_tickets)
        # get the payment and booking details
        fishery_payment = {
            "fishery_id": str(fishery_id),
            "on_the_bank": bool(request.form.get("on_the_bank")),
            "on_arrival": bool(request.form.get("on_arrival")),
            "book_online": bool(request.form.get("book_online")),
            "book_on_phone": bool(request.form.get("book_on_phone")),
            "tackle_shop": bool(request.form.get("tackle_shop"))
        }
        # insert payment and booking details
        mongo.db.fisheries.payment.insert_one(fishery_payment)
        # get fishery facilities
        fishery_facilities = {
            "fishery_id": str(fishery_id),
            "lake_type": request.form.get("lake_type"),
            "stock_size": int(request.form.get("stock_size")),
            "rods": request.form.get("rods"),
            "onsite_tackle_shop": bool(request.form.get("onsite_tackle_shop")),
            "toilet": bool(request.form.get("toilet")),
            "shower": bool(request.form.get("shower")),
            "cafe": bool(request.form.get("cafe")),
            "fridge": bool(request.form.get("fridge")),
            "tackle_rent": bool(request.form.get("tackle_rent")),
            "lakeside_huts": bool(request.form.get("lakeside_huts")),
            "tuition": bool(request.form.get("tuition")),
            "drive_to_swim": bool(request.form.get("drive_to_swim")),
            "takeaway_delivery": bool(request.form.get("takeaway_delivery")),
            "dogs_allowed": bool(request.form.get("dogs_allowed")),
            "parking": bool(request.form.get("parking"))
        }
        # insert payment and booking details
        mongo.db.fisheries.facilities.insert_one(fishery_facilities)
        return render_template("add_fishery.html")

    return render_template("add_fishery.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
