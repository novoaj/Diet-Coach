from . import db # our SQLAlchemy db object

from flask_login import UserMixin
from sqlalchemy.sql import func

"""
User model for storing user information
"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # given by user during sign-up
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150)) 
    first_name = db.Column(db.String(150))   
    sex = db.Column(db.String(10))
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer) 
    age = db.Column(db.Integer)
    goal = db.Column(db.String(10))
    activity_factor = db.Column(db.Float)

    # calculate during sign-up, 
    recommended_intake = db.Column(db.Integer)
    recommended_protein = db.Column(db.Integer)
    recommended_fats = db.Column(db.Integer)
    recommended_carbs = db.Column(db.Integer)

    items = db.relationship("Item", backref = "user")
"""
Items that users can add to their day of eating. reset items at midnight
"""
class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    cals = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    carbs = db.Column(db.Integer)

    date = db.Column(db.DateTime(timezone=True), default = func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

# Note: https://www.digitalocean.com/community/tutorials/how-to-use-one-to-many-database-relationships-with-flask-sqlalchemy
# The db.create_all() function does not recreate or update a table if it already exists. For example, if you modify your model 
# by adding a new column, and run the db.create_all() function, the change you make to the model will not be applied to the table
#  if the table already exists in the database. The solution is to delete all existing database tables with the db.drop_all() 
#  function and then recreate them with the db.create_all() function like so: