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
            "dish": "Pizza Margherita",
            "amount": 350
        }

        Odpowiedź (sukces):
        {
            "dish": "Pizza Margherita",
            "amount": 350,
            "micronutrients": {
                "Magnez": 120.5,
                "Żelazo": 3.2,
                ...
            },
            "status": "success"
        }

        Odpowiedź (błąd):
        {
            "status": "error",
            "message": "Opis błędu"
        }
        """
        try:
            data = request.get_json()

            # Walidacja obecności parametru 'dish'
            if not data or 'dish' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Brak parametru 'dish' w requestcie"
                }), 400

            dish_name = data['dish']
            
            # Parametr amount jest opcjonalny, domyślnie 100g
            amount = data.get('amount', 100)

            # Walidacja amount
            try:
                amount = int(amount)
                if amount <= 0:
                    return jsonify({
                        "status": "error",
                        "message": "Parametr 'amount' musi być liczbą większą od 0"
                    }), 400
                if amount > 10000:
                    return jsonify({
                        "status": "error",
                        "message": "Parametr 'amount' nie może przekraczać 10000g"
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    "status": "error",
                    "message": "Parametr 'amount' musi być liczbą całkowitą"
                }), 400

            print(f"\n{'='*60}")
            print(f"📡 [API] Odebrano zapytanie:")
            print(f"   • Potrawa: {dish_name}")
            print(f"   • Ilość: {amount}g")

            # Analiza potrawy z uwzględnieniem gramatury
            micronutrients = analyze_dish(client, dish_name, amount)

            if micronutrients is None:
                print(f"❌ [API] Błąd analizy potrawy")
                print(f"{'='*60}\n")
                return jsonify({
                    "status": "error",
                    "message": "Nie udało się przeanalizować potrawy. Sprawdź połączenie z OpenAI API lub spróbuj ponownie."
                }), 500

            print(f"✅ [API] Odpowiedź wysłana pomyślnie")
            print(f"{'='*60}\n")

            return jsonify({
                "status": "success",
                "dish": dish_name,
                "amount": amount,
                "micronutrients": micronutrients
            }), 200

        except Exception as e:
            print(f"❌ [API] Nieoczekiwany błąd: {e}")
            print(f"{'='*60}\n")
            return jsonify({
                "status": "error",
                "message": f"Błąd serwera: {str(e)}"
            }), 500

    return api_bp