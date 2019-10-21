#!/usr/bin/env python3

# By Fantin Bibas
# 2019/10/18

import sys
import math
import re
import functools
import collections
import string


english_letter_frequencies = {
    'E': .12,
    'T': .091,
    'A': .0812,
    'O': .0768,
    'I': .0731,
    'N': .0695,
    'S': .0628,
    'R': .0602,
    'H': .0592,
    'D': .0432,
    'L': .0398,
    'U': .0288,
    'C': .0271,
    'M': .0261,
    'F': .023,
    'Y': .0211,
    'W': .0209,
    'G': .0203,
    'P': .0182,
    'B': .0149,
    'V': .0111,
    'K': .0069,
    'X': .0017,
    'Q': .0011,
    'J': .001,
    'Z': .0007
}


def clean(string):
    return re.sub(r'[^A-Z]', '', string.upper())


def find_repetitions(cipher, min_size):
    repeated = []
    for i in range(len(cipher) - min_size):
        for j in range(i + 1, len(cipher) - min_size + 1):
            if cipher[i:i + min_size] == cipher[j:j + min_size]:
                repeated.append((i, j))
    return repeated


def kasiski(cipher, min_size=4):
    offsets = [b - a for (a, b) in find_repetitions(cipher, min_size)]
    key_lengths = {}

    def inc_key_length(length):
        if length > 1:
            if length not in key_lengths.keys() and length:
                key_lengths[length] = 0
            key_lengths[length] += 1

    for offset in offsets:
        for diviser in range(1, math.floor(math.sqrt(offset)) + 1):
            if offset % diviser == 0:
                inc_key_length(diviser)
                opposite = offset // diviser
                if opposite != diviser:
                    inc_key_length(opposite)
    best_matches = sorted(key_lengths.items(), key=lambda x: (x[1], x[0]), reverse=True)
    return best_matches[0][0]


def index_of_coincidence(cipher, top=5):
    shifted = cipher
    offsets = {}
    for key_length in range(1, len(shifted) - 1):
        offsets[key_length] = 0
        shifted = shifted[1:]
        for i in range(len(shifted)):
            if cipher[i] == shifted[i]:
                offsets[key_length] += 1
    best_offsets = sorted(offsets.items(), key=lambda x: (x[1], x[0]), reverse=True)
    return functools.reduce(math.gcd, [offset for (offset, _) in best_offsets[:top]])


def split_vigenere(cipher):
    key_length = index_of_coincidence(cipher)
    return [cipher[i::key_length] for i in range(key_length)]


def english_matching_index(text):
    size = len(text)
    occurrences = collections.Counter(text)
    score = 0
    for letter, frequency in english_letter_frequencies.items():
        score += abs(frequency - (occurrences[letter] / size))
    return score


def crack_caesar(cipher):

    def shift_letter(letter, shift):
        letter = ord(letter) + shift
        if letter > 90:
            letter -= 26
        return chr(letter)

    caesars = []
    for i in range(26):
        text = ''.join([shift_letter(letter, i) for letter in cipher])
        caesars.append((english_matching_index(text), text, 65 + (26 - i) % 26))
    caesars = sorted(caesars)
    return caesars[0]


def main(argv):
    raw = argv[1]
    cipher = clean(raw)
    print('Clean cipher:\n')
    print(cipher)
    print('---')
    print('Best Kasiski key length is: {}'.format(kasiski(cipher)))
    print('Index of coincidence gives a key length of: {}'.format(index_of_coincidence(cipher)))
    print('---')
    columns = split_vigenere(cipher)
    cracked_columns = []
    print('Splitted cipher:\n')
    for column in columns:
        print('\t' + column)
        cracked_column = crack_caesar(column)
        cracked_columns.append(cracked_column)
        print('\tCaesar crack with index of ~{:.2}:'.format(cracked_column[0]))
        print('\t->\t' + cracked_column[1])
    print('---')
    plain = ''
    for i in range(len(cracked_columns[0][1])):
        for cracked_column in cracked_columns:
            if i < len(cracked_column[1]):
                plain += cracked_column[1][i]
    print('Merged result:\n')
    print(plain)
    print('---')
    clean_plain = ''
    j = 0
    for i in range(len(raw)):
        if raw[i] in string.ascii_uppercase:
            clean_plain += plain[j]
            j += 1
        elif raw[i] in string.ascii_lowercase:
            clean_plain += plain[j].lower()
            j += 1
        else:
            clean_plain += raw[i]
    print('Cleaned result:\n')
    print(clean_plain)
    print('---')
    print('Key: ' + ''.join([chr(cracked_column[2]) for cracked_column in cracked_columns]))
    return 0


if __name__ == '__main__':
    exit(main(sys.argv))
