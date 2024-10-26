#!/usr/bin/python3
import argparse

__author__ = 'th3s3cr3tag3nt'

# Argument parser setup
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''\
 _ __ ___  _   _ _ __   __ _  ___   _ __  _   _
| '_ ' _ \\| | | | '_ \\ / _` |/ _ \\ | '_ \\| | | |
| | | | | | |_| | | | | (_| |  __/_| |_) | |_| |
|_| |_| |_|\\__,_|_| |_|\\__, |\\___(_) .__/ \\__, |
                       |___/       |_|    |___/

Dirty little word munger by Th3 S3cr3t Ag3nt.
'''
)
parser.add_argument('word', metavar='word', nargs='?', help='word to munge')
parser.add_argument('-l', '--level', type=int, default=5, help='munge level [0-9] (default 5)')
parser.add_argument('-i', '--input', help='input file')
parser.add_argument('-o', '--output', help='output file')
args = parser.parse_args()

# Validate level argument
args.level = max(0, min(args.level, 9))

# Helper function for leet transformations
def leet_transform(word, patterns):
    for pattern in patterns:
        yield ''.join(pattern.get(char, char) for char in word)

# Define transformation patterns for various levels
leet_patterns = [
    {},  # No transformation
    {'e': '3', 'a': '4', 'o': '0', 'i': '1', 'l': '1', 's': '$'},  # Leet set 1
    {'e': '3', 'a': '@', 'o': '0', 'i': '1', 'l': '1', 's': '$'},  # Leet set 2
    {'e': '3', 'a': '4', 'o': '0', 'i': '!', 'l': '1', 's': '$'},  # Leet set 3
    {'e': '3', 'a': '@', 'o': '0', 'i': '!', 'l': '1', 's': '$'},  # Leet set 4
    {'e': '3', 'a': '4', 'o': '0', 'i': '1', 'l': '1', 's': '5'},  # Leet set 5
    {'e': '3', 'a': '@', 'o': '0', 'i': '1', 'l': '1', 's': '5'},  # Leet set 6
    {'e': '3', 'a': '4', 'o': '0', 'i': '!', 'l': '1', 's': '5'},  # Leet set 7
    {'e': '3', 'a': '@', 'o': '0', 'i': '!', 'l': '1', 's': '5'},  # Leet set 8
]

# Generate capitalization variants
def capitalize_variants(word):
    """Generate different capitalization forms for a word."""
    return {word, word.upper(), word.capitalize(), word.lower()}

# Generate transformations based on level
def munge(word, level):
    transformations = set()
    for variant in capitalize_variants(word):
        transformations.add(variant)
        if level > 4:
            transformations |= set(leet_transform(variant, leet_patterns[:level - 4]))
    return transformations

# Apply transformations and append suffixes
def munge_with_suffixes(word, level):
    suffixes = []
    if level > 4:
        suffixes.extend(['1', '123456', '12', '2', '123', '!', '.', '2'])
    if level > 6:
        suffixes.extend([
            '?', '_', '0', '01', '69', '23', '24', '25', '1234', '8', '9', '10', 
            '11', '13', '3', '4', '5', '6', '7'
        ])
    if level > 7:
        suffixes.extend([
            '07', '08', '09', '14', '15', '16', '17', '18', '19', '21', '22', '20', 
            '77', '88', '99', '12345', '123456789'
        ])
    if level > 8:
        suffixes.extend([
            '00', '02', '03', '04', '05', '06', '19', '20', '25', '26', '27', 
            '28', '007', '1234567', '12345678', '111111', '111', '777', '666', 
            '101', '33', '44', '55', '66', '2022', '2023', '2024', '2025', '86', 
            '2021', '2020', '2019', '87', '89', '90', '91', '92', '93', '94'
            '95', '98'
        ])

    munged_words = munge(word, level)
    for suffix in suffixes:
        for variant in capitalize_variants(word):
            munged_words |= munge(variant + suffix, level)
    return munged_words

# Generate munged words from input
def generate_wordlist(word_list, level):
    result = set()
    for word in word_list:
        word = word.strip().lower()
        result |= munge_with_suffixes(word, level)
    return result

# Main logic for handling input/output
def main():
    word_list = []
    if args.word:
        word_list.append(args.word)
    elif args.input:
        try:
            with open(args.input) as f:
                word_list = f.readlines()
        except IOError:
            print(f"Exiting\nCould not read file: {args.input}")
            return
    else:
        print("Nothing to do!!\nTry -h for help.\n")
        return

    wordlist = generate_wordlist(word_list, args.level)
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write('\n'.join(wordlist) + '\n')
            print(f"Written to: {args.output}")
        except IOError:
            print(f"Exiting\nCould not write file: {args.output}")
    else:
        for word in wordlist:
            print(word)

if __name__ == "__main__":
    main()
