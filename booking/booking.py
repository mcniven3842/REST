from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound
from urllib.parse import urlunparse

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'
SHOWTIME = {
    'host': 'localhost',
    'port': 3202,
}

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_json():
    res = make_response(jsonify(bookings), 200)
    return res

@app.route('/bookings/<userid>', methods=['GET'])
def get_booking_for_user(userid):
    for booking in bookings:
        if booking['userid'] == userid:
            return make_response(jsonify(booking), 200)
    return make_response(jsonify({'error': 'bad input parameter'}), 400)

@app.route('/bookings/<userid>', methods=['POST'])
def add_booking_byuser(userid):
    # get body
    body = request.get_json()
    date = body['date']
    movieid = body['movieid']

    # check if movie is available at this date
    response = requests.get(
        urlunparse(('http', f'{SHOWTIME["host"]}:{SHOWTIME["port"]}',
                    f'showmovies/{date}', '', '', ''))).json()
    if movieid not in response['movies']:
        return make_response({'error': 'movie not available at this date'}, 400)

    for booking in bookings:

        # there are already movies for this user
        if booking['userid'] == userid:
            date_objs = booking['dates']
            for date_obj in date_objs:

                # there are already movies in this date
                if date_obj['date'] == date:

                    # movie already in this date for this user
                    if movieid in date_obj['movies']:
                        return make_response(
                            jsonify({
                                'error':
                                    'an existing item already exists with this id'
                            }), 409)

                    # add movie to this date
                    date_obj['movies'].append(movieid)
                    return make_response(jsonify(booking), 200)

            # add new date to user
            date_objs.append({
                'date': date,
                'movies': [movieid],
            })
            return make_response(jsonify(booking), 200)

    # add new user
    bookings.append({
        'userid': userid,
        'dates': [{
            'date': date,
            'movies': [movieid],
        }],
    })
    return make_response(jsonify(bookings[-1]), 200)    

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
