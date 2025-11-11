import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os

def create_chart(dish_name, data):
    try:
        plt.figure(figsize=(10, 6))
        plt.bar(data.keys(), data.values(), color='lightgreen', edgecolor='black')
        plt.title(f"Zawartość mikroskładników: {dish_name}", fontsize=16, fontweight='bold')
        plt.xlabel("Mikroskładnik", fontsize=12)
        plt.ylabel("Ilość (mg lub µg)", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha='right')

        chart_path = os.path.join('static', 'chart.png')
        plt.tight_layout()
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        return chart_path

    except Exception as e:
        print(f"Błąd przy tworzeniu wykresu: {e}")
        return None