import requests
import json

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
        'screen_name': '@BarackObama',
        'count': 2
    }

    response = requests.get(search_url, headers=search_headers, params=search_params)
    print(response)

    json_response = response.json()
    pprint(json_response)


# if __name__ == '__main__':
#     app.debug = True
#     app.run()