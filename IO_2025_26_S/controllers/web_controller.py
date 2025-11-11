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

            if not dish_name:
                error_msg = "Podaj nazwę potrawy!"
            elif not amount.isdigit():
                error_msg = "Ilość musi być liczbą!"
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

            print(f"\n{'=' * 50}")
            print(f"Odebrano dane: {dish_name}, {amount} g, {date}")
            print(f"{'=' * 50}\n")

            # Analiza potrawy
            data = analyze_dish(client, dish_name)

            chart_error = False
            chart_path = None

            if data is None:
                print("Nie udało się pobrać danych.")
                chart_error = True
            else:
                chart_path = create_chart(dish_name, data)

                # ZAPIS DO DZIENNIKA
                save_success = add_meal(
                    dish_name=dish_name,
                    amount=int(amount),
                    date=date,
                    nutrition_data=data
                )

                if save_success:
                    print(" Posiłek zapisany w dzienniku!")
                else:
                    print(" Nie udało się zapisać posiłku w dzienniku")

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
