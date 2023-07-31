#!/usr/bin/python3
"""The Places Module"""
from os import getenv
from flask import jsonify, request, abort, make_response
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from models.amenity import Amenity


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


@app_views.route('/places_search', methods=['POST'], strict_slashes=True)
def places_search():
    """
    Retrieves all Place objects depending on the JSON in the body request.
    """
    all_places = [obj for obj in storage.all(Place).values()]
    data = request.get_json()
    if data is None:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    states = data.get('states')
    if states and len(states) > 0:
        all_cities = storage.all(City)
        state_cities = set([city.id for city in all_cities.values()
                            if city.state_id in states])
    else:
        state_cities = set()
    cities = data.get('cities')
    if cities and len(cities) > 0:
        cities = set([
            c_id for c_id in cities if storage.get(City, c_id)])
        state_cities = state_cities.union(cities)
    amenities = data.get('amenities')
    if len(state_cities) > 0:
        all_places = [p for p in all_places if p.city_id in state_cities]
    elif amenities is None or len(amenities) == 0:
        result = [place.to_json() for place in all_places]
        return jsonify(result)
    places_amenities = []
    if amenities and len(amenities) > 0:
        amenities = set([
            a_id for a_id in amenities if storage.get(Amenity, a_id)])
        for p in all_places:
            p_amenities = None
            if getenv('HBNB_TYPE_STORAGE') == 'db' and p.amenities:
                p_amenities = [a.id for a in p.amenities]
            elif len(p.amenities) > 0:
                p_amenities = p.amenities
            if p_amenities and all([a in p_amenities for a in amenities]):
                places_amenities.append(p)
    else:
        places_amenities = all_places
    result = [place.to_json() for place in places_amenities]
    return jsonify(result)
