import os
import requests
import random
import re
import time
from collections import defaultdict, Counter
from string import ascii_lowercase, digits, punctuation
from tqdm import tqdm  # Dla pasków postępu (pip install tqdm)

# Alfabet do generowania tekstu
alphabet = ascii_lowercase + digits + ' ' + punctuation

class LargeCorpusMarkovGenerator:
    def __init__(self, corpus_dir="large_corpus", target_size_mb=100):
        """Inicjalizacja generatora z korpusem o określonym rozmiarze."""
        self.corpus_dir = corpus_dir
        self.target_size_mb = target_size_mb
        self.corpus_file = os.path.join(corpus_dir, f"corpus_{target_size_mb}MB.txt")
        self.clean_corpus_file = os.path.join(corpus_dir, f"corpus_{target_size_mb}MB_clean.txt")
        os.makedirs(corpus_dir, exist_ok=True)
        
    def get_book_ids(self, num_books=5000):
        """Generuje listę potencjalnych ID książek z Project Gutenberg."""
        # Większość popularnych książek ma ID poniżej 50000
        potential_ids = list(range(1, 50000))
        random.shuffle(potential_ids)
        return potential_ids[:num_books]
    
    def download_book(self, book_id):
        """Pobiera książkę o danym ID z Project Gutenberg."""
        urls = [
            f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
            f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
            f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Usunięcie nagłówków i stopek Project Gutenberg
                    text = response.text
                    start_marker = "*** START OF"
                    end_marker = "*** END OF"
                    
                    if start_marker in text:
                        text = text.split(start_marker)[1]
                    if end_marker in text:
                        text = text.split(end_marker)[0]
                    
                    return text
            except Exception as e:
                continue
        
        return None
    
    def download_corpus(self):
        """Pobiera korpus o określonym rozmiarze z Project Gutenberg."""
        if os.path.exists(self.corpus_file):
            print(f"Korpus {self.corpus_file} już istnieje, pomijam pobieranie.")
            return self.corpus_file
        
        book_ids = self.get_book_ids()
        total_size = 0
        target_size_bytes = self.target_size_mb * 1024 * 1024
        combined_text = ""
        
        print(f"Pobieranie korpusu o docelowym rozmiarze {self.target_size_mb}MB...")
        
        with tqdm(total=target_size_bytes) as pbar:
            for book_id in book_ids:
                if total_size >= target_size_bytes:
                    break
                    
                book_text = self.download_book(book_id)
                if book_text:
                    book_text = book_text.strip() + "\n\n"
                    book_size = len(book_text.encode('utf-8'))
                    combined_text += book_text
                    total_size += book_size
                    pbar.update(book_size)
                
                # Krótka przerwa, aby nie przeciążać serwera
                time.sleep(0.5)
                    
        print(f"Pobrano teksty o łącznym rozmiarze {total_size / (1024*1024):.2f}MB")
        
        # Zapisz połączony korpus
        with open(self.corpus_file, "w", encoding="utf-8") as f:
            f.write(combined_text)
        
        print(f"Zapisano korpus do pliku {self.corpus_file}")
        return self.corpus_file

    def clean_text(self, text):
        """Oczyszcza tekst, usuwając niepotrzebne znaki i normalizując spacje."""
        # Zamień wszystkie białe znaki na pojedyncze spacje
        text = ' '.join(text.split())
        
        # Konwersja na małe litery
        text = text.lower()
        
        # Pozostawienie tylko dozwolonych znaków
        cleaned_text = ""
        for char in text:
            if char in alphabet:
                cleaned_text += char
        
        return cleaned_text
    
    def prepare_clean_corpus(self):
        """Przygotowuje oczyszczoną wersję korpusu."""
        if os.path.exists(self.clean_corpus_file):
            print(f"Oczyszczony korpus {self.clean_corpus_file} już istnieje, pomijam przetwarzanie.")
            return self.clean_corpus_file
        
        if not os.path.exists(self.corpus_file):
            self.download_corpus()
        
        print(f"Czyszczenie korpusu...")
        with open(self.corpus_file, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        
        clean_text = self.clean_text(text)
        
        with open(self.clean_corpus_file, "w", encoding="utf-8") as f:
            f.write(clean_text)
        
        print(f"Oczyszczony korpus zapisano do pliku {self.clean_corpus_file}")
        return self.clean_corpus_file
    
    def average_length(self, message):
        """Oblicza średnią długość słowa w tekście."""
        words = message.split()
        if not words:
            return 0
        return sum(len(word) for word in words) / len(words)

    def build_character_markov_model(self, text, order):
        """Buduje model Markova określonego rzędu na poziomie znaków."""
        print(f"Budowanie modelu znakowego rzędu {order}...")
        model = defaultdict(Counter)
        
        # Przetwarzanie tekstu partiami, aby oszczędzać pamięć
        chunk_size = 1000000  # 1MB
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size+order]  # Dodajemy order, aby uwzględnić granice chunków
            
            for j in range(len(chunk) - order):
                context = chunk[j:j+order]
                next_char = chunk[j+order]
                model[context][next_char] += 1
                
            print(f"Przetworzono chunk {i//chunk_size + 1}/{(len(text)//chunk_size) + 1}")
        
        # Przekształcenie liczby wystąpień na prawdopodobieństwa
        probability_model = {}
        for context, counter in model.items():
            total = sum(counter.values())
            if total > 0:
                probability_model[context] = {next_char: count/total for next_char, count in counter.items()}
        
        print(f"Model znakowy rzędu {order} zbudowany. Liczba kontekstów: {len(probability_model)}")
        return probability_model

    def generate_text_from_model(self, model, length, order):
        """Generuje tekst na podstawie modelu Markova."""
        if not model:
            return ""
        
        # Wybierz losowy kontekst początkowy
        start_context = random.choice(list(model.keys()))
        
        result = start_context
        current = start_context
        
        # Generuj tekst znak po znaku
        for _ in range(length - order):
            if current not in model:
                # Jeśli bieżący kontekst nie występuje w modelu, wybierz nowy losowo
                current = random.choice(list(model.keys()))
            
            next_chars = list(model[current].keys())
            next_probs = list(model[current].values())
            
            next_char = random.choices(next_chars, weights=next_probs)[0]
            result += next_char
            
            # Aktualizuj kontekst, przesuwając "okno" o jeden znak
            current = current[1:] + next_char
        
        return result

    def build_word_markov_model(self, text, order):
        """Buduje model Markova na poziomie słów."""
        print(f"Budowanie modelu słownego rzędu {order}...")
        words = text.split()
        
        model = defaultdict(Counter)
        
        # Przetwarzanie słów partiami, aby oszczędzać pamięć
        for i in range(len(words) - order):
            if i % 1000000 == 0:
                print(f"Przetworzono {i/1000000:.1f} milionów słów...")
                
            context = tuple(words[i:i+order])
            next_word = words[i+order]
            model[context][next_word] += 1
        
        # Przekształcenie na prawdopodobieństwa
        prob_model = {}
        for context, counter in model.items():
            total = sum(counter.values())
            prob_model[context] = {word: count/total for word, count in counter.items()}
        
        print(f"Model słowny rzędu {order} zbudowany. Liczba kontekstów: {len(prob_model)}")
        return prob_model

    def generate_text_from_word_model(self, model, length, order):
        """Generuje tekst na podstawie modelu słownego Markova."""
        if not model:
            return ""
        
        # Wybierz losowy kontekst początkowy
        current_context = random.choice(list(model.keys()))
        result = list(current_context)
        
        # Generuj tekst słowo po słowie
        for _ in range(length - order):
            if current_context in model:
                next_words = list(model[current_context].keys())
                next_probs = list(model[current_context].values())
                next_word = random.choices(next_words, weights=next_probs)[0]
            else:
                # Jeśli kontekst nie występuje, wybierz losowy kontekst
                current_context = random.choice(list(model.keys()))
                continue
            
            result.append(next_word)
            current_context = tuple(result[-order:])
        
        return " ".join(result)

    def generate_samples(self):
        """Generuje próbki tekstu przy użyciu modeli Markova różnych rzędów."""
        # Upewnij się, że mamy przygotowany oczyszczony korpus
        self.prepare_clean_corpus()
        
        print(f"Wczytywanie oczyszczonego korpusu z pliku {self.clean_corpus_file}...")
        with open(self.clean_corpus_file, "r", encoding="utf-8") as f:
            clean_text = f.read()
        
        # Parametry generowania tekstu
        character_text_length = 1000  # Długość generowanego tekstu znakowego
        word_text_length = 150        # Długość generowanego tekstu słownego
        
        # Generowanie tekstu używając modeli znakowych
        print("\n===== MODELE ZNAKOWE =====")
        for order in [5, 7, 9]:
            print(f"\n--- MODEL ZNAKOWY RZĘDU {order} ---")
            char_model = self.build_character_markov_model(clean_text, order)
            generated_text = self.generate_text_from_model(char_model, character_text_length, order)
            
            print(f"\nWygenerowany tekst (fragment):")
            print(generated_text[:500] + "..." if len(generated_text) > 500 else generated_text)
            
            # Zapisz pełny wygenerowany tekst do pliku
            output_file = os.path.join(self.corpus_dir, f"generated_char_order_{order}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(generated_text)
            print(f"Pełny wygenerowany tekst zapisano w pliku '{output_file}'")
        
        # Generowanie tekstu używając modeli słownych
        print("\n===== MODELE SŁOWNE =====")
        for order in [3, 5, 7, 10]:
            print(f"\n--- MODEL SŁOWNY RZĘDU {order} ---")
            word_model = self.build_word_markov_model(clean_text, order)
            generated_text = self.generate_text_from_word_model(word_model, word_text_length, order)
            
            print(f"\nWygenerowany tekst:")
            print(generated_text)
            
            # Zapisz wygenerowany tekst do pliku
            output_file = os.path.join(self.corpus_dir, f"generated_word_order_{order}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(generated_text)
            print(f"Wygenerowany tekst zapisano w pliku '{output_file}'")
        
        print("\nGotowe! Wszystkie wygenerowane teksty zostały zapisane do oddzielnych plików.")

def main():
    print("===== GENERATOR TEKSTU Z DUŻEGO KORPUSU - MODELE MARKOVA WYŻSZYCH RZĘDÓW =====")
    
    # Rozmiar korpusu w MB (możesz zmienić na pożądaną wartość)
    corpus_size_mb = 100
    
    # Inicjalizacja generatora
    generator = LargeCorpusMarkovGenerator(target_size_mb=corpus_size_mb)
    
    # Pobierz korpus (jeśli jeszcze nie istnieje)
    generator.download_corpus()
    
    # Wygeneruj próbki tekstu
    generator.generate_samples()

if __name__ == "__main__":
    main()