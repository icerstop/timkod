import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import MaxNLocator
import pandas as pd
import os

# Ustawienie stylu seaborn dla ładniejszych wykresów
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['font.size'] = 12

def visualize_results(letter_freq, avg_lengths, cond_probs, text_samples):
    """
    Funkcja tworząca wizualizacje na podstawie wyników obliczeń.
    
    Parametry:
    - letter_freq: słownik {znak: częstość} z częstościami znaków
    - avg_lengths: słownik {nazwa_modelu: średnia_długość} ze średnimi długościami słów
    - cond_probs: słownik {znak: {następny_znak: prawdopodobieństwo}} z prawdopodobieństwami warunkowymi
    - text_samples: słownik {nazwa_modelu: przykładowy_tekst} z próbkami wygenerowanego tekstu
    """
    # Utwórz katalog na wykresy (jeśli nie istnieje)
    if not os.path.exists('wykresy'):
        os.makedirs('wykresy')
    
    # 1. Wykres częstości liter
    plt.figure(figsize=(14, 8))
    plt.suptitle('Wizualizacje dla modelowania tekstu', fontsize=16)
    
    # Sortowanie i wybór 10 najczęstszych znaków
    sorted_freq = sorted(letter_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    chars, freqs = zip(*sorted_freq)
    chars = ['spacja' if c == ' ' else c for c in chars]  # Zamiana spacji na widoczny tekst
    
    plt.subplot(2, 2, 1)
    plt.bar(chars, freqs, color='skyblue')
    plt.title('Częstość występowania znaków (top 10)')
    plt.xlabel('Znak')
    plt.ylabel('Częstość')
    plt.xticks(rotation=45)
    
    # 2. Wykres średniej długości słów
    plt.subplot(2, 2, 2)
    models = list(avg_lengths.keys())
    lengths = list(avg_lengths.values())
    
    # Skrócenie nazw modeli dla lepszej czytelności
    short_models = [m.replace('Przybliżenie ', '').replace('-go rzędu', '') for m in models]
    
    plt.plot(short_models, lengths, 'o-', color='green')
    plt.title('Średnia długość słów dla różnych przybliżeń')
    plt.xlabel('Model')
    plt.ylabel('Średnia długość słowa')
    plt.xticks(rotation=45)
    plt.ylim(bottom=0)  # Zacznij od zera dla lepszej perspektywy
    
    # 3. Wykresy warunkowych prawdopodobieństw
    plt.subplot(2, 2, 3)
    
    # Wybieramy 2 najczęstsze znaki z letter_freq
    most_common = [char for char, _ in sorted_freq[:2]]
    most_common_display = ['spacja' if c == ' ' else c for c in most_common]
    print(f"Dwa najczęstsze znaki: {most_common_display}")
    
    # Pobieranie i sortowanie prawdopodobieństw dla pierwszego najczęstszego znaku
    if most_common[0] in cond_probs:
        first_char_probs = cond_probs[most_common[0]]
        first_sorted = sorted(first_char_probs.items(), key=lambda x: x[1], reverse=True)[:10]
        first_chars, first_probs_vals = zip(*first_sorted)
        first_chars_display = ['spacja' if c == ' ' else c for c in first_chars]
        
        plt.bar(first_chars_display, first_probs_vals, color='purple')
        plt.title(f"Warunkowe prawdopodobieństwa P(X|'{most_common_display[0]}')")
        plt.xlabel('Znak')
        plt.ylabel('Prawdopodobieństwo')
        plt.xticks(rotation=45)
    
    # Pobieranie i sortowanie prawdopodobieństw dla drugiego najczęstszego znaku
    plt.subplot(2, 2, 4)
    if len(most_common) > 1 and most_common[1] in cond_probs:
        second_char_probs = cond_probs[most_common[1]]
        second_sorted = sorted(second_char_probs.items(), key=lambda x: x[1], reverse=True)[:10]
        second_chars, second_probs_vals = zip(*second_sorted)
        second_chars_display = ['spacja' if c == ' ' else c for c in second_chars]
        
        plt.bar(second_chars_display, second_probs_vals, color='orange')
        plt.title(f"Warunkowe prawdopodobieństwa P(X|'{most_common_display[1]}')")
        plt.xlabel('Znak')
        plt.ylabel('Prawdopodobieństwo')
        plt.xticks(rotation=45)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('wykresy/wizualizacja_1.png', dpi=300, bbox_inches='tight')
    print("Zapisano wykres 1: Podstawowe statystyki")
    
    # 4. Wykres porównujący średnie długości słów jako słupki
    plt.figure(figsize=(12, 6))
    
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'plum', 'khaki']
    
    plt.bar(short_models, lengths, color=colors[:len(models)])
    plt.title('Porównanie średniej długości słów dla różnych modeli')
    plt.xlabel('Model')
    plt.ylabel('Średnia długość słowa')
    plt.ylim(0, max(lengths) + 1)
    plt.xticks(rotation=45)
    
    # Dodanie wartości na wierzchołkach słupków
    for i, v in enumerate(lengths):
        plt.text(i, v + 0.1, f'{v:.2f}', ha='center')
    
    plt.tight_layout()
    plt.savefig('wykresy/wizualizacja_2.png', dpi=300, bbox_inches='tight')
    print("Zapisano wykres 2: Porównanie średnich długości słów")
    
    # 5. Wykres porównujący prawdopodobieństwa warunkowe dla obu najczęstszych znaków
    if len(most_common) >= 2 and most_common[0] in cond_probs and most_common[1] in cond_probs:
        plt.figure(figsize=(14, 8))
        
        # Utwórz DataFrame dla łatwiejszej manipulacji danymi
        first_df = pd.DataFrame(list(first_sorted), columns=['znak', 'prawdopodobieństwo'])
        first_df['kontekst'] = f'Po "{most_common_display[0]}"'
        
        second_df = pd.DataFrame(list(second_sorted), columns=['znak', 'prawdopodobieństwo'])
        second_df['kontekst'] = f'Po "{most_common_display[1]}"'
        
        # Połącz dane
        combined_df = pd.concat([first_df, second_df])
        
        # Zamień spacje na widoczny tekst
        combined_df['znak'] = combined_df['znak'].apply(lambda x: 'spacja' if x == ' ' else x)
        
        # Rysuj wykres
        sns.barplot(data=combined_df, x='znak', y='prawdopodobieństwo', hue='kontekst')
        plt.title('Porównanie warunkowych prawdopodobieństw')
        plt.xlabel('Znak')
        plt.ylabel('Prawdopodobieństwo')
        plt.legend(title='Kontekst')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('wykresy/wizualizacja_3.png', dpi=300, bbox_inches='tight')
        print("Zapisano wykres 3: Porównanie prawdopodobieństw warunkowych")
    
    # 6. Próbki wygenerowanego tekstu - wizualnie
    plt.figure(figsize=(14, 16))
    plt.subplots_adjust(top=0.95)

    plt.suptitle('Próbki wygenerowanego tekstu', fontsize=18, y=0.98)
    plt.axis('off')

    models = list(text_samples.keys())
    short_models = [m.replace('Przybliżenie ', '').replace('-go rzędu', '') for m in models]
    n_models = len(models)

    line_length = 75
    padding = 0.02
    total_padding = padding * (n_models - 1)
    available_height = 0.9
    box_height = (available_height - total_padding) / n_models

    y_start = 0.95
    
    for i, (model, text) in enumerate(text_samples.items()):
        # Pozycja każdego boxu
        box_top = y_start - (i * (box_height + padding)) - box_height
        
        # Tworzymy box dla modelu
        rect = plt.Rectangle((0.05, box_top), 0.9, box_height, 
                            fill=True, color='#f0f0f0', alpha=0.9,
                            transform=plt.gcf().transFigure, zorder=1,
                            ec='darkgray', lw=1)
        plt.gcf().patches.extend([rect])
        
        # Nazwa modelu (nagłówek)
        short_name = model.replace('Przybliżenie ', '').replace('-go rzędu', '')
        plt.figtext(0.08, box_top + box_height - 0.02, short_name, 
                    fontsize=12, fontweight='bold', color='black')
        
        # Formatowanie tekstu wewnątrz boxu
        formatted_text = []
        words = text.split()
        current_line = ""
        
        # Tworzenie linii o określonej długości
        for word in words:
            if len(current_line) + len(word) + 1 <= line_length:
                current_line += " " + word if current_line else word
            else:
                formatted_text.append(current_line)
                current_line = word
        
        if current_line:
            formatted_text.append(current_line)
        
        # Maksymalna liczba linii do wyświetlenia
        max_lines = 6
        if len(formatted_text) > max_lines:
            formatted_text = formatted_text[:max_lines-1] + ["..."]
        
        # Wyświetlenie tekstu
        for j, line in enumerate(formatted_text):
            line_spacing = (box_height - 0.05) / max_lines
            y_pos = box_top + box_height - 0.05 - (j * line_spacing)
            plt.figtext(0.08, y_pos, line, fontsize=9, family='monospace')

    plt.savefig('wykresy/wizualizacja_4.png', dpi=300, bbox_inches='tight')
    print("Zapisano wykres 4: Próbki wygenerowanego tekstu")
    
    # 7. Wykres trendów dla rzędów Markova
    markova_models = [k for k in avg_lengths.keys() if 'Markova' in k]
    
    if markova_models:
        plt.figure(figsize=(10, 6))
        
        # Ekstrahujemy rzędy z nazw modeli
        markova_orders = []
        markova_lengths = []
        
        for model in markova_models:
            # Ekstrahujemy rząd z nazwy modelu (np. "Przybliżenie Markova 5-go rzędu" -> 5)
            try:
                order_text = model.split('Markova ')[1].split('-')[0]
                order = int(order_text)
                markova_orders.append(order)
                markova_lengths.append(avg_lengths[model])
            except (IndexError, ValueError):
                continue
        
        # Sortujemy według rzędu
        sorted_data = sorted(zip(markova_orders, markova_lengths))
        markova_orders, markova_lengths = zip(*sorted_data) if sorted_data else ([], [])
        
        if markova_orders:
            plt.plot(markova_orders, markova_lengths, 'o-', color='blue', linewidth=2)
            plt.scatter(markova_orders, markova_lengths, color='red', s=100)
            
            plt.title('Wpływ rzędu modelu Markova na średnią długość słów')
            plt.xlabel('Rząd modelu Markova')
            plt.ylabel('Średnia długość słowa')
            plt.grid(True)
            
            # Dodaj etykiety danych
            for i, txt in enumerate(markova_lengths):
                plt.annotate(f'{txt:.2f}', (markova_orders[i], markova_lengths[i]), 
                            xytext=(5, 5), textcoords='offset points')
            
            # Ustaw całkowite wartości na osi X
            plt.xticks(markova_orders)
            
            plt.tight_layout()
            plt.savefig('wykresy/wizualizacja_5.png', dpi=300, bbox_inches='tight')
            print("Zapisano wykres 5: Wpływ rzędu modelu Markova")
    
    print("\nWizualizacje zostały zapisane w katalogu 'wykresy'.")
    print("Możesz wykorzystać je w swoim sprawozdaniu.")

# Do testowania samodzielnie:
if __name__ == "__main__":
    # Przykładowe dane do wizualizacji (gdyby ktoś chciał testować ten moduł samodzielnie)
    from string import ascii_lowercase, digits
    
    alphabet = ascii_lowercase + digits + ' '
    
    # Przykładowe częstości liter
    letter_freq = {}
    for char in alphabet:
        if char == ' ':
            letter_freq[char] = np.random.random() * 100 + 150
        elif char in 'etaoinshrdlu':
            letter_freq[char] = np.random.random() * 60 + 40
        elif char in '0123456789':
            letter_freq[char] = np.random.random() * 10 + 5
        else:
            letter_freq[char] = np.random.random() * 30 + 10
    
    # Przykładowe średnie długości słów
    avg_lengths = {
        'Przybliżenie zerowego rzędu': 4.2,
        'Przybliżenie pierwszego rzędu': 4.8,
        'Przybliżenie Markova 1-go rzędu': 5.1,
        'Przybliżenie Markova 3-go rzędu': 5.6,
        'Przybliżenie Markova 5-go rzędu': 5.9,
        'Przybliżenie Markova 10-go rzędu': 6.2
    }
    
    # Przykładowe warunkowe prawdopodobieństwa
    cond_probs = {}
    for char in [' ', 'e']:  # Przykładowe najczęstsze znaki
        cond_probs[char] = {}
        for next_char in alphabet:
            cond_probs[char][next_char] = np.random.random()
        
        # Normalizacja
        total = sum(cond_probs[char].values())
        for next_char in cond_probs[char]:
            cond_probs[char][next_char] /= total
    
    # Przykładowe fragmenty tekstu
    text_samples = {
        'Przybliżenie zerowego rzędu': 
            'x9gfuh j34t8 gn5d wj7u tld5 xpq2 u9y2 5sfd h5w2 c9i4 wnr4 jd93 x76d e43f ju75 lrn5...',
        'Przybliżenie pierwszego rzędu': 
            'e o ats r l ndshicup mwgbvkyfxjzq0123456789 e o ats r l ndshicup mwgbvkyfxjzq0123...',
        'Przybliżenie Markova 1-go rzędu': 
            'the andis of to somen the wome for hat inter whis for thave youre but wither my som...',
        'Przybliżenie Markova 3-go rzędu': 
            'the information probability is defined as the most common words in the text and can...',
        'Przybliżenie Markova 5-go rzędu': 
            'probability is the measure of the likelihood that an event will occur based on the ...'
    }
    
    # Wykonaj wizualizacje
    visualize_results(letter_freq, avg_lengths, cond_probs, text_samples)