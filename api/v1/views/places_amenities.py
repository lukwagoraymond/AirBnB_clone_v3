#!/usr/bin/python3
"""
Flask route that returns json status response
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage
from os import environ
STORAGE_TYPE = environ.get('HBNB_TYPE_STORAGE')


@app_views.route('/places/<place_id>/amenities', methods=['GET'])
def amenities_per_place(place_id=None):
    """Endpoint to handle http method for requested reviews by place"""
    place_obj = storage.get('Place', place_id)
    if place_obj is None:
        abort(404, 'Not found')

    if STORAGE_TYPE == 'db':
        place_amenities = place_obj.amenities
    else:
        place_amenities = place_obj.amenity_ids

    amenity_objs = [objs.to_dict() for objs in place_amenities]
    return jsonify(amenity_objs)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE', 'POST'])
def amenity_to_place(place_id=None, amenity_id=None):
    """Endpoint to handle http methods for given review by ID"""
    place_obj = storage.get('Place', place_id)
    amenity_obj = storage.get('Amenity', amenity_id)
    if place_obj is None:
        abort(404, 'Not found')
    if amenity_obj is None:
        abort(404, 'Not found')

    if request.method == 'DELETE':
        if (amenity_obj not in place_obj.amenities and
                amenity_obj.id not in place_obj.amenities):
            abort(404, 'Not found')
        if STORAGE_TYPE == 'db':
            place_obj.amenities.remove(amenity_obj)
        else:
            place_obj.amenity_ids.remove(amenity_obj.id)
        storage.save()
        storage.close()
        return jsonify({}), 200

    if request.method == 'POST':
        if (amenity_obj in place_obj.amenities or
                amenity_obj.id in place_obj.amenities):
            return jsonify(amenity_obj.to_dict()), 200
        if STORAGE_TYPE == 'db':
            place_obj.amenities.append(amenity_obj)
        else:
            place_obj.amenities = amenity_obj
        return jsonify(amenity_obj.to_dict()), 201
