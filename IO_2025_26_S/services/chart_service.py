import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os

def create_chart(dish_name, data, amount=100):
    """
    Tworzy wykres słupkowy mikroskładników z informacją o gramaturze.
    
    Args:
        dish_name: Nazwa potrawy
        data: Słownik z danymi mikroskładników
        amount: Gramatura potrawy w gramach
    
    Returns:
        str: Ścieżka do zapisanego wykresu
        None: W przypadku błędu
    """
    try:
        # Konfiguracja wykresu
        plt.figure(figsize=(12, 7))
        
        # Tworzenie wykresu słupkowego
        bars = plt.bar(
            data.keys(), 
            data.values(), 
            color='lightgreen', 
            edgecolor='black',
            linewidth=1.5
        )
        
        # Dodanie wartości nad słupkami
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2., 
                height,
                f'{height:.1f}',
                ha='center', 
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )
        
        # Tytuł z informacją o gramaturze
        plt.title(
            f"Zawartość mikroskładników: {dish_name} ({amount}g)", 
            fontsize=16, 
            fontweight='bold',
            pad=20
        )
        
        plt.xlabel("Mikroskładnik", fontsize=12, fontweight='bold')
        plt.ylabel("Ilość (mg lub µg)", fontsize=12, fontweight='bold')
        
        # Siatka dla lepszej czytelności
        plt.grid(axis='y', linestyle='--', alpha=0.7, linewidth=0.8)
        
        # Rotacja etykiet na osi X
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)
        
        # Dodanie informacji o gramaturze na dole wykresu
        plt.figtext(
            0.99, 0.01, 
            f'Gramatura: {amount}g', 
            ha='right', 
            fontsize=9, 
            style='italic',
            color='gray'
        )
        
        # Zapisanie wykresu
        chart_path = os.path.join('static', 'chart.png')
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ [WYKRES] Wygenerowano wykres: {chart_path}")
        return chart_path

    except Exception as e:
        print(f"❌ [WYKRES] Błąd przy tworzeniu wykresu: {e}")
        plt.close()  # Upewniamy się, że figura jest zamknięta
        return None