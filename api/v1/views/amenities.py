#!/usr/bin/python3
"""
    Flask route that returns json response
"""
from api.v1.views import app_views
from flask import abort, jsonify, request, make_response
from models import storage
from models.amenity import Amenity


@app_views.route('/amenities/', methods=['GET', 'POST'],
                 strict_slashes=False)
def amenities_no_id():
    """Endpoint that handles http requests for no ID given"""
    if request.method == 'GET':
        all_amenities = storage.all('Amenity')
        Amenity_List = []
        for obj in all_amenities.values():
            Amenity_List.append(obj.to_dict())
        return jsonify(Amenity_List)

    if request.method == 'POST':
        req_json = request.get_json()
        if not req_json:
            abort(400, 'Not a JSON')
        elif 'name' not in req_json:
            abort(400, 'Missing name')
        else:
            new_amenity = Amenity(**req_json)
            storage.new(new_amenity)
            new_amenity.save()
            return jsonify(new_amenity.to_dict()), 201


@app_views.route('/amenities/<amenity_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def amenities_with_id(amenity_id=None):
    """amenities route that handles http requests with ID given"""
    amenity_obj = storage.get('Amenity', amenity_id)
    if not amenity_obj:
        abort(404, 'Not found')

    if request.method == 'GET':
        return jsonify(amenity_obj.to_dict())

    if request.method == 'DELETE':
        amenity_obj.delete()
        storage.save()
        storage.close()
        return make_response(jsonify({}), 200)

    if request.method == 'PUT':
        ignore_keys = ['id', 'created_at', 'updated_at']
        req_json = request.get_json()
        if not req_json:
            abort(400, 'Not a JSON')
        for key, val in req_json.items():
            if key not in ignore_keys:
                setattr(amenity_obj, key, val)
        amenity_obj.save()
        storage.close()
        return jsonify(amenity_obj.to_dict()), 200
