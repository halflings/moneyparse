#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import urllib2

RELEVANT_CHAR = '[0-9,\.]'

CURRENCY_MAP = {'eur' : ('€', 'eur', 'euro'),
                'gbp' : ('£', 'gbp', 'pound'),
                'usd' : ('$', 'usd', 'dollar'),
                'cny' : ('cny', 'yuan'),
                'jpy' : ('円', '圓', '¥', 'yen'),
                'sek' : ('sek'),
                'twd' : ('twd', 'nt$'),
                'vnd' : ('vnd', '₫'),
                'ars' : ('ars'),
                'mad' : ('mad', 'dh'),
                'inr' : ('inr', '₹')} 

RATE_EXCHANGE_API = 'http://rate-exchange.appspot.com/currency?from={}&to={}'


class Currency(object):

    conversion_rate = dict()

    def __init__(self, raw_repr):
        raw_repr = raw_repr.strip().lower()

        # Stripping the input from superfluous characters to get its value
        money = ''.join(c for c in raw_repr if re.match(RELEVANT_CHAR, c))
        money = money.replace(',', '')

        try:
            value = float(money)
        except ValueError:
            raise ValueError("The given input couldn't be parsed as a monetary value.")

        self.value = value

        self.currency = None
        for currency, signatures in CURRENCY_MAP.iteritems():
            if any(sig in raw_repr for sig in signatures):
                self.currency = currency
                break

    def to(self, target_currency):
        target_currency = target_currency.lower()

        if not self.currency:
            raise ValueError('Cannot convert an unknown currency')
        if target_currency == self.currency:
            return
        if not target_currency in CURRENCY_MAP:
            raise ValueError('Unknown currency "{}"'.format(currency))

        if (self.currency, target_currency) in Currency.conversion_rate:
            conversion_rate = Currency.conversion_rate[(self.currency, target_currency)]
        else:
            api_call = urllib2.urlopen(RATE_EXCHANGE_API.format(self.currency, target_currency))
            conversion_rate = json.loads(api_call.read())['rate']
            Currency.conversion_rate[(self.currency, target_currency)] = conversion_rate

        self.value *= conversion_rate
        self.currency = target_currency

    @staticmethod
    def flush_cache():
        Currency.conversion_rate = dict()

    def __str__(self):
        s = str(self.value)
        if self.currency:
            s += CURRENCY_MAP[self.currency][0].upper()
        return s

if __name__ == '__main__':

    c = Currency('$399,394')
    print c

    c.to('EUR')
    print c

    c.to('MAD')
    print c

    # Remember: rate exchange isn't symetric
    c.to('EUR')
    print c

    print Currency('300')