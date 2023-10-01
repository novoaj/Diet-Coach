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

@views.route("/update-items", methods = ["POST"])
def update_items():
    """
    local method to compare the date from the post request with the database dates (5 hrs ahead). 
    returns true if this item should be deleted (database date is from before js date) 
    """
    def comp_js_db_date(js_date, db_datetime):
        month_days = {1: 31, 2 : 28, 3 : 31, 4 : 30, 5 : 31, 6 : 30, 7 : 31, 8 : 31, 9 : 30, 10 : 31, 11 : 30, 12 : 31}
        js_m, js_d, js_y = js_date.split("/")
        db_datetime = db_datetime.strftime('%m-%d-%Y %H:%M:%S')
        # print(type(db_datetime), db_datetime)
        db_date, db_time = db_datetime.split(" ")
        # print(db_date)
        # print(db_time)
        db_y, db_m, db_d = db_date.split("-")
        h, m, s = db_time.split(":")
        # convert database date to hours
        # if m or d start with 0, remove it?
        db_m = int(db_m) if db_m[0] != "0" else int(db_m[1])
        db_d = int(db_d) if db_d[0] != "0" else int(db_d[1])
        db_y = int(db_y)
        db_hours = int(h)
        db_date_in_hours = db_d * 24 + db_y * 8760 + db_hours - 5 # 5 hours ahead so subtract
        for month in range(1,db_m+1):
            db_date_in_hours += month_days[month] * 24
        
        js_m = int(js_m) if js_m[0] != "0" else int(js_m[1])
        js_d = int(js_d) if js_d[0] != "0" else int(js_d[1])
        js_y = int(js_y)
        js_date_in_hours = js_d * 24 + js_y * 8760
        for month in range(1,js_m+1):
            js_date_in_hours += month_days[month] * 24

        if js_date_in_hours < db_date_in_hours: return False
        return True
        # convert JS date to hours (beginning of day)
        # if JS date < db date, return false
    
    date = json.loads(request.data)
    for item in current_user.items:
        # print(date["date"]) # M/DD/YYYY
        # print(item.date) # YYYY-MM-DD HH:MM:SS # hours is 5 ahead because of flask
        if comp_js_db_date(date["date"],item.date):
            db.session.delete(item) # flask datetime is 5 hours ahead
            db.session.commit()
    # print(Item.query.get(current_user.id))
    return jsonify({})
