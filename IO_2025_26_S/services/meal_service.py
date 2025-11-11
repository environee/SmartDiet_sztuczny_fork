import json
import os
from datetime import datetime
from typing import List, Dict

from services.data_service import _ensure_data_directory

MEALS_FILE = os.path.join("data", "meals.json")

def _ensure_meals_file():
    """Tworzy plik meals.json, jeśli nie istnieje."""
    _ensure_data_directory()
    if not os.path.exists(MEALS_FILE):
        with open(MEALS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print(f"Utworzono plik: {MEALS_FILE}")


def add_meal(dish_name: str, amount: int, date: str, nutrition_data: Dict) -> bool:
    """
    Dodaje posiłek do dziennika.

    Args:
        dish_name: Nazwa potrawy
        amount: Ilość w gramach
        date: Data w formacie YYYY-MM-DD
        nutrition_data: Słownik z danymi żywieniowymi (mikroskładniki)

    Returns:
        True jeśli zapis się powiódł, False w przeciwnym razie
    """
    try:
        _ensure_meals_file()

        # Wczytaj istniejące dane
        with open(MEALS_FILE, "r", encoding="utf-8") as f:
            meals = json.load(f)

        # Przygotuj nowy wpis
        new_meal = {
            "id": len(meals) + 1,
            "dish_name": dish_name,
            "amount": amount,
            "date": date,
            "nutrition_data": nutrition_data,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Dodaj wpis
        meals.append(new_meal)

        # Zapisz do pliku
        with open(MEALS_FILE, "w", encoding="utf-8") as f:
            json.dump(meals, f, ensure_ascii=False, indent=4)

        print(f"Zapisano posiłek: {dish_name} ({date})")
        return True

    except Exception as e:
        print(f"Błąd zapisu posiłku: {e}")
        return False


def get_meals_by_date(date: str) -> List[Dict]:
    """
    Pobiera wszystkie posiłki z danego dnia.

    Args:
        date: Data w formacie YYYY-MM-DD

    Returns:
        Lista słowników z posiłkami z danego dnia
    """
    try:
        _ensure_meals_file()

        with open(MEALS_FILE, "r", encoding="utf-8") as f:
            meals = json.load(f)

        # Filtruj po dacie
        filtered_meals = [meal for meal in meals if meal.get("date") == date]

        print(f"📅 Znaleziono {len(filtered_meals)} posiłków na dzień {date}")
        return filtered_meals

    except Exception as e:
        print(f"Błąd odczytu posiłków: {e}")
        return []


def get_all_meals() -> List[Dict]:
    """
    Pobiera wszystkie posiłki z dziennika.

    Returns:
        Lista wszystkich posiłków, posortowana od najnowszych
    """
    try:
        _ensure_meals_file()

        with open(MEALS_FILE, "r", encoding="utf-8") as f:
            meals = json.load(f)

        # Sortuj od najnowszych
        meals.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        print(f"Pobrano {len(meals)} posiłków z dziennika")
        return meals

    except Exception as e:
        print(f"Błąd odczytu wszystkich posiłków: {e}")
        return []


def delete_meal(meal_id: int) -> bool:
    """
    Usuwa posiłek z dziennika.

    Args:
        meal_id: ID posiłku do usunięcia

    Returns:
        True jeśli usunięcie się powiodło, False w przeciwnym razie
    """
    try:
        _ensure_meals_file()

        with open(MEALS_FILE, "r", encoding="utf-8") as f:
            meals = json.load(f)

        # Znajdź i usuń posiłek
        meals = [meal for meal in meals if meal.get("id") != meal_id]

        with open(MEALS_FILE, "w", encoding="utf-8") as f:
            json.dump(meals, f, ensure_ascii=False, indent=4)

        print(f"Usunięto posiłek o ID: {meal_id}")
        return True

    except Exception as e:
        print(f"Błąd usuwania posiłku: {e}")
        return False


def get_meals_statistics() -> Dict:
    """
    Zwraca podstawowe statystyki dziennika.

    Returns:
        Słownik ze statystykami (liczba posiłków, unikalne dni, itp.)
    """
    try:
        meals = get_all_meals()

        if not meals:
            return {
                "total_meals": 0,
                "unique_days": 0,
                "date_range": None
            }

        dates = [meal.get("date") for meal in meals if meal.get("date")]
        unique_dates = set(dates)

        return {
            "total_meals": len(meals),
            "unique_days": len(unique_dates),
            "date_range": {
                "first": min(dates) if dates else None,
                "last": max(dates) if dates else None
            }
        }

    except Exception as e:
        print(f"Błąd obliczania statystyk: {e}")
        return {"total_meals": 0, "unique_days": 0, "date_range": None}