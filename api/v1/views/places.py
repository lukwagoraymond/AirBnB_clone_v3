#!/usr/bin/python3
"""
Flask route that returns json status response
"""
from api.v1.views import app_views
from flask import abort, jsonify, request, make_response
from models import storage
from models.place import Place


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
    """ search places by id """
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
        list_places = []
        for place in places:
            list_places.append(place.to_dict())
        return jsonify(list_places)

    list_places = []
    if states:
        states_obj = [storage.get('State', s_id) for s_id in states]
        for state in states_obj:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            list_places.append(place)

    if cities:
        city_obj = [storage.get('City', c_id) for c_id in cities]
        for city in city_obj:
            if city:
                for place in city.places:
                    if place not in list_places:
                        list_places.append(place)

    if amenities:
        if not list_places:
            list_places = storage.all(Place).values()
        amenities_obj = [storage.get('Amenity', a_id) for a_id in amenities]
        list_places = [place for place in list_places
                       if all([am in place.amenities
                               for am in amenities_obj])]

    places = []
    for p in list_places:
        d = p.to_dict()
        d.pop('amenities', None)
        places.append(d)

    return jsonify(places)
