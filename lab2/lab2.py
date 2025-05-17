import re
import random
from collections import Counter, defaultdict

# --- 1. Przygotowanie korpusu ---
with open('norm_wiki_sample.txt', 'r', encoding='utf-8') as f:
    text = f.read().lower()
# Tokenizacja: słowa angielski, dopuszczamy apostrofy
words = re.findall(r"[a-z']+", text)
total_tokens = len(words)

# --- 2. Statystyki częstości ---
freq = Counter(words)
unique_types = len(freq)

def coverage(n):
    """
    Zwraca procent pokrycia (udział) top-n najczęstszych słów.
    """
    topn_count = sum(count for _, count in freq.most_common(n))
    return topn_count / total_tokens * 100

# Pokrycie dla 6000 i 30000
cov_6000 = coverage(6000)
cov_30000 = coverage(30000)
print(f"Coverage top 6000 words:  {cov_6000:.2f}%")
print(f"Coverage top 30000 words: {cov_30000:.2f}%\n")

# 10 najczęstszych słów
top10 = freq.most_common(10)
print("Top 10 słów (word, count, %):")
for word, count in top10:
    print(f"{word:<12} {count:>8}  {count/total_tokens*100:>6.2f}%")

# --- 3. Generacja Unigramowa (model zerowy) ---
vocab, counts = zip(*freq.items())
probs = [c/total_tokens for c in counts]

def generate_unigram(n):
    """Generuje ciąg n słów z rozkładu unigramowego."""
    return random.choices(vocab, weights=probs, k=n)

print("\nPrzykład z modelu unigramowego:")
print(' '.join(generate_unigram(20)))

# --- 4. Metoda Shannon'a (przykład dla bigramów) ---
def generate_shannon_bigram(start_word, length):
    """
    Dla danego prev_word losuje kolejny wyraz przeszukując korpus:
    znajduje wszystkie miejsca, gdzie prev_word występuje, i losuje 'następnik'.
    """
    seq = [start_word]
    positions = [i for i, w in enumerate(words[:-1]) if w == start_word]
    if not positions:
        # fallback do unigramu
        return generate_unigram(length)
    for _ in range(length - 1):
        positions = [i for i, w in enumerate(words[:-1]) if w == seq[-1]]
        if not positions:
            seq.append(random.choice(vocab))
        else:
            idx = random.choice(positions)
            seq.append(words[idx + 1])
    return seq

print("\nPrzykład Shannon bigram: ")
print(' '.join(generate_shannon_bigram('probability', 20)))

# --- 5. Model Markowa I rzędu ---
transition1 = defaultdict(Counter)
for prev, curr in zip(words, words[1:]):
    transition1[prev][curr] += 1

# Precompute probabilities
probs1 = {
    prev: {w: cnt / sum(counter.values()) for w, cnt in counter.items()}
    for prev, counter in transition1.items()
}

def generate_markov_bigram(start_word, length):
    seq = [start_word]
    for _ in range(length - 1):
        curr = seq[-1]
        if curr not in probs1:
            # fallback do unigramu
            seq.append(random.choices(vocab, weights=probs)[0])
        else:
            choices, weights = zip(*probs1[curr].items())
            seq.append(random.choices(choices, weights=weights)[0])
    return seq

print("\nPrzykład Markov I rzędu:")
print(' '.join(generate_markov_bigram('probability', 20)))

# --- 6. Model Markowa II rzędu ---
transition2 = defaultdict(Counter)
for w1, w2, w3 in zip(words, words[1:], words[2:]):
    transition2[(w1, w2)][w3] += 1

probs2 = {
    prev: {w: cnt / sum(counter.values()) for w, cnt in counter.items()}
    for prev, counter in transition2.items()
}

def generate_markov_trigram(start_pair, length):
    seq = list(start_pair)
    for _ in range(length - 2):
        key = (seq[-2], seq[-1])
        if key not in probs2:
            # fallback do bigramu
            seq.append(random.choices(vocab, weights=probs)[0])
        else:
            choices, weights = zip(*probs2[key].items())
            seq.append(random.choices(choices, weights=weights)[0])
    return seq

print("\nPrzykład Markov II rzędu:")
print(' '.join(generate_markov_trigram(('probability', 'of'), 20)))
