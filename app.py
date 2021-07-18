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

# The websites initial view is a list of fisheries
@app.route("/")
@app.route("/get_fisheries")
def get_fisheries():
    # Fishery data is kept across 4 sub-collections
    fisheries = list(mongo.db.fisheries.contact.find())
    facilities = list(mongo.db.fisheries.facilities.find())
    tickets = list(mongo.db.fisheries.tickets.find())
    payments = list(mongo.db.fisheries.payment.find())
    return render_template(
        "fisheries.html", fisheries=fisheries, facilities=facilities,
        tickets=tickets, payments=payments)

# Using the checkboxes on the main fisheries page the results can be filtered
@app.route("/filter_fisheries", methods=["GET", "POST"])
def filter_fisheries():
    filter_list = []
    if bool(request.form.get("wiltshire")):
        filter_list.append({"county": "wiltshire"})
    if bool(request.form.get("gloucestershire")):
        filter_list.append({"county": "south gloucestershire"})
    if bool(request.form.get("north_somerset")):
        filter_list.append({"county": "north somerset"})
    if bool(request.form.get("somerset")):
        filter_list.append({"county": "somerset"})
    if bool(request.form.get("dorset")):
        filter_list.append({"county": "dorset"})
    if bool(request.form.get("devon")):
        filter_list.append({"county": "devon"})
    if bool(request.form.get("cornwall")):
        filter_list.append({"county": "cornwall"})
    if len(filter_list) == 0:
        fisheries = list(mongo.db.fisheries.contact.find())

    else:
        fisheries = list(mongo.db.fisheries.contact.find({"$or":filter_list}))

    facilities = list(mongo.db.fisheries.facilities.find())
    tickets = list(mongo.db.fisheries.tickets.find())
    payments = list(mongo.db.fisheries.payment.find())

    return render_template(
        "fisheries.html", fisheries=fisheries, facilities=facilities,
        tickets=tickets, payments=payments, filter_list=filter_list)


@app.route("/clear_filter")
def clear_filter():
    return redirect(url_for("get_fisheries"))

# Register for a user account
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
            "is_admin": False
        }
        mongo.db.accounts.insert_one(register)

        flash("Your account has been registered. Please log in.", 'info')
        return redirect(url_for("login"))

    return render_template("register.html")

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get the existing account if it exists
        existing_user = mongo.db.accounts.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            # check hashed passwords match (werkzeug)
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                # Add a session item "user" 
                session["user"] = str(existing_user["_id"])
                # If the user is an admin add this to the session object
                if existing_user["is_admin"]:
                    session["is_admin"] = True
                flash(f"Welcome {existing_user['username']}", 'info')
                # The default is to return to the main fisheries page
                return redirect(url_for("get_fisheries", user=session["user"]))
            else:
                # Invalid password
                flash("Incorrrect email and or password", 'error')
                return redirect(url_for("login"))

        else:
            # Invalid account
            flash("Incorrrect email and or password", 'error')
            return redirect(url_for("login"))

    return render_template("login.html")

# User profile page
@app.route("/profile/<user>", methods=["GET", "POST"])
def profile(user):
    if request.method == "POST":
        # Get the current user profile
        profile = mongo.db.accounts.find_one({"_id": ObjectId(user)})
        # If a user changes items in the profile capture this and update the profile
        updated_profile = { "$set":
        {
            "email": request.form.get("email").lower(),
            "fname": request.form.get("fname").lower(),
            "lname": request.form.get("lname").lower(),
            "username": request.form.get("username"),
            "password": generate_password_hash(request.form.get("password")),
            "is_admin": False
        }
        }
        mongo.db.accounts.update_one(profile, updated_profile)

    account = mongo.db.accounts.find_one(
        {"_id": ObjectId(user)})
    # The profile page displays a summary of fish caught
    catches = list(mongo.db.catch.fish.find({"account_id": session["user"]}))
    sorted_catches = sorted(catches, key=lambda catch: catch["weight"], reverse=True)
    total_fish_weight = 0
    if len(catches) == 0:
        average_fish_weight = 0
        return render_template("profile.html", account=account, catches=catches,
            total_fish_weight=total_fish_weight, average_fish_weight=average_fish_weight)

    else:    
        for catch in catches:
            fish_weight = int(catch["weight"])
            # Sum the total weight caught
            total_fish_weight = fish_weight + total_fish_weight
            # Average of the total weight caught
            average_fish_weight = total_fish_weight/len(catches)
        # Make sure the person executing this function is a session user
        if session["user"]:
            return render_template("profile.html", account=account, catches=catches,
            total_fish_weight=total_fish_weight, average_fish_weight=average_fish_weight, sorted_catches=sorted_catches)

    return redirect(url_for("login"))

# Logging a user out of the site
@app.route("/logout")
def logout():
    # Remove all sessions cookies
    session.clear()
    flash('You have been successfully logged out', 'info')
    return redirect(url_for("login"))

# ################### Fishery Functions ######################
@app.route("/add_fishery", methods=["GET", "POST"])
def add_fishery():
    # Make sure the person executing this function is an admin
    if "is_admin" in mongo.db.accounts.find_one({"_id": ObjectId(session["user"])}):
        if request.method == "POST":
            # create fishery contact dict
            fishery_contact = {
                "name": request.form.get("name"),
                "address": request.form.get("address").lower(),
                "town": request.form.get("town").lower(),
                "county": request.form.get("county").lower(),
                "postcode": request.form.get("postcode").upper(),
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
    
    else:
        flash('You are not authorised for this page', 'warning')
        return redirect(url_for("get_fisheries"))


@app.route("/edit_fishery/<fishery_id>", methods=["GET", "POST"])
def edit_fishery(fishery_id):
    # Make sure the person executing this function is an admin
    if "is_admin" in mongo.db.accounts.find_one({"_id": ObjectId(session["user"])}):
        if request.method == "POST":
            # create fishery contact dict
            submit_fishery_contact = {
                "name": request.form.get("name").lower(),
                "address": request.form.get("address").lower(),
                "town": request.form.get("town").lower(),
                "county": request.form.get("county").lower(),
                "postcode": request.form.get("postcode").upper(),
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

    else:
        flash('You are not authorised for this page', 'warning')
        return redirect(url_for("get_fisheries"))


@app.route("/delete_fishery/<fishery_id>")
def delete_fishery(fishery_id):
    # Make sure the person executing this function is an admin
    if "is_admin" in mongo.db.accounts.find_one({"_id": ObjectId(session["user"])}):
        # add disable to the contact document to preserve report and catch history
        disable_fishery_contact = mongo.db.fisheries.contact.find_one({"_id": ObjectId(fishery_id)})
        disable_fishery_contact["disabled"] = True
        mongo.db.fisheries.contact.update_one({"_id": ObjectId(fishery_id)}, { "$set": disable_fishery_contact })
        # delete the rest
        mongo.db.fisheries.facilities.delete_one({"fishery_id": fishery_id})
        mongo.db.fisheries.payment.delete_one({"fishery_id": fishery_id})
        mongo.db.fisheries.tickets.delete_one({"fishery_id": fishery_id})
        mongo.db.reviews.delete_many({"fishery_id": fishery_id})
        return redirect(url_for("get_fisheries"))
    
    else:
        flash('You are not authorised for this page', 'warning')
        return redirect(url_for("get_fisheries"))

# ################### Review Functions ######################
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
    # Make sure the person executing this function is a session user
    if session["user"]:
        if request.method == "POST":
            review = {
                "fishery_id": str(fishery_id),
                "account_id": session["user"],
                "rating": int(request.form.get("review_rating")),
                "heading": request.form.get("review_heading"),
                "main_text": request.form.get("review_text"),
                "pro_text": request.form.get("pro_text"),
                "con_text": request.form.get("con_text"),
                "date": datetime.strptime(request.form.get("review_date"), '%d-%b-%Y')
            }
            # insert review
            mongo.db.reviews.insert_one(review)
            flash('You have successfully added the review', 'success')
            return redirect(url_for('reviews', fishery_id=review["fishery_id"]))

        fishery_contact = mongo.db.fisheries.contact.find_one(
            {"_id": ObjectId(fishery_id)})
        return render_template("add_review.html",
        fishery_contact=fishery_contact, fishery_id=fishery_id)

    else:
            flash('You are not authorised for this page', 'warning')
            return redirect(url_for("get_fisheries"))


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    fishery_review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    # Make sure the person executing this function is a session user
    if session["user"] == fishery_review["account_id"]:
        if request.method == "POST":
            updated_review = {
                "fishery_id": fishery_review['fishery_id'],
                "account_id": session["user"],
                "rating": int(request.form.get("review_rating")),
                "heading": request.form.get("review_heading"),
                "main_text": request.form.get("review_text"),
                "pro_text": request.form.get("pro_text"),
                "con_text": request.form.get("con_text"),
                "date": datetime.strptime(request.form.get("review_date"), '%d-%b-%Y')
            }
            # insert review
            mongo.db.reviews.update({"_id": ObjectId(review_id)}, updated_review)            
            flash('You have successfully updated the review', 'success')
            return redirect(url_for('reviews', fishery_id=fishery_review["fishery_id"]))

        fishery_review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
        fishery_contact = mongo.db.fisheries.contact.find_one(
            {"_id": ObjectId(fishery_review["fishery_id"])})    
        return render_template(
            "edit_review.html", fishery_review=fishery_review,
            fishery_contact=fishery_contact)

    else:
            flash('You are not authorised for this page', 'warning')
            return redirect(url_for("get_fisheries"))


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    fishery_review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    # Make sure the person executing this function is the person that wrote the review
    # or an admin
    if session["user"] == fishery_review["account_id"] or session["is_admin"]:
    # delete the review
        mongo.db.reviews.remove({"_id": ObjectId(review_id)})
        flash('Your review as been deleted', 'info')
        # If this is the user return them back to the reviews for that fishery
        if session["user"] == fishery_review["account_id"]:
            return redirect(url_for('reviews', fishery_id=fishery_review["fishery_id"]))
        # If the delete was created by an admin take the admin back to the moderation page
        elif session["is_admin"]:
            return redirect(url_for('moderate_reviews'))

    else:
        flash('You are not authorised for this page', 'warning')
        return redirect(url_for("get_fisheries"))

# Anyone can report a review to be reviewed due to its content
@app.route("/report_review/<review_id>")
def report_review(review_id):
    fishery_review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    # The following entry is added to the review document
    fishery_review["moderation"] = True
    mongo.db.reviews.update({"_id": ObjectId(review_id)}, fishery_review)
    flash("Thank you. This review has been submitted to the website administrators for review", 'info')    
    return redirect(url_for('reviews', fishery_id=fishery_review["fishery_id"]))


@app.route("/moderate_reviews")
def moderate_reviews():
    # Make sure the person executing this function is an admin
    if session["is_admin"]:
        fishery_reviews = list(mongo.db.reviews.find({"moderation": True}))
        if len(fishery_reviews) == 0:
            return render_template("moderation_reviews.html", fishery_reviews=fishery_reviews)

        else:
            accounts = []   
            for account_id in fishery_reviews:
                accounts.append({"_id": ObjectId(account_id["account_id"])})
            accounts_list = list(mongo.db.accounts.find({"$or":accounts}))
            return render_template("moderation_reviews.html", fishery_reviews=fishery_reviews,
            accounts_list=accounts_list)

    else:
        flash('You are not authorised for this page', 'warning')
        return redirect(url_for("get_fisheries"))   


@app.route("/keep_review/<review_id>")
def keep_review(review_id):
    # Make sure the person executing this function is an admin
    if session["is_admin"]:
        fishery_review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
        fishery_review.pop('moderation', True) 
        mongo.db.reviews.update({"_id": ObjectId(review_id)}, fishery_review)
        flash("Moderation flag removed", 'success')    
        return redirect(url_for('moderate_reviews'))

# ################### Report Functions ######################
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
    # Make sure the person executing this function is a session user
    if session["user"]:
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

    else:
            flash('You are not authorised for this page', 'warning')
            return redirect(url_for("get_fisheries"))


@app.route("/edit_report/<report_id>", methods=["GET", "POST"])
def edit_report(report_id):
    fishery_report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
    # Make sure the person executing this function the person that created the report
    if session["user"] == fishery_report["account_id"]:
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
                return redirect(url_for('reports', fishery_id=report["fishery_id"]))

            else:
                for catch in report_catches:
                    # each catch list item has it's own unique id name and label values
                    str_catch_id = str(catch["_id"])
                    marked_delete = bool(request.form.get(f"{str_catch_id}delete"))
                    if marked_delete:
                        mongo.db.catch.fish.delete_one({"_id": ObjectId(str_catch_id)})

                    else:
                        weight_lbs = int(request.form.get(f"{str_catch_id}weight_lbs")) *16
                        weight_oz = int(request.form.get(f"{str_catch_id}weight_oz"))
                        weight = weight_oz + weight_lbs
                        updated_catch = { "$set":
                        {
                            "report_id": report_id,
                            "account_id": session["user"],
                            "fishery_id": report["fishery_id"],
                            "fish": request.form.get(f"{str_catch_id}fish"),
                            "weight": weight,
                            "date": datetime.strptime(request.form.get(f"{str_catch_id}catch_date"), '%d-%b-%Y'),
                            "time": datetime.strptime(request.form.get(f"{str_catch_id}catch_time"), '%H:%M')
                        }
                        }
                        mongo.db.catch.fish.update(catch, updated_catch)
                return redirect(url_for('reports', fishery_id=report["fishery_id"]))
            

        report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
        report_catches = mongo.db.catch.fish.find({"report_id": report_id})
        fishery_contact = mongo.db.fisheries.contact.find_one({"_id": ObjectId(report["fishery_id"])}) 
        return render_template(
            "edit_report.html", report=report, report_catches=report_catches,
            fishery_contact=fishery_contact)

    else:
        flash('You are not authorised for this page', 'warning')
        return redirect(url_for("get_fisheries"))


@app.route("/delete_report/<report_id>")
def delete_report(report_id):
    report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
    # Make sure the person executing this function is the same person deleting it
    if session["user"] == report["account_id"]:
        mongo.db.catch.reports.delete_one({"_id": ObjectId(report_id)})
        mongo.db.catch.fish.delete_many({"report_id": report_id})
        flash('Your review as been deleted', 'info')    
        return redirect(url_for('reports', fishery_id=report["fishery_id"]))

    else:
        flash('You are not authorised for this page', 'warning')
        return redirect(url_for("get_fisheries"))


@app.route("/add_fish/<report_id>", methods=["GET", "POST"])
def add_fish(report_id):
    report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
    # Make sure the person executing this function is the same person that created the report
    if session["user"] == report["account_id"]:
        if request.method == "POST":
            fishery_contact = mongo.db.fisheries.contact.find_one({"_id": ObjectId(report["fishery_id"])})
            weight_lbs = int(request.form.get("weight_lbs")) *16
            weight_oz = int(request.form.get("weight_oz"))
            weight = weight_oz + weight_lbs
            catch = {
                "report_id": report_id,
                "account_id": session["user"],
                "fishery_id": report["fishery_id"],
                "fish": request.form.get("fish"),
                "weight": weight,
                "date": datetime.strptime(request.form.get("catch_date"), '%d-%b-%Y'),
                "time": datetime.strptime(request.form.get("catch_time"), '%H:%M')
            }
            mongo.db.catch.fish.insert_one(catch)
            report_catches = mongo.db.catch.fish.find({"report_id": report_id})
            return redirect(url_for('add_fish', report_id=report["_id"]))


        report = mongo.db.catch.reports.find_one({"_id": ObjectId(report_id)})
        report_catches = mongo.db.catch.fish.find({"report_id": report_id})
        fishery_contact = mongo.db.fisheries.contact.find_one({"_id": ObjectId(report["fishery_id"])})
        return render_template("add_fish.html", fishery_contact=fishery_contact,
            report=report, report_catches=report_catches)

    else:
            flash('You are not authorised for this page', 'warning')
            return redirect(url_for("get_fisheries"))

# ################### Contact and Message Functions ######################
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        contact_form = {
            "email": request.form.get("email"),
            "heading": request.form.get("heading"),
            "text": request.form.get("contact_text")
        }
        mongo.db.messages.insert(contact_form)
        flash('Your message has been sent. Thank you for getting in touch', 'info')
        return render_template("contact.html")

    return render_template("contact.html")


@app.route("/messages")
def messages():
    messages = list(mongo.db.messages.find())
    return render_template("messages.html", messages=messages)


@app.route("/hide_message/<message_id>")
def hide_message(message_id):
    # Make sure the person executing this function is an admin
    if session["is_admin"]:
        message = mongo.db.messages.find_one({"_id": ObjectId(message_id)})
        message["hidden"] = True
        mongo.db.messages.update({"_id": ObjectId(message_id)}, message)
        return redirect(url_for('messages'))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True) 
