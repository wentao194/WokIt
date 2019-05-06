from flask import redirect, render_template, request, session
import requests
import json
import time

class GooglePlaces(object):
    def __init__(self, apiKey):
        super(GooglePlaces, self).__init__()
        self.apiKey = apiKey

    def search_places_by_coordinate(self, location, radius, addy, name):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places = []
        params = {
            'location': location,
            'radius': radius,
            'query': addy,
            'name' : name,
            'key': self.apiKey
        }
        res = requests.get(endpoint_url, params = params)
        results =  json.loads(res.content)
        places.extend(results['results'])
        time.sleep(2)
        while "next_page_token" in results:
            params['pagetoken'] = results['next_page_token'],
            res = requests.get(endpoint_url, params = params)
            results = json.loads(res.content)
            places.extend(results['results'])
            time.sleep(2)
        return places

def get_place_details(place_id, fields):
    endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'placeid': place_id,
        'fields': ",".join(fields),
        'key': "AIzaSyBlcH-tkt7e6JqIPGKFxo6WM84KbANBEhc"
    }
    res = requests.get(endpoint_url, params = params)
    place_details =  json.loads(res.content)
    return place_details

def google_review(lat,lng,address,name):
    api = GooglePlaces("AIzaSyBlcH-tkt7e6JqIPGKFxo6WM84KbANBEhc")
    location = lat+","+lng
    places = api.search_places_by_coordinate( location, "5", address, name)
    return places
