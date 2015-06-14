# Alfred Rates #
[![Build Status](https://travis-ci.org/kennedyoliveira/alfred-rates.svg?branch=master)](https://travis-ci.org/kennedyoliveira/alfred-rates)
[![Code Health](https://landscape.io/github/kennedyoliveira/alfred-rates/master/landscape.svg?style=flat)](https://landscape.io/github/kennedyoliveira/alfred-rates/master)
[![Coverage Status](https://coveralls.io/repos/kennedyoliveira/alfred-rates/badge.svg?branch=master)](https://coveralls.io/r/kennedyoliveira/alfred-rates?branch=master)

#### Rates exchange for alfred. ####

Convert between many currencies using the YQL (Yahoo! Query Language) to get the exchange rates in realtime for free.

### Screenshots ###

Convert from USD to EUR

![Alt text](screenshots/1.png?raw=true)

Convert from default configured currency (BRL in my case) to USD

![Alt text](screenshots/2.png?raw=true)

Autocomplete example

![Alt text](screenshots/3.png?raw=true)

## New Features

You can do math with the values now!

### Example:

`rate 100*1.03 USD EUR` -> will do the math first and after get the rates!

You can do the basic math operations:

- Divide
- Multiply
- Sum
- Substract

### Usage: ###

`rate <VAL> <CUR SRC> <CUR DST>` -> Convert the value <VAL> from the currency <CUR SRC> to the currency <CUR DST>. Example: `rate 100 BRL USD`

`rate <VAL> <CUR DST>` -> Convert the value <VAL> to the default currency setted with ratesetcurrency comand.

`rate <CUR SRC> <VAL>` -> Convert the value <VAL> from the currency <CUR SRC> to the default currency setted with ratesetcurrency command.

`rate <CUR DST>` -> Convert the default currency to the `<CUR DST>`, just to show the rates.

`ratesetcurrency` -> Set the default currency, for use with the comands `rate <VAL> <CUR DST>` and `rate <CUR SRC> <VAL>`

`rateclear` -> Clears all the cached data, used when there is a new version for removing olds caches.
