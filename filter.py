#!/usr/bin/python3
import argparse

__author__ = 'th3s3cr3tag3nt'

def read_words(filename):
    """Read words from a file, return a set of words (case insensitive)."""
    with open(filename, 'r') as file:
        return set(word.strip().lower() for word in file)

def filter_words(word_file, common_file, output_file=None):
    """Filter words that are not in the common words file and print or save them."""
    # Read words from files
    words = read_words(word_file)
    common_words = read_words(common_file)

    # Filter words not in the common words file
    unique_words = words - common_words

    # Output results
    if output_file:
        with open(output_file, 'w') as file:
            for word in sorted(unique_words):
                file.write(word + '\n')
    else:
        for word in sorted(unique_words):
            print(word)

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
     _ __ ___  _   _ _ __   __ _  ___   _ __  _   _
    | '_ ' _ \\| | | | '_ \\ / _` |/ _ \\ | '_ \\| | | |
    | | | | | | |_| | | | | (_| |  __/_| |_) | |_| |
    |_| |_| |_|\\__,_|_| |_|\\__, |\\___(_) .__/ \\__, |
                           |___/       |_|    |___/

    Filter out commons words.
    '''
    )
    parser.add_argument("word_file", help="The file containing a list of words to filter.")
    parser.add_argument("common_file", help="The file containing common words.")
    parser.add_argument("-o", "--output", help="The output file to save results. If not provided, results are printed.")
    args = parser.parse_args()

    # Call the filter function with the provided arguments
    filter_words(args.word_file, args.common_file, args.output)

if __name__ == "__main__":
    main()

