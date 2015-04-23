# Alfred Rates #
[![Build Status](https://travis-ci.org/kennedyoliveira/alfred-rates.svg?branch=master)](https://travis-ci.org/kennedyoliveira/alfred-rates)
[![Code Health](https://landscape.io/github/kennedyoliveira/alfred-rates/master/landscape.svg?style=flat)](https://landscape.io/github/kennedyoliveira/alfred-rates/master)

#### Rates exchange for alfred. ####

Convert between many currencies using the YQL (Yahoo! Query Language) to get the exchange rates in realtime for free.

### Usage: ###

`rate <VAL> <CUR SRC> <CUR DST>` -> Convert the value <VAL> from the currency <CUR SRC> to the currency <CUR DST>. Example: `rate 100 BRL USD`

`rate <VAL> <CUR DST>` -> Convert the value <VAL> to the default currency setted with ratesetcurrency comand.

`rate <CUR SRC> <VAL>` -> Convert the value <VAL> from the currency <CUR SRC> to the default currency setted with ratesetcurrency command.

`rate <CUR DST>` -> Convert the default currency to the `<CUR DST>`, just to show the rates.

`ratesetcurrency` -> Set the default currency, for use with the comands `rate <VAL> <CUR DST>` and `rate <CUR SRC> <VAL>`


##### TODO List #####
 - [ ] Add more currencies info (The script will work, just need some info to validate).
 - [ ] Refactor the script (I'm not a pro python coder, just started to learn and did this as first project).
 - [ ] Show currencies while user is typing, to help when you don't remember the currency code.
