from datetime import date, datetime
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
            flash("That email address is already in use", 'warning')
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

        flash("Your account has been registered. Please log in.", 'error')
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
                session["user"] = str(existing_user["_id"])
                flash(f"Welcome {existing_user['username']}", 'info')
                return redirect(url_for("profile", user=session["user"]))
            else:
                # Invalid password
                flash("Incorrrect email and or password", 'error')
                return redirect(url_for("login"))

        else:
            # Invalid password
            flash("Incorrrect email and or password", 'error')
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<user>", methods=["GET", "POST"])
def profile(user):
    username = mongo.db.accounts.find_one(
        {"_id": ObjectId(user)})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Remove all sessions cookies
    session.clear()
    flash('You have been successfully logged out', 'info')
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
        flash('You have successfully added the fishery', 'success')
        return render_template("add_fishery.html")

    return render_template("add_fishery.html")


@app.route("/edit_fishery/<fishery_id>", methods=["GET", "POST"])
def edit_fishery(fishery_id):
    if request.method == "POST":
        # create fishery contact dict
        submit_fishery_contact = {
            "name": request.form.get("name"),
            "address": request.form.get("address"),
            "town": request.form.get("town"),
            "postcode": request.form.get("postcode"),
            "telephone": request.form.get("telephone"),
            "website": request.form.get("website"),
            "facebook": request.form.get("facebook")
        }
        # Update fishery contact details
        mongo.db.fisheries.contact.update(
            {"_id": ObjectId(fishery_id)}, submit_fishery_contact)
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
        submit_fishery_tickets = {
            "fishery_id": fishery_id,
            "day_dayonly": day_dayonly,
            "day_daynight": day_daynight,
            "lake_daynight": lake_daynight,
            "syndicate_daynight": syndicate_daynight,
            "club_dayonly": club_dayonly,
            "club_daynight": club_daynight,
            "season_dayonly": season_dayonly,
            "season_daynight": season_daynight
        }
        # update ticket prices
        mongo.db.fisheries.tickets.update(
            {"fishery_id": fishery_id}, submit_fishery_tickets)
        # get the payment and booking details
        submit_fishery_payment = {
            "fishery_id": fishery_id,
            "on_the_bank": bool(request.form.get("on_the_bank")),
            "on_arrival": bool(request.form.get("on_arrival")),
            "book_online": bool(request.form.get("book_online")),
            "book_on_phone": bool(request.form.get("book_on_phone")),
            "tackle_shop": bool(request.form.get("tackle_shop"))
        }
        # update payment and booking details
        mongo.db.fisheries.payment.update(
            {"fishery_id": fishery_id}, submit_fishery_payment)
        # get fishery facilities
        submit_fishery_facilities = {
            "fishery_id": fishery_id,
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
        # update payment and booking details
        mongo.db.fisheries.facilities.update(
            {"fishery_id": fishery_id}, submit_fishery_facilities)
        flash('You have successfully updated the fishery', 'success')
        return redirect(url_for("get_fisheries"))

    fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_id)})
    fishery_tickets = mongo.db.fisheries.tickets.find_one(
        {"fishery_id": fishery_id})
    fishery_payment = mongo.db.fisheries.payment.find_one(
        {"fishery_id": fishery_id})
    fishery_facilities = mongo.db.fisheries.facilities.find_one(
        {"fishery_id": fishery_id})
    return render_template(
        "edit_fishery.html",
        fishery_contact=fishery_contact,
        fishery_tickets=fishery_tickets,
        fishery_payment=fishery_payment,
        fishery_facilities=fishery_facilities)


@app.route("/delete_fishery/<fishery_id>")
def delete_fishery(fishery_id):
    mongo.db.fishery.contact.delete_one({"_id": ObjectId(fishery_id)})
    mongo.db.fishery.facilities.delete_one({"fishery_id": fishery_id})
    mongo.db.fishery.payment.delete_one({"fishery_id": fishery_id})
    mongo.db.fishery.tickets.delete_one({"fishery_id": fishery_id})
    mongo.db.reviews.delete_many({"fishery_id": fishery_id})
    fisheries = mongo.db.fisheries.contact.find()
    facilities = list(mongo.db.fisheries.facilities.find())
    tickets = list(mongo.db.fisheries.tickets.find())
    payments = list(mongo.db.fisheries.payment.find())
    return render_template(
        "fisheries.html", fisheries=fisheries, facilities=facilities,
        tickets=tickets, payments=payments)


@app.route("/reviews/<fishery_id>")
def reviews(fishery_id):
    fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_id)})
    fishery_reviews = mongo.db.reviews.find({"fishery_id": fishery_id})
    reviews = []
    # loop through the reviews and for each one retrieve the username for the account_id
    for doc in fishery_reviews:
        author_id = doc['account_id']
        username = mongo.db.accounts.find_one({"_id": ObjectId(author_id)})['username']
        doc.update({"username": username})
        reviews.append(doc)
        reviews.sort(key = lambda review_date:review_date['date'], reverse=True)
    return render_template(
        "reviews.html", fishery_contact=fishery_contact,
        reviews=reviews)


@app.route("/add_review/<fishery_id>", methods=["GET", "POST"])
def add_review(fishery_id):
    if request.method == "POST":
        review = {
            "fishery_id": str(fishery_id),
            "account_id": session["user"],
            "rating": int(request.form.get("review_rating")),
            "heading": request.form.get("review_heading"),
            "main_text": request.form.get("review_text"),
            "pro_text": request.form.get("pro_text"),
            "con_text": request.form.get("con_text"),
            "moderation": False,
            "date": datetime.strptime(request.form.get("review_date"), '%d-%b-%Y')
        }
        # insert review
        mongo.db.reviews.insert_one(review)
        flash('You have successfully added the review', 'success')
        fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_id)})
        fishery_reviews = mongo.db.reviews.find({"fishery_id": fishery_id})
        reviews = []
        # loop through the reviews and for each one retrieve the username for the account_id
        for doc in fishery_reviews:
            author_id = doc['account_id']
            username = mongo.db.accounts.find_one({"_id": ObjectId(author_id)})['username']
            doc.update({"username": username})
            reviews.append(doc)
            reviews.sort(key = lambda review_date:review_date['date'], reverse=True)
        return render_template("reviews.html", fishery_contact=fishery_contact,
        reviews=reviews)

    fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_id)})
    return render_template("add_review.html",
    fishery_contact=fishery_contact, fishery_id=fishery_id)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == "POST":
        fishery_review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
        updated_review = {
            "fishery_id": fishery_review['fishery_id'],
            "account_id": session["user"],
            "rating": int(request.form.get("review_rating")),
            "heading": request.form.get("review_heading"),
            "main_text": request.form.get("review_text"),
            "pro_text": request.form.get("pro_text"),
            "con_text": request.form.get("con_text"),
            "moderation": False,
            "date": datetime.strptime(request.form.get("review_date"), '%d-%b-%Y')
        }
        # insert review
        mongo.db.reviews.update({"_id": ObjectId(review_id)}, updated_review)            
        flash('You have successfully updated the review', 'success')
        fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_review["fishery_id"])})  
        fishery_reviews = mongo.db.reviews.find({"fishery_id": fishery_review['fishery_id']})
        reviews = []
        # loop through the reviews and for each one retrieve the username for the account_id
        for doc in fishery_reviews:
            author_id = doc['account_id']
            username = mongo.db.accounts.find_one({"_id": ObjectId(author_id)})['username']
            doc.update({"username": username})
            reviews.append(doc)
            reviews.sort(key = lambda review_date:review_date['date'], reverse=True)
        return render_template("reviews.html", fishery_contact=fishery_contact,
        reviews=reviews)

    fishery_review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_review["fishery_id"])})    
    return render_template(
        "edit_review.html", fishery_review=fishery_review,
        fishery_contact=fishery_contact)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    fishery_review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    # delete the review
    mongo.db.reviews.remove({"_id": ObjectId(review_id)})
    flash('Your review as been deleted', 'info')    
    fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_review["fishery_id"])})  
    fishery_reviews = mongo.db.reviews.find({"fishery_id": fishery_review['fishery_id']})
    reviews = []
    # loop through the reviews and for each one retrieve the username for the account_id
    for doc in fishery_reviews:
        author_id = doc['account_id']
        username = mongo.db.accounts.find_one({"_id": ObjectId(author_id)})['username']
        doc.update({"username": username})
        reviews.append(doc)
        reviews.sort(key = lambda review_date:review_date['date'], reverse=True)
    return render_template("reviews.html", fishery_contact=fishery_contact,
    reviews=reviews)


@app.route("/reports/<fishery_id>")
def reports(fishery_id):
    fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_id)})
    fishery_reports = list(mongo.db.catch.reports.find({"fishery_id": fishery_id}))
    fishery_catches = list(mongo.db.catch.fish.find({"fishery_id": fishery_id}))
    reports = []
    # loop through the reports and for each one retrieve the username for the account_id
    for report in fishery_reports:        
        author_id = report['account_id']
        username = mongo.db.accounts.find_one({"_id": ObjectId(author_id)})['username']
        report.update({"username": username})
        reports.append(report)
        reports.sort(key = lambda report_date:report_date['date'], reverse=True)
    return render_template(
        "reports.html", fishery_contact=fishery_contact,
        reports=reports, fishery_catches=fishery_catches)


@app.route("/add_report/<fishery_id>", methods=["GET", "POST"])
def add_report(fishery_id):
    if request.method == "POST":
        fishery_contact = mongo.db.fisheries.contact.find_one(
        {"_id": ObjectId(fishery_id)})
        report = {
            "fishery_id": fishery_id,
            "account_id": session["user"],
            "name": request.form.get("report_name"),
            "date": datetime.strptime(request.form.get("report_date"), '%d-%b-%Y'),
            "notes": request.form.get("report_notes")
        }
        mongo.db.catch.reports.insert_one(report)
        return redirect(url_for('add_fish', report_id=report["_id"]))

    fishery_contact = mongo.db.fisheries.contact.find_one({"_id": ObjectId(fishery_id)})    
    return render_template(
        "add_report.html", fishery_contact=fishery_contact)


@app.route("/edit_report/<report_id>", methods=["GET", "POST"])
def edit_report(report_id):
    if request.method == "POST":
        report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
        report_catches = list(mongo.db.catch.fish.find({"report_id": report_id}))
        updated_report = { "$set":
        {
            "fishery_id": report["fishery_id"],
            "account_id": session["user"],
            "name": request.form.get("report_name"),
            "date": datetime.strptime(request.form.get("report_date"), '%d-%b-%Y'),
            "notes": request.form.get("report_notes")
        }
        }
        mongo.db.catch.reports.update_one({"_id": ObjectId(report_id)}, updated_report)
        if not report_catches:
            print("Caught nothing but this error")

        else:
            for catch in report_catches:
                # each catch list item has it's own unique id name and label values
                str_catch_id = str(catch["_id"])
                updated_catch = { "$set":
                {
                    "report_id": report_id,
                    "account_id": session["user"],
                    "fishery_id": report["fishery_id"],
                    "fish": request.form.get(f"{str_catch_id}fish"),
                    "weight": float(request.form.get(f"{str_catch_id}weight")),
                    "date": datetime.strptime(request.form.get(f"{str_catch_id}catch_date"), '%d-%b-%Y'),
                    "time": datetime.strptime(request.form.get(f"{str_catch_id}catch_time"), '%H:%M')
                }
                }
                mongo.db.catch.fish.update(catch, updated_catch)

        print("")
        print(report["fishery_id"])
        print("")
        return redirect(url_for('reports', fishery_id=report["fishery_id"]))

    report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
    report_catches = mongo.db.catch.fish.find({"report_id": report_id})
    fishery_contact = mongo.db.fisheries.contact.find_one({"_id": ObjectId(report["fishery_id"])}) 
    return render_template(
        "edit_report.html", report=report, report_catches=report_catches,
        fishery_contact=fishery_contact)


@app.route("/add_fish/<report_id>", methods=["GET", "POST"])
def add_fish(report_id):
    if request.method == "POST":
        report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
        fishery_contact = mongo.db.fisheries.contact.find_one({"_id": ObjectId(report["fishery_id"])})
        catch = {
            "report_id": report_id,
            "account_id": session["user"],
            "fishery_id": report["fishery_id"],
            "fish": request.form.get("fish"),
            "weight": float(request.form.get("weight")),
            "date": datetime.strptime(request.form.get("catch_date"), '%d-%b-%Y'),
            "time": datetime.strptime(request.form.get("catch_time"), '%H:%M')
        }
        mongo.db.catch.fish.insert_one(catch)
        report_catches = mongo.db.catch.fish.find({"report_id": report_id})
        return render_template("add_fish.html", fishery_contact=fishery_contact,
        report=report, report_catches=report_catches)

    report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
    report_catches = mongo.db.catch.fish.find({"report_id": report_id})
    fishery_contact = mongo.db.fisheries.contact.find_one({"_id": ObjectId(report["fishery_id"])})
    return render_template("add_fish.html", fishery_contact=fishery_contact,
        report=report, report_catches=report_catches)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
