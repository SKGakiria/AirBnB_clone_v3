#!/usr/bin/python3
"""The Places Module"""
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
    if request.get_json() is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)

    data = request.get_json()

    if data and len(data):
        states = data.get('states', None)
        cities = data.get('cities', None)
        amenities = data.get('amenities', None)

    if not data or not len(data) or (
            not states and
            not cities and
            not amenities):
        places = storage.all(Place).values()
        all_places = []
        for place in places:
            all_places.append(place.to_dict())
        return jsonify(all_places)

    all_places = []
    if states:
        states_obj = [storage.get(State, s_id) for s_id in states]
        for state in states_obj:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            all_places.append(place)

    if cities:
        city_obj = [storage.get(City, c_id) for c_id in cities]
        for city in city_obj:
            if city:
                for place in city.places:
                    if place not in all_places:
                        all_places.append(place)

    if amenities:
        if not all_places:
            all_places = storage.all(Place).values()
        amenities_obj = [storage.get(Amenity, a_id) for a_id in amenities]
        all_places = [place for place in all_places
                      if all([am in place.amenities for am in amenities_obj])]

    places = []
    for plc in all_places:
        place_dict = plc.to_dict()
        place_dict.pop('amenities', None)
        places.append(place_dict)

    return jsonify(places)
