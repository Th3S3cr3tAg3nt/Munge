*This project was inspired by: [Th3S3cr3tAg3nt](https://github.com/Th3S3cr3tAg3nt/Munge) and [John Hammond](https://www.youtube.com/watch?v=nNvhK1LUD48)*  

```
                                            __                          
                                           /'__`\                        
  ___ ___   __  __    ___      __      __ /\_\L\ \     _____   __  __    
/' __` __`\/\ \/\ \ /' _ `\  /'_ `\  /'__`\/_/_\_<_   /\ '__`\/\ \/\ \   
/\ \/\ \/\ \ \ \_\ \/\ \/\ \/\ \L\ \/\  __/ /\ \L\ \__\ \ \L\ \ \ \_\ \  
\ \_\ \_\ \_\ \____/\ \_\ \_\ \____ \ \____\\ \____/\_\\ \ ,__/\/`____ \ 
 \/_/\/_/\/_/\/___/  \/_/\/_/\/___L\ \/____/ \/___/\/_/ \ \ \/  `/___/> \
                               /\____/                   \ \_\     /\___/
                               \_/__/                     \/_/     \/__/ 
  
This code was written to bring munge to python3 with a definitions file.
```

# Table of Contents
1. [Installation](#Installation)
2. [Usage](#Usage)
3. [Operations](#Operations)
4. [Definitions](#Definitions)
5. [TODO](#TODO)

## Installation:
```bash
$ git clone https://github.com/lilragekitten/Munge.git
$ sudo pip install -r requirements.txt
$ chmod u+x ./munge3.py
```

## Usage:
```bash
$ ./munge3.py -h

usage: munge3.py [-h] (-s SINGLE | -w WORDLIST) [-o OUTPUT] [-F] [-q] [-d DEFINITIONS]

options:
  -h, --help                        show this help message and exit
  -s SINGLE, --single SINGLE        Single mode.
  -w WORDLIST, --wordlist WORDLIST  Wordlist mode.
  -o OUTPUT, --output OUTPUT        Output to new file.

  -F, --force           Overwrite existing file.
  -q, --quiet           Hide banner
  -d DEFINITIONS, --definitions DEFINITIONS Definitions file
```
The program can run in single "-s" or wordlist "-w" mode, but **you must select a mode**. The programs can output to stdout or to a file with "-o \<filename\>". If the output file exists, **you must use -F to force overwrite**. The banner can be silence with the "-q" option for use in scripting.

Each word will be processed through the munger function using the settings in the YAML definitions file(more info below).

The order of operations is: [basic, prepend, numbers, punctuation, append, transform]

## Operations
*even in single word mode, the words are processed as a list*  

All opererations can be disabled in the config file  

| Operation | Desciption |
|-----------|------------| 
| **basic** | First converts all the words in the list to upperscase and stores it in a temp list. Then converts the original words to a capitalized and appends again. Lastly converts the original words to capitalized and then swaps the case to invert them and appends one more time to the temp list. Then it extends the original word list in memory to include the temp list and clears the temp list. |
|**prepend**|Prepend the list of munges from the definitions file to the in memory wordlist.|
|**numbers**|Appends range of numbers from start to end value in definitions file and appends to in memory wordlist.| 
|**punctuation**|Appends number of punctuation in every combination using *python module: **string.punctuation*** to the in memory wordlist. The number of character in the combination is set with the definitions file.|
|**append**|Appends the list of munges from the definitions file to the in memory wordlist.|
|**transform**|Transforms character in the words using the munges in the definitions file to find the first char and replace with the second char, and append to the in memory wordlist.|  

## Definitions
The default definitions file is **definitions.yml** in the same directort as the script.

*Default definitions.yml file*
```
# definitions.yml file for munge3.py
basic:
  enabled: true

prepend:
  enabled: true
  munge: ['-','prod_']

numbers:
  enabled: true
  start: 2014
  end: 3050

punctuation:
  enabled: true
  count: 1

append:
  enabled: true
  munge: ['123456','_dev']

transform: 
  enabled: true
  munge: [
    ['a', '@'],
    ['a', '4'],
    ['A', '@'],
    ['A', '4'],
    ['e', '3'],
    ['E', '3'],
    ['i', '!'],
    ['i', '1'],
    ['I', '!'],
    ['I', '1'],
    ['l', '1'],
    ['L', '1'],
    ['s', '$'],
    ['s', '5'],
    ['S', '$'],
    ['S', '5']
  ]
```

## TODO
- [x] Written in Python3
- [x] Definition file in yaml to allow expansion of rules
- [x] Replace hardcoded title
- [x] Move to argparse and implement exclusive group for single and wordlist operation
- [x] Implement error checking for wordlists loading
- [x] Prevent accidental overwrite of existing files
- [x] Implement quiet mode for scripting
- [x] Move to a oop model to avoid globals
- [ ] find a way to removed the need for requirements.txt
