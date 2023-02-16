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
        ignore_keys = ['id', 'created_at', 'updated_at', 'city_id', 'user_id']
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
    """
        places route to handle http method for request to search places
    """
    all_places = [p for p in storage.all('Place').values()]
    req_json = request.get_json()
    if req_json is None:
        abort(400, 'Not a JSON')
    states = req_json.get('states')
    if states and len(states) > 0:
        all_cities = storage.all('City')
        state_cities = set([city.id for city in all_cities.values()
                            if city.state_id in states])
    else:
        state_cities = set()
    cities = req_json.get('cities')
    if cities and len(cities) > 0:
        cities = set([
            c_id for c_id in cities if storage.get('City', c_id)])
        state_cities = state_cities.union(cities)
    amenities = req_json.get('amenities')
    if len(state_cities) > 0:
        all_places = [p for p in all_places if p.city_id in state_cities]
    elif amenities is None or len(amenities) == 0:
        result = [place.to_json() for place in all_places]
        return jsonify(result)
    places_amenities = []
    if amenities and len(amenities) > 0:
        amenities = set([
            a_id for a_id in amenities if storage.get('Amenity', a_id)])
        for p in all_places:
            p_amenities = None
            if STORAGE_TYPE == 'db' and p.amenities:
                p_amenities = [a.id for a in p.amenities]
            elif len(p.amenities) > 0:
                p_amenities = p.amenities
            if p_amenities and all([a in p_amenities for a in amenities]):
                places_amenities.append(p)
    else:
        places_amenities = all_places
    result = [place.to_dict() for place in places_amenities]
    return jsonify(result)
