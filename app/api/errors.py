from flask import jsonify
from app.api import api
from werkzeug.exceptions import HTTPException

@api.app_errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.status_code = e.code
    return response

@api.app_errorhandler(500)
def internal_error(error):
    return jsonify({
        "code": 500,
        "name": "Internal Server Error",
        "description": "An unexpected error occurred on the server."
    }), 500
