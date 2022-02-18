
from flask import Flask, render_template, request
import requests
import folium
from geopy.geocoders import Nominatim
import json

from config_token import token

def get_followers(id):
    """
    Returns followers by id
    """
    global token
    return requests.get(f"https://api.twitter.com/2/users/{id}/following", headers={'Authorization': f'Bearer {token}'}).json()['data']

def get_id(username):
    """
    Gets id by name
    """
    global token
    return requests.get(f"https://api.twitter.com/2/users/by/username/{username}", headers={'Authorization': f'Bearer {token}'}).json()['data']['id']


def get_location(id):
    """
    Returns location by id
    """
    global token
    return requests.get(f"https://api.twitter.com/2/users/{id}?user.fields=location", headers={'Authorization': f'Bearer {token}'}).json()['data']['location']


def create_map(name):
    """
    Creates map and returns True of success
    """
    id = '?'
    try:
        id = get_id(name)
    except:
        return None
    followers = get_followers(id)

    geolocator = Nominatim(user_agent="Map creator")

    map = folium.Map()
    fg = folium.FeatureGroup(name = 'Friends')
    for x in followers:
        follower_id = x['id']
        try:
            follower_loc = get_location(follower_id)
            if follower_loc is None:
                continue
            follower_coord = geolocator.geocode(follower_loc)
            fg.add_child(folium.Marker(location=(follower_coord.latitude, follower_coord.longitude), popup=x['name'], icon=folium.Icon()))
        except:
            continue
        
    map.add_child(fg)
    #map.save('templates/map.html')
    return map



app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    map =  create_map(name)
    if map != None:
        return  map._repr_html_()
    else:
        return render_template("error.html", message="Invalid name")

app.run()