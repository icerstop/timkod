import random
import copy
from  string import ascii_lowercase, digits
from collections import defaultdict, Counter
from visualizations import visualize_results

alphabet = ascii_lowercase + digits + ' '
filename = 'norm_wiki_sample.txt'

def generate_random_string(charset, length):
    return ''.join(random.choice(charset) for _ in range(length))

def average_length(message):
    words = message.split() #podział message na słowa
    return sum(map(len, words)) / len(words) if words else 0 #suma długości słów podzielona przez liczbę słów


#Zadanie 1
def zeroRowApproximation():
    message = generate_random_string(alphabet, 100000)
    print('\nŚrednia długość słowa - przybliżenie zerowego rzędu:\n', average_length(message))
    return message, average_length(message)

def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()

#Zadanie 2
def letter_frequency(content):
    dictionary = dict.fromkeys(alphabet, 0) #wartość początkowa to zero
    for char in content:
        if char in dictionary:
            dictionary[char] += 1
    return dictionary

#Zadanie 3
def firstRowApproximation(length):
    freq_dict = letter_frequency(read_file(filename))
    generated = ''
    letters = [*freq_dict.keys()]
    weights = [*freq_dict.values()]
    for _ in range(length):
        generated += random.choices(letters, weights=weights)[0]
    words = generated.split()
    if words:
        total_length = sum(len(word) for word in words)
        average = total_length / len(words)
    else: 
        average = 0

    return generated, average

#Zadanie 4
def conditional_probabilities(text, alphabet, letter_freq):
    most_common = [letter for letter, count in sorted(letter_freq.items(), key=lambda item: item[1], reverse=True)[:2]]
    print("Najczęściej występujące znaki:", most_common)

    pairs = defaultdict(int)
    for i in range(len(text) - 1):
        first, second = text[i], text[i + 1]
        if first in most_common:
            pairs[(first, second)] += 1

    conditional_probs = {letter: {} for letter in most_common}
    for (first, second), count in pairs.items():
        conditional_probs[first][second] = count  / letter_freq[first]
    
    for first_letter in most_common:
        print(f"Warunkowe prawdopodobieństwo dla '{first_letter}':")
        sorted_probs = sorted(conditional_probs[first_letter].items(), key=lambda item: item[1], reverse=True)
        for second_letter, prob in sorted_probs:
            print(f"P({second_letter} | {first_letter}) = {prob:.4f}")

    return conditional_probs


#Zadanie 5

def markov_approx(text, order, length, start_sequence=None):
    if order == 0:
        generated_text = generate_random_string(alphabet, length)
        return generated_text, average_length(generated_text)

    model = defaultdict(Counter)

    if order == 1:
        for i in range(len(text) - 1):
            current = text[i]
            next_char = text[i + 1]
            model[current][next_char] += 1
    else:
        for i in range(len(text) - order):
            context = text[i:i + order]
            next_char = text[i + order]
            model[context][next_char] += 1
    
    probability_model = {}

    for context, counter in model.items():
        total = sum(counter.values())
        if total > 0:
            probability_model[context] = {char: count / total for char, count in counter.items()}
    
    if not probability_model:
        return "", 0
    
    if start_sequence and len(start_sequence) == order:
        current = start_sequence
    elif order == 1:
        current = random.choice(list(probability_model.keys()))
    else:
        current = random.choice(list(probability_model.keys()))

    generated_text = current 

    for _ in range(length - len(current)):
        if current not in probability_model:
            current = random.choice(list(probability_model.keys()))
        next_chars = list(probability_model[current].keys())
        next_probs = list(probability_model[current].values())

        next_char = random.choices(next_chars, weights=next_probs)[0]
        generated_text += next_char

        if order > 1:
            current = current[1:] + next_char
        else:
            current = next_char 

    return generated_text, average_length(generated_text) 

def find_sequence(text, word, context):
    word = word.lower()
    text = text.lower()

    index = text.find(word)
    if index == -1:
        return None

    start = max(0, index - context + len(word))
    return text[start:index + len(word)]

def build_probability_model(text, order):
    model = defaultdict(Counter)
    for i in range(len(text) - order):
        context = text[i:i + order]
        next_char = text[i + order]
        model[context][next_char] += 1

    probability_model = {}
    for context, counter in model.items():
        total = sum(counter.values())
        if total > 0:
            probability_model[context] = {char: count / total for char, count in counter.items()}

    return probability_model


def main():
    letter_freq_data = {}
    avg_lengths_data = {}
    cond_probs_data = {}
    text_samples_data = {}

    print("Zadanie 1:")
    zero_text, zero_avg = zeroRowApproximation()
    avg_lengths_data["Przybliżenie zerowego rzędu"] = zero_avg
    text_samples_data["Przybliżenie zerowego rzędu"] = zero_text[:250]
    print('')

    print("\nZadanie 2:")
    file = read_file(filename)
    letter_freq = letter_frequency(file)
    letter_freq_data = letter_freq
    print('\n Liczba wystąpień znaków:\n', sorted(letter_freq.items(), key=lambda item: item[1], reverse=True))

    print("\nZadanie 3:")
    first_message, first_avg = firstRowApproximation(1000)
    avg_lengths_data["Przybliżenie pierwszego rzędu"] = first_avg
    text_samples_data["Przybliżenie pierwszego rzędu"] = first_message[:250]
    print('\nWygenerowana wiadomość:\n', first_message[:250], '\n')
    print('Średnia długość wygenerowanego słowa - przybliżenie I rzędu:\n ', first_avg, '\n')

    print("\nZadanie 4:")
    cond_probs = conditional_probabilities(file, alphabet, letter_freq)
    cond_probs_data = cond_probs

    print("\nZadanie 5:")

    print("\n# Przybliżenie źródła Markova 1-go rzędu:")
    text_1st, avg_1st = markov_approx(file, 1, 1000)
    avg_lengths_data["Przybliżenie Markova 1-go rzędu"] = avg_1st
    text_samples_data["Przybliżenie Markova 1-go rzędu"] = text_1st[:250]
    print("Wygenerowany tekst (fragment):", text_1st[:250])
    print(f"Średnia długość słowa w przybliżeniu 1-go rzędu: {avg_1st:.4f}")

    print("\n# Przybliżenie źródła Markova 3-go rzędu:")
    text_3rd, avg_3rd = markov_approx(file, 3, 1000)
    avg_lengths_data["Przybliżenie Markova 3-go rzędu"] = avg_3rd
    text_samples_data["Przybliżenie Markova 3-go rzędu"] = text_3rd[:250]
    print("Wygenerowany tekst (fragment):", text_3rd[:250])
    print(f"Średnia długość słowa w przybliżeniu 3-go rzędu: {avg_3rd:.4f}")

    print("\n# Przybliżenie źródła Markova 5-go rzędu:")
    text_5th, avg_5th = markov_approx(file, 5, 1000)
    avg_lengths_data["Przybliżenie Markova 5-go rzędu"] = avg_5th
    text_samples_data["Przybliżenie Markova 5-go rzędu"] = text_5th[:250]
    print("Wygenerowany tekst (fragment):", text_5th[:250])
    print(f"Średnia długość słowa w przybliżeniu 5-go rzędu: {avg_5th:.4f}")

    # print("\n# Przybliżenie źródła Markova 10-go rzędu:")
    # text_10th, avg_10th = markov_approx(file, 10, 1000)
    # avg_lengths_data["Przybliżenie Markova 10-go rzędu"] = avg_10th
    # text_samples_data["Przybliżenie Markova 10-go rzędu"] = text_10th[:100]
    # print("Wygenerowany tekst (fragment):", text_10th[:100])
    # print(f"Średnia długość słowa w przybliżeniu 10-go rzędu: {avg_10th:.4f}")

    word = 'probability'
    start_seq = word[-5:]
    text_5th_prob = word
    probability_model = build_probability_model(file, 5)

    for _ in range(1000 - len(word)):
        if start_seq not in probability_model:
            start_seq = random.choice(list(probability_model.keys()))
        next_chars = list(probability_model[start_seq].keys())
        next_probs = list(probability_model[start_seq].values())
        next_char = random.choices(next_chars, weights=next_probs)[0]
        text_5th += next_char
        start_seq = start_seq[1:] + next_char

    print(f"\nWygenerowany tekst (fragment z 'probability' na początku): {text_5th_prob[:100]}")
    avg_5th_prob = average_length(text_5th_prob)
    print(f"Średnia długość słowa w przybliżeniu 5-go rzędu z 'probability': {avg_5th_prob:.4f}")

    print("\nTworzenie wizualizacji wyników...")

    visualize_results(letter_freq_data, avg_lengths_data, cond_probs_data, text_samples_data)

    return True

if __name__ == '__main__':
    main()