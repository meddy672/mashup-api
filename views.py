from __builtin__ import unicode
from findArestaurant import findARestaurant
from models import Base, Restaurant, User
from flask import Flask, jsonify, request, abort, url_for
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import sys
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

# foursquare_client_id = ''

# foursquare_client_secret = ''

# google_api_key = ''

engine = create_engine('sqlite:///restaruants.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)



@app.route('/api/user', methods=['POST', 'GET'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if session.query(User).filter_by(username=username).first() is not None:
        abort(400)
    user = User(username=username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'username': username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)}

@app.route('/restaurants', methods=['GET', 'POST'])
def all_restaurants_handler():
    if request.method == 'GET':
        restaurant = session.query(Restaurant).all()
        # return json object
        return jsonify(restaurant=[i.serialize for i in restaurant])
    elif request.method == 'POST':
        # Make new restaurant and store it in database
        location = request.args.get('location', '')
        mealtype = request.args.get('mealtype', '')
        restaurant_info = findARestaurant(mealtype, location)
        if restaurant_info != "No Restaurants Found":
            # Create new restaurant Object and add it to the database
            restaurant = Restaurant(restaurant_name=unicode(restaurant_info['name']),
                                    restaurant_address=unicode(restaurant_info['address']),
                                    restaurant_image=restaurant_info['image'])
            session.add(restaurant)
            session.commit()
            return jsonify(restaurant=restaurant.serialize)
        else:
            return jsonify({"error": "No Restaurants Found for %s in %s" % (mealtype, location)})


@app.route('/restaurants/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def restaurant_handler(id):
    restaurant = session.query(Restaurant).filter_by(id=id).one()
    if request.method == 'GET':
        # RETURN A SPECIFIC RESTAURANT
        return jsonify(restaurant=restaurant.serialize)
    elif request.method == 'PUT':
        # Update a specific restaurant
        address = request.args.get('address')
        image = request.args.get('image')
        name = request.args.get('name')
        if address:
            restaurant.restaurant_address = address
        if image:
            restaurant.restaurant_image = image
        if name:
            restaurant.restaurant_name = name
        session.commit()
        return jsonify(restaurant=restaurant.serialize)

    elif request.method == 'DELETE':
        session.delete(restaurant)
        session.commit()
        return "Restaurant Deleted"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

