![munge](munge.png)
# Munge

A dirty little python script to munge dictionary words into possible passwords.

Example usage:

./munge.py -l 9 -i dictionary.txt -o munged.txt

# Optimise Wordlists

Enforce password policy to optimise dictionaries for brute force tests.

Example usage:

./munge.py --mode policy -i munged.txt -o optimised.txt

Remove common words from custom dictionaries (say from website scraping using cewl)

./munge.py -i wordlist.txt --exclude-file common_words.txt -o optimised.txt

# Why?

Sometimes you need to generate a realistic set of passwords for security testing. You might need to generate a set of hashes of common passwords, or generate a wordlist for hydra or burpsuite. This isn't a replacement for hashcat rules, it's just a handy script.