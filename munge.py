#!/usr/bin/python
import argparse
__author__ = 'th3s3cr3tag3nt'

parser = argparse.ArgumentParser(description='Word munger for password cracking by Th3 S3cr3t Ag3nt.')
parser.add_argument('word', metavar='word',
                    help='word to munge')
parser.add_argument('-l','--level', type=int, default=5,
                    help='munge level [0-9] (default 5)')

parser.add_argument('--debug', dest='debug', action='store_const',
                    const=1, default=0,)

# Parse the arguments
args = parser.parse_args()

# Limit the level
if args.level > 9:
	args.level = 9;
if args.level < 0:
	args.level = 0;

# Display what we have.
if args.debug==1:
	print ("Word: %s" % args.word )
	print ("Level: %s" % args.level )

# create word list
wordlist = list()

def munge(wrd, level):
	global wordlist
	if level > 0:
		wordlist.append( wrd )
		#print wrd

	if level > 0:
		wordlist.append( wrd.upper() )

	if level > 0:
		wordlist.append( wrd.capitalize() )

	if level > 2:
		temp = wrd.capitalize()
		wordlist.append( temp.swapcase() )

	if level > 4:
		wordlist.append( wrd.replace('e', '3') )

	if level > 4:
		wordlist.append( wrd.replace('a', '4') )

	if level > 4:
		wordlist.append( wrd.replace('o', '0') )

	if level > 4:
		wordlist.append( wrd.replace('i', '!') )

	if level > 4:
		wordlist.append( wrd.replace('i', '1') )

	if level > 4:
		wordlist.append( wrd.replace('l', '1') )

	if level > 4:
		wordlist.append( wrd.replace('a', '@') )

	if level > 4:
		wordlist.append( wrd.replace('s', '$') )

	# Leet speak
	if level > 4:
		temp = wrd
		temp = temp.replace('e', '3')
		temp = temp.replace('a', '4')
		temp = temp.replace('o', '0')
		temp = temp.replace('i', '1')
		temp = temp.replace('s', '$')
		wordlist.append( temp )

	if level > 4:
		temp = wrd
		temp = temp.replace('e', '3')
		temp = temp.replace('a', '@')
		temp = temp.replace('o', '0')
		temp = temp.replace('i', '1')
		temp = temp.replace('s', '$')
		wordlist.append( temp )

	if level > 4:
		temp = wrd
		temp = temp.replace('e', '3')
		temp = temp.replace('a', '4')
		temp = temp.replace('o', '0')
		temp = temp.replace('i', '!')
		temp = temp.replace('s', '$')
		wordlist.append( temp )

	if level > 4:
		temp = wrd
		temp = temp.replace('e', '3')
		temp = temp.replace('a', '4')
		temp = temp.replace('o', '0')
		temp = temp.replace('l', '1')
		temp = temp.replace('s', '$')
		wordlist.append( temp )

	# Capitalize
	if level > 4:
		temp = wrd.capitalize()
		temp = temp.replace('e', '3')
		temp = temp.replace('a', '4')
		temp = temp.replace('o', '0')
		temp = temp.replace('i', '1')
		temp = temp.replace('s', '$')
		wordlist.append( temp )

	if level > 4:
		temp = wrd.capitalize()
		temp = temp.replace('e', '3')
		temp = temp.replace('a', '@')
		temp = temp.replace('o', '0')
		temp = temp.replace('i', '1')
		temp = temp.replace('s', '$')
		wordlist.append( temp )

	if level > 4:
		temp = wrd.capitalize()
		temp = temp.replace('e', '3')
		temp = temp.replace('a', '4')
		temp = temp.replace('o', '0')
		temp = temp.replace('i', '!')
		temp = temp.replace('s', '$')
		wordlist.append( temp )

	if level > 4:
		temp = wrd.capitalize()
		temp = temp.replace('e', '3')
		temp = temp.replace('a', '4')
		temp = temp.replace('o', '0')
		temp = temp.replace('l', '1')
		temp = temp.replace('s', '$')
		wordlist.append( temp )


wrd = args.word.lower()

munge(wrd, args.level)

if args.level > 6:
	munge(wrd + '!', args.level)
	munge(wrd + '.', args.level)
	munge(wrd + '?', args.level)
	munge(wrd + '_', args.level)
	munge(wrd + '1', args.level)

if args.level > 8:
	munge(wrd + '0', args.level)
	munge(wrd + '2', args.level)
	munge(wrd + '3', args.level)
	munge(wrd + '4', args.level)
	munge(wrd + '5', args.level)
	munge(wrd + '6', args.level)
	munge(wrd + '7', args.level)
	munge(wrd + '8', args.level)
	munge(wrd + '9', args.level)


wordlist = set(wordlist)

for word in wordlist:
	print(word)
