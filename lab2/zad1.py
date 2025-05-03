import re
from collections import Counter

with open('norm_wiki_sample.txt', 'r', encoding='utf-8') as f:
    text = f.read().lower()

words = re.findall(r"[a-z]+", text)
total_tokens = len(words)
freq = Counter(words)
unique_types = len(freq)

def coverage(n):
    topn = sum(count for _, count in freq.most_common(n))
    return topn / total_tokens * 100

cov_6000 = coverage(6000)
cov_30000 = coverage(30000)

print(f"Coverage top 6000 words:  {cov_6000:.2f}%")
print(f"Coverage top 30000 words: {cov_30000:.2f}%\n")

top10 = freq.most_common(10)

import pandas as pd

df = pd.DataFrame(top10, columns=['word', 'count']) 
df['percent_total'] = df['count'] / total_tokens * 100

print(df.to_string(index=False))

vocab, counts = zip(*freq.items())
total = sum(counts)
probs = [c/total for c in counts]

import random

def generate_unigram_sequence(n):
    return random.choices(vocab, weights=probs, k=n)

seq = generate_unigram_sequence(20)
print(' '. join(seq))

from collections import defaultdict

transition1 = defaultdict(Counter)
for prev, curr in zip(words, words[1:]):
    transition1[prev][curr] += 1

probs1 = {}
for prev, counter in transition1.items():
    total = sum(counter.values())
    probs1[prev] = {word: count / total for word, count in counter.items()}

import random

def generate_bigram(start, length):
    seq = [start]
    for _ in range(length-1):
        choices, weights = zip(*probs1[seq[-1]].items())
        seq.append(random.choices(choices, weights=weights)[0])
    return seq

print(' '.join(generate_bigram('probability', 50)))


transitions2 = defaultdict(Counter)
for w1, w2, w3 in zip(words, words[1:], words[2:]):
    transitions2[(w1, w2)][w3] += 1

probs2 = {}
for prev2, counter in transitions2.items():
    total = sum(counter.values())
    probs2[prev2] = [(word, count/total) for word, count in counter.items()]

def generate_trigram(start_pair, length):
    seq = list(start_pair)
    for _ in range(length-2):
        key = tuple(seq[-2:])
        choices, weights = zip(*probs2[key])
        next_word = random.choices(choices, weights=weights)[0]
        seq.append(next_word)
    return seq

print(' '.join(generate_trigram(('probability','of'), 50)))


