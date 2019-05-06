import requests
from flask import Flask, flash, jsonify, redirect, render_template, request, session
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
def get_business_id(name, address1, city, state, country, lat, lng):
    try:
        business_path = BUSINESS_PATH
        url = API_HOST + business_path + 'matches'
        print(url)
        headers = {'Authorization': "Bearer "+API_KEY}
        params = {'name': name, 'address1':address1, 'city':city,'state':state,'country':country, 'latitude':lat, 'longitude':lng} 
        response = requests.get(url, headers=headers, params=params)
    except:
        return 'Null'

    try:
        response = response.json()
        return response['businesses'][0]['id']
    except:
        return 'Null'

# Extract Yelp Restaurants by PHONE
def get_business_id_phone(phone):
    try:
        business_path = BUSINESS_PATH
        url = API_HOST + business_path + 'search/phone'
        print(url)
        headers = {'Authorization': "Bearer "+API_KEY}
        params = {'phone': phone} 
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
        map_info = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address="+address+"&key=AIzaSyBlcH-tkt7e6JqIPGKFxo6WM84KbANBEhc")
        map_info = map_info.json()

        # Extracting Google Maps Search Info which will be used to get Yelp's Restaurant Review
        lat = map_info["results"][0]["geometry"]["location"]["lat"]
        lng = map_info["results"][0]["geometry"]["location"]["lng"]
        addresslst = address.split(',')
        name = addresslst[0]
        address1 = map_info["results"][0]["address_components"][0]["short_name"] + map_info["results"][0]["address_components"][1]["short_name"]
        city = map_info["results"][0]["address_components"][-5]["short_name"]
        state = map_info["results"][0]["address_components"][-3]["short_name"]
        country = map_info["results"][0]["address_components"][-2]["short_name"]


        # Google Review Extract
        places = google_review(str(lat), str(lng), addresslst[0], name)
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


        # Yelp API ID and Review
        address1 = addy.split(',')
        restaurant_id = get_business_id(name, address1[0], city, state, country, lat, lng)
        # Yelp Phone search
        phone_num = '+'
        for i in phone_number:
            if i >= '0' and i <= '9':
                phone_num += i
        restaurant_id2 = get_business_id_phone(phone_num)
        # Yelp Review Extract
        try:
            yelp_reviews = get_business_review(restaurant_id)
            yelp_reviews = yelp_reviews['reviews']
        except KeyError:
            try:
                yelp_reviews = get_business_review(restaurant_id2)
                yelp_reviews = yelp_reviews['reviews']
            except: 
                yelp_reviews = ''

        # Return a page with Google, Yelp, and OpenTable Review
        return render_template("main.html",lat=lat,lng=lng, restaurant_id=restaurant_id, yelp_reviews=yelp_reviews, places=places, website=website, name=name, addy=addy, phone_number=phone_number, reviews=reviews)
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
#         return render_template("500.html", error = str(e))


# @app.errorhandler(404)
# def page_not_found(d):
#     return render_template("404.html")

if __name__ == "__main__":
    app.run(debug=True)