#!/usr/bin/python
import argparse
__author__ = 'th3s3cr3tag3nt'

parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
     description='''\
 _ __ ___  _   _ _ __   __ _  ___   _ __  _   _ 
| \'_ \' _ \| | | | \'_ \ / _\' |/ _ \ | \'_ \| | | |
| | | | | | |_| | | | | (_| |  __/_| |_) | |_| |
|_| |_| |_|\__,_|_| |_|\__, |\___(_) .__/ \__, |
                       |___/       |_|    |___/ 

Dirty little word munger by Th3 S3cr3t Ag3nt.
'''
                       )
parser.add_argument('word', metavar='word', nargs='?',
                    help='word to munge')

parser.add_argument('-l','--level', type=int, default=5,
                    help='munge level [0-9] (default 5)')

parser.add_argument('-i','--input', dest='input',
                    help='input file')

parser.add_argument('-o','--output', dest='output',
                    help='output file')

# Parse the arguments
args = parser.parse_args()

# Limit the level
if args.level > 9:
	args.level = 9;
if args.level < 0:
	args.level = 0;

# create word list
wordlist = list()

def munge(wrd, level):
	global wordlist
	if level > 0:
		wordlist.append( wrd )
		wordlist.append( wrd.upper() )
		wordlist.append( wrd.capitalize() )

	if level > 2:
		temp = wrd.capitalize()
		wordlist.append( temp.swapcase() )

	# Leet speak
	if level > 4:
		wordlist.append( wrd.replace('e', '3') )
		wordlist.append( wrd.replace('a', '4') )
		wordlist.append( wrd.replace('o', '0') )
		wordlist.append( wrd.replace('i', '!') )
		wordlist.append( wrd.replace('i', '1') )
		wordlist.append( wrd.replace('l', '1') )
		wordlist.append( wrd.replace('a', '@') )
		wordlist.append( wrd.replace('s', '$') )

	# Leet speak conmbinations
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

def mungeword(wrd, level):
	global wordlist
	munge(wrd, level)

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

if args.word:
	wrd = args.word.lower()
	mungeword(wrd. args.level)
elif args.input:
	## Open the file with read only permit
	try:
		with open(args.input) as f:
			for wrd in f:
				mungeword(wrd.rstrip(), args.level)
			f.close()
	except IOError:
		print "Exiting\nCould not read file:", args.input
else:
	print "Nothing to do!!\nTry -h for help.\n";

wordlist = set(wordlist)


if args.output:
	## Open the file with read only permit
	try:
		with open(args.output, 'w') as f:
			for word in wordlist:
				#print(word)
				f.write(word + "\n")
			f.close()
			print "Written to:", args.output
	except IOError:
		print "Exiting\nCould not write file:", args.input
else:
	for word in wordlist:
		print(word)
