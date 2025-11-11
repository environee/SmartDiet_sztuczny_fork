from flask import Blueprint, render_template, request, url_for, redirect, flash
from services.openai_service import analyze_dish
from services.chart_service import create_chart
from services.meal_service import add_meal, get_all_meals, get_meals_by_date, delete_meal, get_meals_statistics
from datetime import datetime


def create_web_blueprint(client):
    web_bp = Blueprint("web_bp", __name__)

    @web_bp.route("/", methods=["GET", "POST"])
    def home():
        submitted = False
        dish_name = None
        error_msg = None
        api_connected = client is not None

        today = datetime.today().strftime("%Y-%m-%d")

        if request.method == "POST":
            dish_name = request.form.get("dish_name", "").strip()
            amount = request.form.get("amount", "").strip()
            date = request.form.get("date", today).strip()

            if not api_connected:
                error_msg = "Brak połączenia z OpenAI API."
                return render_template(
                    "prototyp.html",
                    submitted=False,
                    error_msg=error_msg,
                    api_connected=False,
                    today=today
                )

            # Walidacja danych wejściowych
            if not dish_name:
                error_msg = "Podaj nazwę potrawy!"
            elif not amount.isdigit():
                error_msg = "Ilość musi być liczbą!"
            elif int(amount) <= 0:
                error_msg = "Ilość musi być większa od 0!"
            elif int(amount) > 10000:
                error_msg = "Ilość nie może przekraczać 10000g!"
            else:
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    error_msg = "Data musi być w formacie RRRR-MM-DD!"

            if error_msg:
                return render_template(
                    "prototyp.html",
                    submitted=False,
                    api_connected=api_connected,
                    error_msg=error_msg,
                    today=today
                )

            amount_int = int(amount)

            print(f"\n{'=' * 60}")
            print(f"📥 [FORMULARZ] Odebrano dane:")
            print(f"   • Potrawa: {dish_name}")
            print(f"   • Ilość: {amount_int}g")
            print(f"   • Data: {date}")
            print(f"{'=' * 60}")

            # Analiza potrawy z uwzględnieniem gramatury
            data = analyze_dish(client, dish_name, amount_int)

            chart_error = False
            chart_path = None

            if data is None:
                print("❌ [BŁĄD] Nie udało się pobrać danych z API")
                error_msg = "Nie udało się przeanalizować potrawy. Spróbuj ponownie."
                chart_error = True
            else:
                # Generowanie wykresu
                chart_path = create_chart(dish_name, data, amount_int)

                if chart_path is None:
                    print("⚠️  [OSTRZEŻENIE] Nie udało się wygenerować wykresu")
                    chart_error = True

                # ZAPIS DO DZIENNIKA
                save_success = add_meal(
                    dish_name=dish_name,
                    amount=amount_int,
                    date=date,
                    nutrition_data=data
                )

                if save_success:
                    print(f"✅ [DZIENNIK] Posiłek zapisany pomyślnie!")
                else:
                    print(f"❌ [DZIENNIK] Nie udało się zapisać posiłku")

            submitted = True

            return render_template(
                "result.html",
                dish=dish_name,
                amount=amount,
                date=date,
                chart_path=url_for('static', filename='chart.png') if chart_path else None,
                data=data,
                error_msg=error_msg,
                chart_error=chart_error,
                submitted=submitted
            )

        return render_template(
            "prototyp.html",
            submitted=submitted,
            api_connected=api_connected,
            error_msg=error_msg,
            today=today
        )

    # NOWY ENDPOINT: Dziennik wszystkich posiłków
    @web_bp.route("/diary")
    def diary():
        meals = get_all_meals()
        stats = get_meals_statistics()

        return render_template(
            "diary.html",
            meals=meals,
            stats=stats
        )

    # NOWY ENDPOINT: Posiłki z konkretnego dnia
    @web_bp.route("/diary/<date>")
    def diary_by_date(date):
        try:
            # Walidacja daty
            datetime.strptime(date, "%Y-%m-%d")
            meals = get_meals_by_date(date)

            return render_template(
                "diary_by_date.html",
                meals=meals,
                date=date
            )
        except ValueError:
            return "Nieprawidłowy format daty. Użyj YYYY-MM-DD", 400

    # NOWY ENDPOINT: Usuwanie posiłku
    @web_bp.route("/diary/delete/<int:meal_id>", methods=["POST"])
    def delete_meal_route(meal_id):
        success = delete_meal(meal_id)

        if success:
            print(f"✅ Usunięto posiłek ID: {meal_id}")
        else:
            print(f"❌ Nie udało się usunąć posiłku ID: {meal_id}")

        return redirect(url_for("web_bp.diary"))

    return web_bp