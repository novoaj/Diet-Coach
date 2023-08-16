from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user

from . import views

auth = Blueprint("auth", __name__)

@auth.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
       
        if user:
            # check pswrd
            if check_password_hash(user.password, password): # hashes second param and checks against first
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category = "error")
        else:
            flash("Email does not exist", category = "error")
    
    return render_template("login.html", user=current_user)

@auth.route("/sign-up", methods = ["GET", "POST"])
def signUp():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first-name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        sex = request.form.get("sex-select")
        height_ft = request.form.get("height-ft")
        height_in = request.form.get("height-in")
        age = request.form.get("age")
        weight = request.form.get("weight")
        goal = request.form.get("goals")
        activity_factor = float(request.form.get("activity-factor"))

        """
        method to calculate Basal Metabolic Rate (BMR) of user
        """
        def calculate_BMR(weight, height, age):
            # convert height and weight
            weight_kg = int(weight)/2.2
            height_cm = int(height)*2.54
            return 10 * weight_kg + 6.25 * height_cm - 5 * int(age) + 5
        """
        takes in user information to calculate recommended daily intake values for Calories (TDEE), fats, proteins, carbs in grams
        """
        def calculate_recommended(sex,height,weight, age, goal, activity_factor):
            # calc BMR
            bmr = calculate_BMR(weight,height,age)
            tdee = bmr * activity_factor # Total Daily Energy Expenditure (Calories)
            
            rec_dict = {"cals":2000, "fats": 50, "protein": 60, "carbs": 250} # default vals
            # maintain
            if goal == "maintain":
                goal_cals = tdee
                rec_dict["cals"] = goal_cals
                rec_dict["fats"] = (goal_cals * .3)/9 # these are all in grams
                rec_dict["carbs"] = (goal_cals * .5)/4
                rec_dict["protein"] = (goal_cals * .2)/4
            # lose
            elif goal == "lose":
                goal_cals = tdee-400
                rec_dict["cals"] = goal_cals
                rec_dict["fats"] = (goal_cals*.25)/9
                rec_dict["carbs"] = (goal_cals*.4)/4
                rec_dict["protein"] = (goal_cals*.35)/4
            # gain
            else:
                if sex == "Male":
                    goal_cals = tdee + 300
                else:
                    goal_cals = tdee + 200
                rec_dict["cals"] = goal_cals
                rec_dict["fats"] = (goal_cals*.2)/9
                rec_dict["carbs"] = (goal_cals*.45)/4
                rec_dict["protein"] = (goal_cals*.35)/4
            return rec_dict
        """
        local helper method verifying input is numeric
        """
        def verify_num(txt):
            if not txt:
                return False
            return txt.strip().isdigit()
        """
        local helper method calculating height
        """
        def calc_height_inches(ft,inches):
            return (int(ft)*12) + int(inches)

        user = User.query.filter_by(email=email).first()
        recommended_dict = {}
        if user:
            flash("Email already exists", category="error")
        elif password1 != password2:
            flash("passwords must match, try again", category = "error")
        elif (not verify_num(weight)):
            flash("Weight must be an Integer", category = "error")
        elif (not verify_num(age)):
            flash("Age must be an integer", category = "error")
        elif len(first_name) < 2:
            flash("First Name should be longer than 1 character", category = "error")
        else:
            height = calc_height_inches(height_ft, height_in)
            recommended_dict = calculate_recommended(sex,height,weight, age, goal, activity_factor)
            new_user = User(email = email, password = generate_password_hash(password1, method = "sha256"), recommended_intake = recommended_dict["cals"], recommended_fats = recommended_dict["fats"], recommended_protein = recommended_dict["protein"], recommended_carbs = recommended_dict["carbs"], sex=sex, weight=weight, height=height, goal=goal, activity_factor=activity_factor,age=age, first_name=first_name)
            # add user to db
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("account created", category="success")
            return redirect(url_for("views.home"))
    return render_template("sign_up.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))