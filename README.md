# pyMnemo
Small python GUI to mnemomize numbers (using Mnemonic major system: https://en.wikipedia.org/wiki/Mnemonic_major_system)

For the moment the script uses an sqlite3 database for french and english words.

## Requirements
* python3
* pyQt5

## Usage
just run the file mnemo-qt5.py
Enter tne number you wish to mnemomize and the language.

The result is displayed as a list of comboboxes.
Each line display a possible solution. For example 7337 will display
* 7 33 7
* 7 337
* 73 37
* 733 7

Then each number display a drop down menu with a list of words associated with the same number.
By changing this number you will update the database by setting this specific word as default for the future requests.

Numbers with a blue background are number without default values.
Lines with red numbers is the shortest possibilities. In our example 
![7 337](https://placehold.it/30/ffffff/f03c15?text=+) `7 337`
![73 37](https://placehold.it/30/ffffff/f03c15?text=+) `73 37`
, and 
![733 7](https://placehold.it/30/ffffff/f03c15?text=+) `733 7`
 can express the number 7337 as a combination of 2 words (which is the shortest).
