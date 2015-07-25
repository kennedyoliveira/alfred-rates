# Alfred Rates #
[![Build Status](https://travis-ci.org/kennedyoliveira/alfred-rates.svg?branch=master)](https://travis-ci.org/kennedyoliveira/alfred-rates)
[![PayPayl donate button](http://img.shields.io/paypal/donate.png?color=yellow)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=CR4K3FDKKK5FA&lc=BR&item_name=Kennedy%20Oliveira&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted "Donate with paypal if you feels like helping me out :D")
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

Multiple queries example

![Alt text](screenshots/5.png?raw=true)

Converstion from one source to many destinations

![Alt text](screenshots/4.png?raw=true)

Math in the conversion:

![Alt text](screenshots/6.png?raw=true)

## New Features

You can do math with the values now!

### Example:

`rate 100*1.03 USD EUR` -> will do the math first and after get the rates!

You can do the basic math operations:

- Divide
- Multiply
- Sum
- Substract

You can see a conversion for many currencies!

### Example:

`rate 100 usd gbp cad inr`

![Alt text](screenshots/4.png?raw=true)

You can do many queries separing them with ";"

### Example: 

![Alt text](screenshots/5.png?raw=true)

### Usage: ###

`rate <VAL> <CUR SRC> <CUR DST>` -> Convert the value <VAL> from the currency <CUR SRC> to the currency <CUR DST>. Example: `rate 100 BRL USD`

`rate <VAL> <CUR DST>` -> Convert the value <VAL> to the default currency setted with ratesetcurrency comand.

`rate <CUR SRC> <VAL>` -> Convert the value <VAL> from the currency <CUR SRC> to the default currency setted with ratesetcurrency command.

`rate <CUR DST>` -> Convert the default currency to the `<CUR DST>`, just to show the rates.

`rate <VAL> <CUR SRC> <CUR DST1> <CUR DST2> <CUR DST3> <CUR DSTn...>`, Convert the value <VAL> from the currency <CUR SUR> to all the <CUR DST(num)>

`rate <VAL> <CUR SRC> <CUR DST>; <VAL> <CUR SRC> <CUR DST>;`, use the ";" to separate queries, you can run as many as you can and using any way, not just the `<VAL> <CUR SRC> <CUR DST>`

`ratesetcurrency` -> Set the default currency, for use with the comands `rate <VAL> <CUR DST>` and `rate <CUR SRC> <VAL>`

`rateclear` -> Clears all the cached data, used when there is a new version for removing olds caches.

## Donations: ##

If this workflow helps you and you feels like helping me back, please, consider making a donation, anything is a help!
There's a button in the top "paypal | donation", just click there.

Thanks for who helps, i'm glad that i can help you with the software too!
