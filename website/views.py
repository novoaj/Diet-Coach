from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Item
from . import db
import json
totals = {}
views = Blueprint("views", __name__)

def calculate_totals(user):
    # will calculate user totals to display to home page
    totals = {}
    categories = ["cals", "fats", "protein", "carbs"]
    for category in categories:
        totals[category] = 0
    for item in user.items:
        totals["cals"] += item.cals
        totals["protein"] += item.protein
        totals["fats"] += item.fats
        totals["carbs"] += item.carbs
    totals["percent_intake"] = (totals["cals"]/user.recommended_intake) * 100
    
    return totals

@views.route("/", methods = ["GET", "POST"])
@login_required
def home():
    global totals
    # if logged in home page, if not get_started
    if request.method == "POST":
        item = request.form.get("item")
        cals = request.form.get("cals")        
        fats = request.form.get("fats")
        protein = request.form.get("protein")
        carbs = request.form.get("carbs")

        """
        validates that txt is a number
        """
        def validate(txt):
            return txt.strip().isnumeric()
        
        if (not item) or item == "":  # validate
            flash("invalid entrance for item", category="error")
        elif (not cals) or (not protein) or (not fats) or (not carbs):
            flash("calories, protein, fat, and carbs cannot be blank", category="error")
        elif cals == "" or fats  == "" or protein == "" or carbs == "":
            flash("calories, protein, fat, and carbs cannot be blank", category="error")
        elif not (validate(cals) and validate(fats) and validate(protein) and validate(carbs)):
            flash("calories, protein, fat, and carbs must be a number", category = "error")
        else: # add to db
            new_item = Item(carbs=carbs.strip(), cals=cals.strip(), fats=fats.strip(), protein=protein.strip(), name=item.strip(), user_id=current_user.id)
            db.session.add(new_item)
            db.session.commit()
            flash("item added!", category="success")
    totals = calculate_totals(current_user)
    return render_template("home.html", user = current_user, user_dict = totals)

"""
not yet implemented with this app
"""
@views.route("/get-started")
def get_started():
    return render_template("get_started.html", user=current_user)

"""
tranfers python dictionary with user data to frontend for javascript to handle
"""
@views.route("/getpythondata")
def get_python_data():
    return json.dumps(totals)

"""
receives post request from delete JS function with the id of the item to delete. 
finds the item and deletes it from database
"""
@views.route("/delete-item", methods = ["POST"])
def delete_item():
    item = json.loads(request.data) # item is a python dict
    id = item["itemId"] # accessing id attribute
    item = Item.query.get(id) # looking for item
    if item: 
        if item.user_id == current_user.id: # if item exists and belongs to current user, delete
            db.session.delete(item)
            db.session.commit()
    
    return jsonify({})

@views.route("/profile", methods = ["POST", "GET"])
def profile():
    return render_template("profile.html", user=current_user)
