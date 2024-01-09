from flask import Flask, render_template, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, QueryApi
from influxdb_client.client.write_api import SYNCHRONOUS

import requests
import json
import os

from forms import UserAddForm, UserLogInForm 
from models import db, connect_db, User
from dotenv import load_dotenv 


CURR_USER_KEY = "curr_user"
scheduler = BackgroundScheduler()
app = Flask(__name__)

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

# I need to add my database here whether it is postgresql or a timebased series. Something there
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///btc_database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SECRET_KEY"] = os.getenv('secret')

app.app_context().push()

connect_db(app)
db.create_all()

debug = DebugToolbarExtension(app)

##########################INFLUXDB & API DETAILS################################################
# Crypto Compare API Key
key = os.getenv('api_key')
# InfluxDB Database Details
bucket = "btcCharter"
org = "btcCharter"
token = os.getenv('influx_admin_key')
url = "http://127.0.0.1:8086"
client = InfluxDBClient(url=url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)


# setting the api_key to a new variable

###############################################################################
# Setting a datetime class to handle datetime objects

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

###############################################################################

# User Signup/Login/Logout

@app.before_request
def add_user_to_g():
    
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

@app.before_request
def scheduler_start():

    if not scheduler.running:
        scheduler.start()

@app.teardown_appcontext
def scheduler_end(exception=None):
    if scheduler.running:
        scheduler.shutdown()

def do_login(user):
    """Log the user in"""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout the user"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]    

@app.route('/', methods=["GET"])
def frontpage():

    return render_template('display/frontpage.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user sign up. 
    
    This will create a new user and add them to the database. Redirect to home page afterwards
    
    If form not valid, present form. 
    
    If there is already a user with that username: flash message and re-present form
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()
        
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)
        
        do_login(user)

        return redirect('/')
    
    else:
        return render_template('users/signup.html', form=form)
    

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle User log in

    If user is not logged in they will be shown the log in for to put in their user and password

    if they are logged in already they will be re-directed to the home page

    """

    form = UserLogInForm()

    if form.validate_on_submit():
        try:
            user = User.login(
                username=form.username.data,
                password=form.password.data,
            )
            db.session.commit()
        
        except IntegrityError:
            flash("Incorrect Username or Password", 'danger')
            return render_template('users/login.html', form=form)
        
        do_login(user)

        return redirect('/')
    
    else:
        return render_template('users/login.html', form=form)
    

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


###############################################################################################################

@app.route('/home')
def home_page():
    """Show the home page of the """

    # Connect to InfluxDB using the correct URL and token
    client = InfluxDBClient(url='http://localhost:8086', token=token, org='btcCharter')

    # Use the query API to perform queries
    query_api = QueryApi(client)

    query = 'from(bucket:"btcCharter") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "bitcoin_price") |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'

    result = query_api.query(org='btcCharter', query=query)

    # Iterate over tables in the result (there might be multiple tables)

    labels=[]

    try:
        labels = [str(label) for label in labels]
        # labels_str = json.dumps(labels, cls=DateTimeEncoder)
        values = []

        for table in result:
            # Iterate over rows in each table
            for row in table.records:
                labels.append(row['_time'].strftime("%m/%d/%Y, %H:%M:%S"))
                values.append(row['price'])

        print('Labels:', labels)
        print('Labels:', type(labels))
        print('Values:', values)

        return render_template('display/home.html', labels=labels, values=json.dumps(values))
    
    except Exception as e:
        # Handle exceptions gracefully and print the error for debugging
        print(f"Error: {e}")
        return render_template('404.html')

def get_amount():
    print("Fetching Bitcoin price...")
    url = 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD'
    response = requests.get(url, headers={'authorization': f'Apikey {key}'})
    data = response.json()
    amount = data.get('USD', None)
    print(amount) 
    return round(amount, 2) if amount is not None else None

@app.route('/store_bitcoin_price', methods=['POST'])
def store_bitcoin_price():
    """Get the price from the JSON request and store in InfluxDB"""

    bitcoin_price = get_amount()
    current_time = datetime.now(timezone.utc)

    data = [
        {
            'measurement': "bitcoin_price",
            "tags": {
                "currency": "BTC"
            },
            "time": current_time.isoformat(),
            "fields": {
                "price": bitcoin_price
            }
        }
    ]

    org = "btcCharter"
    bucket = "btcCharter"
    # api_token = os.getenv('influx_admin_key')

    try:
        # Write the data point to InfluxDB
        client.write_api(write_options=SYNCHRONOUS).write(bucket=bucket, org=org, record=data)
        print("Bitcoin price stored in InfluxDB")
        return "Bitcoin price stored in InfluxDB"
    except Exception as e:
        print(f"Error storing Bitcoin price in InfluxDB: {e}")
        return "Error storing Bitcoin price in InfluxDB"
    
    

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page.
    If an error occurs, the user will be prompted to return to the home page
    """

    return render_template('404.html'), 404

scheduler.add_job(store_bitcoin_price, trigger='interval', minutes=1, id='job')
scheduler.start()

if (__name__ == "__main__"):
    app.run(debug=True, use_reloader = False)
