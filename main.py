"""
GitHub link: https://github.com/alorthius/lab_3_task_3_html_map
"""
import requests
import json
import folium

from flask import Flask, redirect, render_template, request
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable


def find_users_friends_info(bearer_token: str, user_name: str) -> dict:
    """
    Find users's friends by its user_name using bearer_token.
    Return a dictionary with info about friends profiles.
    """
    base_url = 'https://api.twitter.com/'
    search_url = '{}1.1/friends/list.json'.format(base_url)

    search_headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
    search_params = {'screen_name': user_name,
                     'count': 15}

    response = requests.get(
        search_url, headers=search_headers, params=search_params)

    json_response = response.json()
    return json_response


def find_friends_locations(friends_dict: dict) -> dict:
    """
    Find in the dictionary the location, name and username of the friend.
    Return a dictionary, where the location is key, and names are values.
    """
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
    """
    For each friend find coordinates of the location in their profiles.
    """
    coordinates_dict = {}

    for user_location, user_info in locations_dict.items():
        location = geolocator.geocode(user_location)
        try:
            latitude, longitude = location.latitude, location.longitude
        except (AttributeError, GeocoderUnavailable):
            continue
        coordinates_dict[(latitude, longitude)] = user_info
    return coordinates_dict


def create_html_map(coordinates_dict: dict):
    """
    Dicplay all friends locations on the map.
    Return it as an html.
    """
    map = folium.Map(zoom_start=2)
    fg = folium.FeatureGroup(name="My map")

    friends_location = MarkerCluster(name='friends locations').add_to(map)

    for tup in coordinates_dict.keys():
        folium.Marker(location=[tup[0], tup[1]],
            popup=f'Name: «{coordinates_dict[tup][0]}»;\nUsername: «{coordinates_dict[tup][1]}»',
            icon=folium.Icon(color='darkpurple', icon='user')).add_to(friends_location)
    map.add_child(fg)
    return map._repr_html_()


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

    friends_dict = find_users_friends_info(token, username)
    if friends_dict == {'errors': [{'code': 34, 'message': 'Sorry, that page does not exist.'}]}:
        return render_template("username_fail.html")
    elif friends_dict == {'users': [], 'next_cursor': 0, 'next_cursor_str': '0',
                          'previous_cursor': 0, 'previous_cursor_str': '0', 'total_count': None}:
        return render_template("no_locations.html")

    locations_dict = find_friends_locations(friends_dict)
    coordinates_dict = find_coordinates(locations_dict)
    return create_html_map(coordinates_dict)


if __name__ == '__main__':
    geolocator = Nominatim(user_agent="friends_map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    app.debug = True
    app.run()
