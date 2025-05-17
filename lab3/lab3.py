from string import ascii_lowercase, digits
import math
from collections import Counter

# Alfabet - tylko małe litery, cyfry i spacje
ALPHABET = ascii_lowercase + digits + ' '

def load_text(filename):
    """Wczytuje tekst z pliku i filtruje znaki do dozwolonego alfabetu"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read().lower()
            # Zostawiamy tylko znaki z naszego alfabetu
            filtered_text = ''.join(c for c in text if c in ALPHABET)
            return filtered_text
    except Exception as e:
        print(f"Błąd wczytywania pliku {filename}: {e}")
        return ""

def char_entropy(text):
    """Oblicza entropię znaków zerowego rzędu (H0)"""
    if not text:
        return 0
    
    freq = Counter(text)
    total = sum(freq.values())
    return -sum((count/total) * math.log2(count/total) for count in freq.values() if count > 0)

def word_entropy(text):
    """Oblicza entropię słów zerowego rzędu (H0)"""
    words = text.split()
    if not words:
        return 0
    
    freq = Counter(words)
    total = sum(freq.values())
    return -sum((count/total) * math.log2(count/total) for count in freq.values() if count > 0)

def conditional_char_entropy(text, order=1):
    """Oblicza entropię warunkową znaków rzędu order"""
    if len(text) <= order:
        return 0
    
    # Zliczamy n-gramy długości order+1 i order
    ngrams_next = Counter([text[i:i+order+1] for i in range(len(text)-order)])
    ngrams_curr = Counter([text[i:i+order] for i in range(len(text)-order+1)])
    
    total_ngrams = sum(ngrams_next.values())
    entropy = 0
    
    for ngram_next, count in ngrams_next.items():
        prefix = ngram_next[:-1]
        # Obliczamy prawdopodobieństwo warunkowe P(znak|kontekst)
        prob = count / ngrams_curr[prefix]
        # Liczymy wkład do entropii warunkowej
        entropy -= (count / total_ngrams) * math.log2(prob)
    
    return entropy

def conditional_word_entropy(text, order=1):
    """Oblicza entropię warunkową słów rzędu order"""
    words = text.split()
    if len(words) <= order:
        return 0
    
    # Zliczamy n-gramy słów długości order+1 i order
    ngrams_next = Counter([tuple(words[i:i+order+1]) for i in range(len(words)-order)])
    ngrams_curr = Counter([tuple(words[i:i+order]) for i in range(len(words)-order+1)])
    
    total_ngrams = sum(ngrams_next.values())
    entropy = 0
    
    for ngram_next, count in ngrams_next.items():
        prefix = ngram_next[:-1]
        # Obliczamy prawdopodobieństwo warunkowe P(słowo|kontekst)
        prob = count / ngrams_curr[prefix]
        # Liczymy wkład do entropii warunkowej
        entropy -= (count / total_ngrams) * math.log2(prob)
    
    return entropy

def analyze_language(filename):
    """Analizuje plik tekstowy pod kątem entropii"""
    text = load_text(filename)
    if not text:
        return None
    
    results = {
        'filename': filename,
        'char_entropy': char_entropy(text),
        'word_entropy': word_entropy(text),
        'char_cond_entropy_1': conditional_char_entropy(text, 1),
        'char_cond_entropy_2': conditional_char_entropy(text, 2),
        'word_cond_entropy_1': conditional_word_entropy(text, 1),
        'word_cond_entropy_2': conditional_word_entropy(text, 2)
    }
    
    # Obliczamy stosunek entropii warunkowej do bezwarunkowej
    if results['char_entropy'] > 0:
        results['char_ratio_1'] = results['char_cond_entropy_1'] / results['char_entropy']
        results['char_ratio_2'] = results['char_cond_entropy_2'] / results['char_entropy']
    else:
        results['char_ratio_1'] = float('inf')
        results['char_ratio_2'] = float('inf')
    
    return results

def is_natural_language(results, threshold=0.8):
    """Decyduje czy tekst jest językiem naturalnym na podstawie progu entropii"""
    # Języki naturalne mają niski stosunek entropii warunkowej do bezwarunkowej
    return results['char_ratio_1'] < threshold

def main():
    """Główna funkcja programu"""
    print("\n=== Analiza języków referencyjnych ===\n")
    
    # Analizujemy języki referencyjne
    ref_langs = [
        ('norm_wiki_en.txt', 'Angielski'),
        ('norm_wiki_la.txt', 'Łaciński')
    ]
    
    # Dodatkowe języki opcjonalne
    opt_langs = [
        ('norm_wiki_eo.txt', 'Esperanto'),
        ('norm_wiki_et.txt', 'Estoński'),
        ('norm_wiki_so.txt', 'Somalijski'),
        ('norm_wiki_ht.txt', 'Haitański'),
        ('norm_wiki_nv.txt', 'Navaho')
    ]
    
    # Łączymy wszystkie języki do analizy
    all_langs = ref_langs + opt_langs
    
    # Przechowujemy wyniki dla języków referencyjnych
    ref_results = {}
    
    # Analizujemy języki referencyjne
    for file, name in all_langs:
        result = analyze_language(file)
        if result:
            ref_results[file] = result
            print(f"{name} ({file}):")
            print(f"  Entropia znaków (H0): {result['char_entropy']:.4f} bitów/znak")
            print(f"  Entropia słów (H0): {result['word_entropy']:.4f} bitów/słowo")
            print(f"  Entropia warunkowa znaków (H1): {result['char_cond_entropy_1']:.4f} bitów/znak")
            print(f"  Entropia warunkowa znaków (H2): {result['char_cond_entropy_2']:.4f} bitów/znak")
            print(f"  Entropia warunkowa słów (H1): {result['word_cond_entropy_1']:.4f} bitów/słowo")
            print(f"  Entropia warunkowa słów (H2): {result['word_cond_entropy_2']:.4f} bitów/słowo")
            print(f"  Stosunek H1/H0 (znaki): {result['char_ratio_1']:.4f}")
            print()
    
    # Znajdujemy średni próg dla języków naturalnych
    thresholds = [result['char_ratio_1'] for result in ref_results.values()]
    avg_threshold = sum(thresholds) / len(thresholds) if thresholds else 0.8
    
    # Używamy progu nieco wyższego niż średnia (z marginesem bezpieczeństwa)
    threshold = min(0.8, avg_threshold * 1.1)
    
    print(f"\n=== Klasyfikacja plików sample ===")
    print(f"Ustalony próg klasyfikacji: {threshold:.4f}\n")
    
    # Analizujemy próbki
    samples = [f"sample{i}.txt" for i in range(6)]  # sample0.txt - sample5.txt
    
    for sample in samples:
        result = analyze_language(sample)
        if result:
            is_natural = is_natural_language(result, threshold)
            verdict = "JĘZYK NATURALNY" if is_natural else "TEKST LOSOWY/SZTUCZNY"
            
            print(f"{sample}:")
            print(f"  Entropia znaków (H0): {result['char_entropy']:.4f} bitów/znak")
            print(f"  Entropia warunkowa znaków (H1): {result['char_cond_entropy_1']:.4f} bitów/znak")
            print(f"  Stosunek H1/H0 (znaki): {result['char_ratio_1']:.4f}")
            print(f"  Klasyfikacja: {verdict}")
            
            # Uzasadnienie odpowiedzi
            if is_natural:
                print(f"  Uzasadnienie: Stosunek entropii warunkowej do bezwarunkowej ({result['char_ratio_1']:.4f}) jest poniżej progu ({threshold:.4f}), co jest charakterystyczne dla języków naturalnych.")
            else:
                print(f"  Uzasadnienie: Stosunek entropii warunkowej do bezwarunkowej ({result['char_ratio_1']:.4f}) jest powyżej progu ({threshold:.4f}), co wskazuje na tekst losowy lub sztuczny.")
            print()

if __name__ == "__main__":
    main()
