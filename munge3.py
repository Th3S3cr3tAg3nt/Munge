#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
from yaml import safe_load
from string import punctuation
from itertools import combinations
from re import sub
from pyfiglet import Figlet

__progname__='munge3.py'
__version__='0.0.1'
__author__='Zizzix (zizzixsec@gmail.com)'
__description__='a dirty little word munger for python3'


class munger():
	def __init__(self, args):
		self.args = args
		self.wordarray = []
		
		try:
			with open(self.args.definitions, 'r') as fd:
				self.definitions = safe_load(fd)
		except (FileNotFoundError, PermissionError) as msg:
			msg = ' '.join(str(msg).split(' ')[2:])
			exit(f'[!] {msg}')
	
	def main(self):
		if not self.args.quiet:
			self.banner()
		self.get_words()
		self.munge()
		self.output()
	
	def get_words(self):
		if self.args.single:
			self.wordarray.append(self.args.single.lower())
		else:
			try:
				path = Path(self.args.wordlist)
				with open(path, 'r') as fd:
					data = fd.readlines()
				[self.wordarray.append(item.rstrip()) for item in data]
			except (FileNotFoundError, PermissionError) as msg:
				msg = ' '.join(str(msg).split(' ')[2:])
				exit(f'[!] {msg}')

	def munge(self):
		_tmp = []

		if self.definitions['basic']['enabled']:
			_tmp.extend([word.upper() for word in self.wordarray])
			_tmp.extend([word.capitalize() for word in self.wordarray])
			_tmp.extend([word.capitalize().swapcase() for word in self.wordarray])
			self.wordarray.extend(_tmp)
			_tmp.clear()

		if self.definitions['prepend']['enabled']:
			self.wordarray.extend([f'{p}{word}' \
				for p in self.definitions['prepend']['munge'] \
					for word in self.wordarray])
		
		if self.definitions['numbers']['enabled']:
			self.wordarray.extend([f'{word}{num}' for num in range( \
				self.definitions['numbers']['start'], self.definitions['numbers']['end']+1) \
					for word in self.wordarray])
		
		if self.definitions['punctuation']['enabled']:
			punc = [''.join(p) for p in list(combinations( \
				punctuation, self.definitions['punctuation']['count']))]
			self.wordarray.extend([f'{word}{p}' for p in punc\
				for word in self.wordarray])

		if self.definitions['append']['enabled']:
			self.wordarray.extend([f'{word}{a}' \
				for a in self.definitions['append']['munge'] \
					for word in self.wordarray])

		if self.definitions['transform']['enabled']:
			self.wordarray.extend([sub(rf'{_rule[0]}',f'{_rule[1]}', _word) \
				for _rule in self.definitions['transform']['munge'] \
					for _word in self.wordarray if _rule[0] in _word])

	def output(self):
		if self.args.output:
			path = Path(self.args.output)

			if not self.args.force:
				if path.exists():
					msg = f'File exists! Use -F to force: {self.args.output}'
					exit(f'[!] {msg}')
			with open(path, 'w') as fd:
				for word in self.wordarray:
					fd.writelines(f'{word}\n')
		else:
			[print(item) for item in self.wordarray]

	def banner(self):
		fmt = Figlet(font='larry3d')
		print(f'''
		{fmt.renderText(__progname__)}
		--- {__description__.title()} ---
		Version: {__version__}
		Authors: {__author__}
		''')


def get_args():
	parser = ArgumentParser()

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-s', '--single', action='store', help='Single mode.')
	group.add_argument('-w', '--wordlist', action='store', help='Wordlist mode.')

	parser.add_argument('-o', '--output', action='store', help='Output to new file.')
	parser.add_argument('-F', '--force', action='store_true', help='Overwrite existing file.')
	parser.add_argument('-q', '--quiet', action='store_true', help='Hide banner')
	parser.add_argument('-d', '--definitions', action='store', default=('definitions.yml'), \
		help='Definitions file')
	
	return parser.parse_args()


if __name__=='__main__':
	args = get_args()
	M = munger(args)
	M.main()