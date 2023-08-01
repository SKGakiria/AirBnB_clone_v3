#!/usr/bin/python3
"""The Places Module"""
from os import getenv

from flask import abort, jsonify, make_response, request

from api.v1.views import app_views
from models import storage
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.state import State
from models.user import User


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places_by_city(city_id):
    """Retrieves list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    a_places_list = [obj.to_dict() for obj in storage.all(Place).values()
                     if city_id == obj.city_id]
    return jsonify(a_places_list)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    storage.delete(place)
    storage.save()
    return (jsonify({}), 200)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a Place object"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)

    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    if 'user_id' not in data:
        return make_response(jsonify({"error": "Missing user_id"}), 400)

    user_id = data['user_id']
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    if 'name' not in data:
        return make_response(jsonify({"error": "Missing name"}), 400)

    data['city_id'] = city_id
    n_place = Place(**data)
    n_place.save()
    return (jsonify(n_place.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    ignored_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, val in data.items():
        if key not in ignored_keys:
            setattr(place, key, val)

    storage.save()
    return (jsonify(place.to_dict()), 200)


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """
    Retrieves all Place objects depending on the JSON in the request body.
    """
    all_places = [obj for obj in storage.all(Place).values()]
    data = request.get_json()

    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])

    state_cities = set()
    if states:
        all_cities = storage.all(City)
        state_cities.update(c.id for c in all_cities.values() if
                            c.state_id in states)

    if cities:
        city_objs = {c.id: c for c in storage.all(City).values() if
                     c.id in cities}
        state_cities.update(city_objs.keys())

    if state_cities:
        all_places = [p for p in all_places if p.city_id in state_cities]
    elif not amenities:
        return jsonify([place.to_dict() for place in all_places])

    if amenities:
        amenity_objs = {a.id: a for a in storage.all(Amenity).values() if
                        a.id in amenities}
        places_amenities = []
        for place in all_places:
            place_amenities = [a.id for a in place.amenities]
            if all(amenity_id in place_amenities for amenity_id in amenities):
                places_amenities.append(place)
    else:
        places_amenities = all_places

    # Return the final result
    result = [place.to_dict() for place in places_amenities]
    return jsonify(result)
