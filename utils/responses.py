from flask import jsonify


def success(data=None, message="Success", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status


def failure(message, status):
    return jsonify({"success": False, "message": message, "data": None}), status
