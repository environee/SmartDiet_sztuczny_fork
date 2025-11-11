import json
import time

def analyze_dish(client, name, amount=100):
    """
    Analiza potrawy za pomocą OpenAI API z uwzględnieniem gramatury.
    
    Args:
        client: Klient OpenAI API
        name: Nazwa potrawy
        amount: Gramatura potrawy (domyślnie 100g dla standardowej porcji)
    
    Returns:
        dict: Dane o mikroskładnikach przeliczone na podaną gramaturę
        None: W przypadku błędu
    """
    if not client:
        print("❌ Brak połączenia z OpenAI API")
        return None

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # Prompt z uwzględnieniem gramatury
            prompt = f"""Podaj wartości mikroskładników dla potrawy "{name}" o gramaturze {amount}g w formacie JSON.

WAŻNE WYMAGANIA:
1. Przelicz wszystkie wartości proporcjonalnie do podanej gramatury {amount}g
2. Zwróć tylko 4-6 najważniejszych mikroskładników (np. Magnez, Żelazo, Witamina D, Wapń, Cynk, Potas)
3. Wartości podaj w mg lub µg (odpowiednio do standardów żywieniowych)
4. Weź pod uwagę rzeczywistą gramaturę potrawy - {amount}g

Format odpowiedzi (tylko JSON, bez dodatkowego tekstu):
{{
    "Magnez": 120,
    "Żelazo": 3,
    "Witamina D": 5,
    "Wapń": 250,
    "Cynk": 2,
    "Potas": 300
}}

Przykład: Jeśli standardowa porcja 100g zawiera 50mg magnezu, to dla {amount}g powinno być {amount/100 * 50}mg magnezu."""

            print(f"\n{'='*60}")
            print(f"🔍 [ANALIZA] Potrawa: {name}")
            print(f"⚖️  [GRAMATURA] Ilość: {amount}g")
            print(f"🔄 [PRÓBA] {attempt + 1}/{max_retries}")
            print(f"{'='*60}")

            # Wywołanie API
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Jesteś ekspertem od żywienia. Zwracasz tylko poprawny JSON bez dodatkowych komentarzy. Wszystkie wartości mikroskładników MUSZĄ być proporcjonalnie przeliczone na podaną gramaturę potrawy."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=10000
                 
            )

            content = response.choices[0].message.content.strip()
            print(f"✅ [API] Otrzymano odpowiedź od ChatGPT")
            print(f"📄 [RAW] Surowa odpowiedź:\n{content[:200]}...")

            # Czyszczenie odpowiedzi z markdown
            cleaned_content = _clean_json_response(content)
            
            # Walidacja i parsowanie JSON
            data = _validate_and_parse_json(cleaned_content, name, amount)
            
            if data:
                print(f"✅ [SUKCES] Dane sparsowane poprawnie")
                print(f"📊 [WYNIK] Mikroskładniki dla {amount}g:")
                for key, value in data.items():
                    print(f"   • {key}: {value}")
                print(f"{'='*60}\n")
                return data
            else:
                print(f"⚠️  [OSTRZEŻENIE] Próba {attempt + 1} nieudana - ponawiam...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

        except Exception as e:
            print(f"❌ [BŁĄD] Próba {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"⏳ Czekam {retry_delay}s przed kolejną próbą...")
                time.sleep(retry_delay)
            else:
                print(f"❌ [KRYTYCZNY] Wszystkie próby wyczerpane")
                print(f"{'='*60}\n")
                return None

    print(f"❌ [BŁĄD] Nie udało się przeanalizować potrawy po {max_retries} próbach")
    print(f"{'='*60}\n")
    return None


def _clean_json_response(content):
    """
    Czyści odpowiedź z markdown i innych niepotrzebnych elementów.
    
    Args:
        content: Surowa odpowiedź z API
    
    Returns:
        str: Wyczyszczona odpowiedź zawierająca tylko JSON
    """
    # Usuwanie markdown ```json ... ```
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    # Usuwanie białych znaków
    content = content.strip().replace("\n", "").replace("\r", "")
    
    return content


def _validate_and_parse_json(content, dish_name, amount):
    """
    Waliduje i parsuje JSON z odpowiedzi LLM.
    
    Args:
        content: Wyczyszczona odpowiedź do sparsowania
        dish_name: Nazwa potrawy (do logowania)
        amount: Gramatura potrawy (do walidacji)
    
    Returns:
        dict: Sparsowane i zwalidowane dane
        None: W przypadku błędu
    """
    try:
        data = json.loads(content)
        
        # Walidacja struktury
        if not isinstance(data, dict):
            print(f"❌ [WALIDACJA] Odpowiedź nie jest słownikiem")
            return None
        
        if len(data) == 0:
            print(f"❌ [WALIDACJA] Pusty słownik mikroskładników")
            return None
        
        # Walidacja wartości
        validated_data = {}
        for key, value in data.items():
            if not isinstance(key, str):
                print(f"⚠️  [WALIDACJA] Pomijam nieprawidłowy klucz: {key}")
                continue
            
            # Konwersja wartości na float/int
            try:
                numeric_value = float(value)
                if numeric_value < 0:
                    print(f"⚠️  [WALIDACJA] Wartość ujemna dla {key}: {numeric_value} - pomijam")
                    continue
                
                # Zaokrąglenie do 1 miejsca po przecinku
                validated_data[key] = round(numeric_value, 1)
                
            except (ValueError, TypeError):
                print(f"⚠️  [WALIDACJA] Nieprawidłowa wartość dla {key}: {value} - pomijam")
                continue
        
        if len(validated_data) == 0:
            print(f"❌ [WALIDACJA] Brak prawidłowych mikroskładników po walidacji")
            return None
        
        print(f"✅ [WALIDACJA] Zwalidowano {len(validated_data)} mikroskładników")
        return validated_data
        
    except json.JSONDecodeError as e:
        print(f"❌ [JSON] Błąd parsowania JSON: {e}")
        print(f"📄 [JSON] Problematyczna treść: {content[:200]}")
        return None
    except Exception as e:
        print(f"❌ [WALIDACJA] Nieoczekiwany błąd: {e}")
        return None


def _calculate_proportional_values(base_data, target_amount, base_amount=100):
    """
    Przelicza wartości mikroskładników proporcjonalnie do gramatury.
    
    Args:
        base_data: Słownik z wartościami bazowymi (zwykle dla 100g)
        target_amount: Docelowa gramatura
        base_amount: Bazowa gramatura (domyślnie 100g)
    
    Returns:
        dict: Przeliczone wartości
    """
    if not base_data or target_amount <= 0:
        return base_data
    
    ratio = target_amount / base_amount
    proportional_data = {}
    
    for key, value in base_data.items():
        try:
            proportional_value = float(value) * ratio
            proportional_data[key] = round(proportional_value, 1)
        except (ValueError, TypeError):
            proportional_data[key] = value
    
    return proportional_data