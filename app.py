import os
from dotenv import load_dotenv

from flask import Flask, render_template,flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mqttClient import mqtt_water

from models import Water
load_dotenv()

# Configure the PostgreSQL connection
db_user = 'mpappas'
db_password = os.environ['db_password']
# db_password = 'postgres'
db_host = 'localhost'
db_port = '5432'
db_name = 'van_data'

db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Congifure db connection
db = create_engine(db_url)

Session = sessionmaker(db)
session = Session()

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)


@app.post('/reset/water')
def reset_water():
    """reset water value in db and send mqtt message."""
    new_water = Water(consumption = 0, percent_remain = 100)
    db.session.add(new_water)
    db.session.commit()

    mqtt_water(["water", "reset"], "reset")

    return