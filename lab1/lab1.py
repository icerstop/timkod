import random
from  string import ascii_lowercase


alphabet = ascii_lowercase + ' '
filename = 'norm_hamlet.txt'



def generate_random_string(charset, length):
    return ''.join(random.choice(charset) for _ in range(length))

def average_length(message):
    words = message.split() #podział message na słowa
    return sum(map(len, words)) / len(words) #suma długości słów podzielona przez liczbę słów


#Zadanie 1
def zero_row_approximation():
    message = generate_random_string(alphabet, 100000)
    print(average_length(message))

def read_file(filename):
    file = open(filename, 'r')
    return file

#Zadanie 2
def letter_frequency(file):
    dictionary = dict.fromkeys(alphabet, 0)
    for line in file:
        for char in line:
            dictionary[char] += 1
    dictionary = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)
    return dictionary

#Zadanie 3
def first_row_approximation(length, letter_freq):
    result = ''
    letters = [pair[0] for pair in letter_freq]
    weights = [pair[1] for pair in letter_freq]
    for _ in range(length):
        result += random.choices(letters, weights)[0]
    print(result)
    print('\n')
    print(average_length(result))
    #return result

#Zadanie 4
def conditional_probabilities(text, alphabet):
    return True

def main():
    print("Zadanie 1:")
    zero_row_approximation()
    print("\nZadanie 2:")
    file = read_file(filename)
    letter_freq = letter_frequency(file)
    print(letter_freq)
    print("\nZadanie 3:")
    first_row_approximation(1000, letter_freq)
    #result = first_row_approximation(1000, letter_freq)
    #print(letter_frequency(result))
    print("\nZadanie 4:")
    conditional_probabilities()
    return True

if __name__ == '__main__':
    main()
