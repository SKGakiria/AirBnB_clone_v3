#!/usr/bin/python3
"""The Place Amenity module"""
from flask import abort, jsonify, request

from api.v1.views import app_views
from models import storage
from models.amenity import Amenity
from models.place import Place
from flasgger.utils import swag_from


@app_views.route('/places/<place_id>/amenities', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/place_amenity/get_id.yml', methods=['GET'])
def get_amenities_by_place(place_id):
    """Retrieves list of all Amenity objects of a Place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    a_amenities = [obj.to_dict() for obj in place.amenities]
    return jsonify(a_amenities)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE'], strict_slashes=False)
@swag_from('documentation/place_amenity/delete.yml', methods=['DELETE'])
def delete_amenity_from_place(place_id, amenity_id):
    """Deletes Amenity object to a Place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    if amenity not in place.amenities:
        abort(404)

    place.amenities.remove(amenity)
    storage.save()
    return (jsonify({}), 200)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['POST'], strict_slashes=False)
@swag_from('documentation/place_amenity/post.yml', methods=['POST'])
def link_amenity_to_place(place_id, amenity_id):
    """Links Amenity object to a Place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404)

    if amenity in place.amenities:
        return (jsonify(amenity.to_dict()), 200)

    place.amenities.append(amenity)

    storage.save()
    return (jsonify(amenity.to_dict()), 201)
