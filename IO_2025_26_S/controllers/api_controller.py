from flask import Blueprint, jsonify, request
from services.openai_service import analyze_dish

def create_api_blueprint(client):
    api_bp = Blueprint("api_bp", __name__)

    @api_bp.route("/analyze", methods=["POST"])
    def api_analyze():
        """
            Endpoint API do testowania przez Postmana.

            Przykład użycia:
            POST http://127.0.0.1:5000/api/analyze
            Content-Type: application/json

            Body:
            {
                "dish": "Pizza Margherita"
            }

            Odpowiedź:
            {
                "dish": "Pizza Margherita",
                "micronutrients": {
                    "Magnez": 120,
                    "Żelazo": 3,
                    ...
                },
                "status": "success"
            }
            """
        try:
            data = request.get_json()

            if not data or 'dish' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Brak parametru 'dish' w requestcie"
                }), 400

            dish_name = data['dish']
            print(f"\n{'='*50}")
            print(f"[API] Odebrano zapytanie: {dish_name}")

            micronutrients = analyze_dish(client, dish_name)

            if micronutrients is None:
                return jsonify({
                    "status": "error",
                    "message": "Nie udało się przeanalizować potrawy. Sprawdź połączenie z OpenAI API."
                }), 500

            print(f"[API] Odpowiedź wysłana pomyślnie")
            print(f"{'='*50}\n")

            return jsonify({
                "status": "success",
                "dish": dish_name,
                "micronutrients": micronutrients
            }), 200

        except Exception as e:
            print(f"[API] Błąd: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

    return api_bp
