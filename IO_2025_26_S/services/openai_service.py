import json

def analyze_dish(client, name):
    """
    Analiza potrawy za pomocą OpenAI API.
    Zwraca dane o mikroskładnikach w formacie dict.
    """
    if not client:
        print("Brak połączenia z OpenAI API")
        return None

    try:
        prompt = f"""Podaj wartości mikroskładników dla potrawy "{name}" w formacie JSON.
Zwróć tylko 4-6 najważniejszych mikroskładników (np. magnez, żelazo, witamina D, wapń, cynk, potas).
Wartości podaj w mg lub µg.

Format odpowiedzi (tylko JSON, bez dodatkowego tekstu):
{{
    "Magnez": 120,
    "Żelazo": 3,
    "Witamina D": 5,
    "Wapń": 250,
    "Cynk": 2
}}"""

        print(f"Wysyłanie zapytania do ChatGPT dla potrawy: {name}")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem od żywienia. Zwracasz tylko poprawny JSON bez dodatkowych komentarzy."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=500
        )

        content = response.choices[0].message.content.strip()
        print("Otrzymano odpowiedź od ChatGPT")

        # Usuwanie markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        content = content.strip().replace("\n", "").replace("\r", "")

        try:
            data = json.loads(content)
            print(f"Dane sparsowane poprawnie: {data}")
        except json.JSONDecodeError:
            print("Nie udało się sparsować JSON-a.")
            print(content)
            data = None

        return data

    except Exception as e:
        print(f"Błąd podczas analizy potrawy: {e}")
        return None
