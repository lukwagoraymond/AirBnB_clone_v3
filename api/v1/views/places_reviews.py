#!/usr/bin/python3
"""
Flask route that returns json status response
"""
from api.v1.views import app_views
from flask import abort, jsonify, request
from models import storage
from models.review import Review


@app_views.route('/places/<place_id>/reviews', methods=['GET', 'POST'],
                 strict_slashes=False)
def reviews_per_place(place_id=None):
    """Endpoint to handle http method for requested reviews by place"""
    place_obj = storage.get('Place', place_id)

    if request.method == 'GET':
        if place_obj is None:
            abort(404, 'Not found')
        all_reviews = storage.all('Review')
        place_reviews = [obj.to_dict() for obj in all_reviews.values()
                         if obj.place_id == place_id]
        return jsonify(place_reviews)

    if request.method == 'POST':
        if place_obj is None:
            abort(404, 'Not found')
        req_json = request.get_json()
        if req_json is None:
            abort(400, 'Not a JSON')
        user_id = req_json.get("user_id")
        if user_id is None:
            abort(400, 'Missing user_id')
        user_obj = storage.get('User', user_id)
        if user_obj is None:
            abort(404, 'Not found')
        if req_json.get('text') is None:
            abort(400, 'Missing text')
        new_Review = Review(**req_json)
        new_Review.place_id = place_id
        storage.new(new_Review)
        new_Review.save()
        storage.close()
        return jsonify(new_Review.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['GET', 'DELETE', 'PUT'],
                 strict_slashes=False)
def reviews_with_id(review_id=None):
    """Endpoint to handle http methods for given review by ID"""
    review_obj = storage.get('Review', review_id)

    if request.method == 'GET':
        if review_obj is None:
            abort(404, 'Not found')
        return jsonify(review_obj.to_json())

    if request.method == 'DELETE':
        if review_obj is None:
            abort(404, 'Not found')
        review_obj.delete()
        storage.save()
        storage.close()
        return jsonify({}), 200

    if request.method == 'PUT':
        if review_obj is None:
            abort(404, 'Not found')
        ignore_keys = ['id', 'created_at', 'updated_at', 'city_id', 'user_id']
        req_json = request.get_json()
        if req_json is None:
            abort(400, 'Not a JSON')
        for key, val in req_json.items():
            if key not in ignore_keys:
                setattr(review_obj, key, val)
        review_obj.save()
        storage.close()
        return jsonify(review_obj.to_dict()), 200
