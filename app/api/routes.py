from flask import jsonify, current_app
from app.api import api
from app.extensions import db
from sqlalchemy import text

@api.route('/health', methods=['GET'])
def health_check():
    """
    Check the health of the API and database connection.
    """
    health_status = {
        "status": "up",
        "api": "ok",
        "database": "unknown"
    }
    
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        health_status["database"] = "ok"
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {str(e)}")
        health_status["database"] = "down"
        health_status["status"] = "degraded"
        
    return jsonify(health_status), 200 if health_status["status"] == "up" else 503

@api.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"}), 200

@api.route('/teste', methods=['GET'])
def Teste():
    return("<p>Teste deu certo<p/>")

