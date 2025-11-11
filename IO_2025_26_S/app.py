from flask import Flask
from dotenv import load_dotenv
from openai import OpenAI
import os

from controllers.web_controller import create_web_blueprint
from controllers.api_controller import create_api_blueprint

load_dotenv()

app = Flask(__name__)

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("Połączono z OpenAI API")
except Exception as e:
    print(f"Błąd połączenia z OpenAI API: {e}")
    client = None

# Rejestracja kontrolerów
app.register_blueprint(create_web_blueprint(client))
app.register_blueprint(create_api_blueprint(client), url_prefix="/api")

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Uruchamianie aplikacji SmartDiet")
    print("=" * 50)

    if client:
        print("   Status OpenAI API: POŁĄCZONO")
    else:
        print("   Status OpenAI API: BRAK POŁĄCZENIA")
        print("   Sprawdź plik .env i klucz OPENAI_API_KEY")

    print("\n   Dostępne endpointy:")
    print("   - Interfejs WWW: http://127.0.0.1:5000/")
    print("   - API (Postman): http://127.0.0.1:5000/api/analyze")
    print("=" * 50 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)