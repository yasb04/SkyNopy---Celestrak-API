from flask import Flask, jsonify, request
from domain.services.tle_coordinator_service import TLECoordinatorService


def create_routes(app: Flask, coordinator: TLECoordinatorService):   
    @app.route("/satellite_tle/<norad_id>", methods=["GET"])
    def get_satellite_tle(norad_id: str):
        try:
            tle_entry = coordinator.get_latest_tle(norad_id)
            
            if not tle_entry:
                return jsonify({
                    "error": f"TLE not found for NORAD ID: {norad_id}"
                }), 404
            
            tle_dict = tle_entry.to_dict()
            response = {
                "line1": tle_dict["line1"],
                "line2": tle_dict["line2"],
                "epoch": tle_dict["epoch"],
                "source": tle_dict["source"]
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({
                "error": f"Internal server error: {str(e)}"
            }), 500
    
    @app.route("/satellite_tle/<norad_id>/history", methods=["GET"])
    def get_satellite_tle_history(norad_id: str):
        try:
            history = coordinator.get_tle_history(norad_id)
            
            response = {
                "norad_id": norad_id,
                "count": len(history),
                "tles": [tle_entry.to_dict() for tle_entry in history]
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({
                "error": f"Internal server error: {str(e)}"
            }), 500
    
    @app.route("/satellite_tle/<norad_id>", methods=["POST"])
    def post_satellite_tle(norad_id: str):
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    "error": "Request body must contain JSON with 'line1' and 'line2'"
                }), 400
            
            line1 = data.get("line1")
            line2 = data.get("line2")
            
            if not line1 or not line2:
                return jsonify({
                    "error": "Both 'line1' and 'line2' are required"
                }), 400
            
            tle_entry = coordinator.add_custom_tle(norad_id, line1, line2)
            
            if tle_entry is None:
                return jsonify({
                    "error": "Invalid TLE format or NORAD ID mismatch"
                }), 400
            
            tle_dict = tle_entry.to_dict()
            response = {
                "message": "TLE successfully stored",
                "line1": tle_dict["line1"],
                "line2": tle_dict["line2"],
                "epoch": tle_dict["epoch"],
                "source": tle_dict["source"]
            }
            
            return jsonify(response), 201
            
        except Exception as e:
            return jsonify({
                "error": f"Internal server error: {str(e)}"
            }), 500
    
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "Bonjour SkyNopy"}), 200
