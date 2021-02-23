import requests
import json
import folium

from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from pprint import pprint
from flask import Flask, redirect, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    token = request.form.get("token")
    if not username or not token:
        return render_template("failure.html")
    return render_template("success.html")


def find_users_friends_info(bearer_token: str, user_name: str):
    base_url = 'https://api.twitter.com/'

    search_url = '{}1.1/friends/list.json'.format(base_url)

    search_headers = {
        'Authorization': 'Bearer {}'.format(bearer_token)
    }

    search_params = {
        'screen_name': user_name,
        'count': 15
    }

    response = requests.get(
        search_url, headers=search_headers, params=search_params)

    json_response = response.json()
    return json_response


def find_friends_locations(friends_dict: dict):
    locations_dict = {}
    for user_info in friends_dict['users']:
        user_name = []
        for key, value in user_info.items():
            if key == 'name' or key == 'screen_name':
                user_name.append(value)
            elif key == 'location' and value != '':
                locations_dict[value] = user_name
                continue
    return locations_dict


def find_coordinates(locations_dict: dict) -> dict:
    new_dict = {}
    # geolocator = Nominatim(user_agent="friends_html_ma")


    for user_location, user_info in locations_dict.items():
        location = geolocator.geocode(user_location)
        try:
            latitude, longitude = location.latitude, location.longitude
        except (AttributeError, GeocoderUnavailable):
            continue
        new_dict[(latitude, longitude)] = user_info
    return new_dict


def create_html_map(coordinates_dict: dict):
    map = folium.Map(zoom_start=2)
    fg = folium.FeatureGroup(name="My map")

    friends_location = MarkerCluster(name='friends locations').add_to(map)

    for tup in coordinates_dict.keys():
        folium.Marker(location=[tup[0], tup[1]],
                      popup=f'Name: {coordinates_dict[tup][0]}\nUsername: {coordinates_dict[tup][1]}',
                      icon=folium.Icon(color='darkpurple', icon='user')).add_to(friends_location)
    map.add_child(fg)
    map.save('Your_map_here.html')


# if __name__ == '__main__':


#     app.debug = True
#     app.run()

