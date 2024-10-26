#!/usr/bin/python3
import argparse
import os
import string
import re
__author__ = 'th3s3cr3tag3nt'

parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
	 description='''\
                                     _             _ _
  _ __  __ _ _______ __ _____ _ _ __| |  _ __  ___| (_)__ _  _
 | \'_ \/ _\' (_-<_-< V  V / _ \ \'_/ _\' | | \'_ \/ _ \ | / _| || |
 | .__/\__,_/__/__/\_/\_/\___/_| \__,_| | .__/\___/_|_\__|\_, |
 |_|                                    |_|               |__/

Password policy enforcer to optimise dictionaries by Th3 S3cr3t Ag3nt.

Eg. policy.py -luns --input passwords.txt

'''
					   )
parser.add_argument('--lowercase', '-l', action="store_true", dest="lowercase",
					default=False,
					help="Include lowercase.")

parser.add_argument('--uppercase', '-u', action="store_true", dest="uppercase",
					default=False,
					help="Include uppercase.")

parser.add_argument('--numeric', '-n', action="store_true", dest="numeric",
					default=False,
					help="Include numbers.")

parser.add_argument('--special', '-s', action="store_true", dest="special",
					default=False,
					help="Include special characters.")

parser.add_argument('-r','--rules', type=int, default=4,
					help='minimum number of rules to match [default 4]')

parser.add_argument('-m','--min', type=int, default=8,
					help='minimum password length [default 8]')

parser.add_argument('-M','--max', type=int, default=32,
					help='maximum password length [default 32]')

parser.add_argument('-i','--input', dest='input', required=True,
					help='input file')

parser.add_argument('-o','--output', dest='output',
					help='output file')

args = parser.parse_args()

# print(args)

def check_lowercase(password):
	flag=False
	for c in password:
		if c.islower():
			flag=True
			break
	return flag

def check_uppercase(password):
	flag=False
	for c in password:
		if c.isupper():
			flag=True
			break
	return flag

def check_numeric(password):
	flag=False
	for c in password:
		if c.isdigit():
			flag=True
			break
	return flag

def check_special(password):
	flag=False
	for c in password:
		if c.isalnum()==False:
			flag=True
			break
	return flag

def d_subs(plaintext, shifted_alphabet):
	alphabet = string.ascii_lowercase
	table = string.maketrans(shifted_alphabet, alphabet)
	return plaintext.translate(table)

if args.output:
	of = open(args.output, 'w')

if os.path.isfile(args.input):
	with open(args.input) as f:
		for line in f:
			policy=True
			rules=0
			if args.rules:
				minrules=args.rules
			else:
				minrules=99
			password=line.rstrip()
			if len(password)>0:
				if args.min:
					if len(password)<args.min:
						policy=False
						rules=-100
				if args.max:
					if len(password)>args.max:
						policy=False
						rules=-100
				if args.lowercase:
					if check_lowercase(password)==False:
						policy=False
					else:
						rules+=1;
				if args.uppercase:
					if check_uppercase(password)==False:
						policy=False
					else:
						rules+=1;
				if args.numeric:
					if check_numeric(password)==False:
						policy=False
					else:
						rules+=1;
				if args.special:
					if check_special(password)==False:
						policy=False
					else:
						rules+=1;
			else:
				policy=False;
			if policy==True or rules>=minrules:
				if args.output:
					of.write(password + '\n')
				else:
					print(password)
else:
	print ("Input file does not exist.");

if args.output:
	of.close()
