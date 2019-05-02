from flask import Flask, flash, jsonify, redirect, render_template, request, session
import requests
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import json
import time
from helper_functions import google_review, get_place_details

app = Flask(__name__)

# Yelp API Information
API_KEY = "E0C7Oeds86YIjOooaAmMNUOo_JNC4yI--n_jzYyPi1JLX8K7KFa6rnf2OrCBBN9m5pYVZAtS5380V_9V5YSRYTvUJ5ODc7wRNBro89a7do_2FEBXQCsV2QT_59nHXHYx"
API_HOST = 'https://api.yelp.com'
BUSINESS_PATH = '/v3/businesses/'

# Extract Yelp Restaurants by ID
def get_business_id(name, address1, city, state, country):
    try:
        business_path = BUSINESS_PATH
        url = API_HOST + business_path + 'matches'
        print(url)
        headers = {'Authorization': "Bearer "+API_KEY}
        params = {'name': name, 'address1':address1, 'city':city,'state':state,'country':country} 
        response = requests.get(url, headers=headers, params=params)
    except:
        return 'Null'

    try:
        response = response.json()
        return response['businesses'][0]['id']
    except:
        return 'Null'

# Extract Yelp Restaurant Review with ID
def get_business_review(business_id):
    try:
        business_path = BUSINESS_PATH + business_id
        url = API_HOST + business_path + '/reviews'
        headers = {'Authorization': "Bearer "+API_KEY}
        response = requests.get(url, headers=headers)
    except:
        return 'Null'

    try:
        return response.json()
    except:
        return 'Null'

@app.route('/', methods=['GET', 'POST'])
@app.route('/home/', methods=['GET', 'POST'])
def homepage():
	# User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
    	if not request.form.get("address"):
            render_template("index.html")

        address = request.form.get("address")

    	# Contact Google API
        try:
        	map_info = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address="+address+"&key=AIzaSyBlcH-tkt7e6JqIPGKFxo6WM84KbANBEhc")
        	map_info = map_info.json()
        except (KeyError, TypeError, ValueError):
            render_template("index.html")

    	# Extracting Google Maps Search Info which will be used to get Yelp's Restaurant Review
        lat = map_info["results"][0]["geometry"]["location"]["lat"]
        lng = map_info["results"][0]["geometry"]["location"]["lng"]
        name = address
        address1 = map_info["results"][0]["address_components"][0]["short_name"] + map_info["results"][0]["address_components"][1]["short_name"]
        city = map_info["results"][0]["address_components"][-5]["short_name"]
        state = map_info["results"][0]["address_components"][-3]["short_name"]
        country = map_info["results"][0]["address_components"][-2]["short_name"]

    	# Yelp API ID and Review
    	restaurant_id = get_business_id(name, address1, city, state, country)
        if restaurant_id == 'Null':
            return render_template("index.html")
    	restaurant_review = get_business_review(restaurant_id)
        if restaurant_review == 'Null':
            return render_template("index.html")

        # Google Review Extract
        places = google_review(str(lat), str(lng))
        fields = ['name', 'formatted_address', 'international_phone_number', 'website', 'rating', 'review']
        for place in places:
            details = get_place_details(place['place_id'], fields)
            try:
                website = details['result']['website']
            except KeyError:
                website = ""
            try:
                name = details['result']['name']
            except KeyError:
                name = ""

            try:
                addy = details['result']['formatted_address']
            except KeyError:
                address = ""

            try:
                phone_number = details['result']['international_phone_number']
            except KeyError:
                phone_number = ""

            try:
                reviews = details['result']['reviews']
            except KeyError:
                reviews = []

        # Return a page with Google, Yelp, and OpenTable Review
    	return render_template("main.html",lat=lat,lng=lng, restaurant_id=restaurant_id, restaurant_review=restaurant_review, places=places, website=website, name=name, addy=addy, phone_number=phone_number, reviews=reviews)
    else:
    	return render_template("index.html")


@app.route('/main/')
def dashboard():
    return render_template("main.html")

# @app.route('/slashboard/')
# def slashboard():
#     try:
#         return render_template("dashboard.html", TOPIC_DICT = shasdafmwow)
#     except Exception as e:
# 	    return render_template("500.html", error = str(e))


# @app.errorhandler(404)
# def page_not_found(d):
#     return render_template("404.html")

if __name__ == "__main__":
    app.run()