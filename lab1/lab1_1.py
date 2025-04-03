import random
import copy
from  string import ascii_lowercase, digits


alphabet = ascii_lowercase + digits + ' '
filename = 'norm_hamlet.txt'



def generate_random_string(charset, length):
    return ''.join(random.choice(charset) for _ in range(length))

def average_length(message):
    words = message.split() #podział message na słowa
    return sum(map(len, words)) / len(words) #suma długości słów podzielona przez liczbę słów


#Zadanie 1
def zeroRowApproximation():
    message = generate_random_string(alphabet, 100000)
    print(average_length(message))

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
    result = ''
    letters = [*freq_dict.keys()]
    weights = [*freq_dict.values()]
    for _ in range(length):
        result += random.choices(letters, weights=weights)[0]
    return result
    

def main():
    print("Zadanie 1:")
    zeroRowApproximation()
    print('')
    print("Zadanie 2:")
    file = read_file(filename)
    letter_freq = letter_frequency(file)
    print(sorted(letter_freq.items(), key=lambda item: item[1], reverse=True))
    print("Zadanie 3:")
    message = firstRowApproximation(1000)
    print(message)
    return True

if __name__ == '__main__':
    main()