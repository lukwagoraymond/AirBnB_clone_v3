#!/usr/bin/python3
"""
Flask route that returns json status response
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage
from os import environ
from models.place import Place
STORAGE_TYPE = environ.get('HBNB_TYPE_STORAGE')


@app_views.route('/cities/<city_id>/places', methods=['GET', 'POST'],
                 strict_slashes=False)
def places_per_city(city_id=None):
    """Endpoint to handle http method for requested places by city"""
    city_obj = storage.get('City', city_id)
    if not city_obj:
        abort(404, 'Not found')

    if request.method == 'GET':
        all_places = storage.all('Place')
        place_List = []
        for val in all_places.values():
            if val.city_id == city_id:
                place_List.append(val.to_dict())
        return jsonify(place_List)

    if request.method == 'POST':
        req_json = request.get_json()
        user_id = req_json.get('user_id')
        user_obj = storage.get('User', user_id)

        if not req_json:
            abort(400, 'Not a JSON')
        if not user_id:
            abort(400, 'Missing user_id')

        if not user_obj:
            abort(404, 'Not found')
        if "name" not in req_json.keys():
            abort(400, 'Missing name')

        new_Place = Place(**req_json)
        new_Place.city_id = city_id
        storage.new(new_Place)
        new_Place.save()
        storage.close()
        return jsonify(new_Place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def places_with_id(place_id=None):
    """Endpoint to handle http methods for given place"""
    place_obj = storage.get('Place', place_id)
    if not place_obj:
        abort(404, 'Not found')

    if request.method == 'GET':
        return jsonify(place_obj.to_dict())

    if request.method == 'DELETE':
        place_obj.delete()
        storage.save()
        storage.close()
        return jsonify({}), 200

    if request.method == 'PUT':
        ignore_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
        req_json = request.get_json()
        if not req_json:
            abort(400, 'Not a JSON')
        for key, val in req_json.items():
            if key not in ignore_keys:
                setattr(place_obj, key, val)
        place_obj.save()
        storage.close()
        return jsonify(place_obj.to_dict()), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """End route to handle http method for request to search places"""
    req_json = request.get_json()
    if req_json is not None:
        states = req_json.get('states', [])
        cities = req_json.get('cities', [])
        amenities = req_json.get('amenities', [])

        amenity_objs = []
        for amenity_id in amenities:
            amenity = storage.get('Amenity', amenity_id)
            if amenity:
                amenity_objs.append(amenity)

        if states == cities == []:
            all_places = storage.all('Place').values()
        else:
            all_places = []
            for state_id in states:
                state = storage.get('State', state_id)
                state_cities = state.cities
                for city in state_cities:
                    if city.id not in cities:
                        cities.append(city.id)
            for city_id in cities:
                city = storage.get('City', city_id)
                for place in city.places:
                    all_places.append(place)
        confirmed_places = []
        for place in all_places:
            place_amenities = place.amenities
            confirmed_places.append(place.to_dict())
            for amenity in amenity_objs:
                if amenity not in place_amenities:
                    confirmed_places.pop()
                    break
        return jsonify(confirmed_places)
    else:
        abort(400, 'Not a JSON')
