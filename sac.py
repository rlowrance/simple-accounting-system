import collections
import copy
import datetime

from typing import List

import utility as u

AccountDeclaration = collections.namedtuple('AccountDeclaration', 'category name')
Amount = collections.namedtuple('Amount', 'dollars cents')
Balance = collections.namedtuple('Balance', 'side amount')
JournalEntry = collections.namedtuple('JournalEntry', 'date amount debit_account credit_account description')
LedgerEntry = collections.namedtuple('LedgerEntry', 'account date balance description source location')


class InputError(Exception):
    def __init__(self, msg): self.msg = msg
    def __str__(self): return f'{self.msg}'


# Return type-checked value x
def checked(x, kind):
    assert isinstance(x, kind)
    return x

# Make a new instance with type-checked and normalized attributes
def make(kind, *args):
    if kind == 'AccountDeclaration':
        category, name = args
        assert category in {'Asset', 'Liability', 'Equity', 'Revenue', 'Expense'}
        return AccountDeclaration(category, checked(name, str))
    if kind == 'Amount':
        dollars, cents = args
        assert isinstance(dollars, int)
        assert isinstance(cents, int)
        if cents >= 0 and cents < 100: return Amount(dollars, cents)
        if cents > 100: return make('Amount', dollars+1, cents-100)
        if cents < 0: return make('Amount', dollars-1, cents+100)
    if kind == 'Balance':
        side, amount = args
        assert side in {'debit', 'credit'}
        return Balance(side, checked(amount, Amount))
    if kind == 'JournalEntry':
        date, amount, debit_account, credit_account, description = args
        return JournalEntry(
            checked(date, datetime.date),
            checked(amount, Amount),
            checked(debit_account, str),
            checked(credit_account, str),
            checked(description, str),
        )
    if kind == 'LedgerEntry':
        account, date, balance, description, source, location = args
        return LedgerEntry(
            checked(account, str),
            checked(date, datetime.date),
            checked(balance, Balance),
            checked(description, str),
            checked(source, str),
            checked(location, str),
        )

    raise NotImplementedError(f'make({kind}, {args})')


# Return val cast according to kind
# For Q's definition, see https://code.kx.com/q/ref/cast/
def cast(kind, val):
    if kind == 'Amount' and isinstance(val, str):
        dollars, _, cents = val.partition('.')
        return make(
            'Amount',
            0 if dollars == '' else int(dollars),
            0 if cents == '' else int(cents)
        )
    if kind == 'AccountDeclaration' and isinstance(val, str):
        error_msg = 'Account Declaration was not like: Asset Accounts Receivable'
        splits = u.split_and_strip(val)
        if len(splits) < 2: raise InputError(error_msg)
        try:
            return make('AccountDeclaration', splits[0], ' '.join(splits[1:]))
        except AssertionError:
            raise InputError(error_msg)
    if kind == 'JournalEntry' and isinstance(val, str):
        error_msg = 'Journal Entry was not like: date, amount, debit_account, credit_account, description'
        splits = u.split_and_strip(val)
        if len(splits) != 5: raise InputError(error_msg)
        try:
            return make('JournalEntry', cast('datetime.date', splits[0]), cast('Amount', splits[1]), splits[2], splits[3], splits[4])
        except AssertionError:
            raise InputError(error_msg)
    if kind == 'datetime.date' and isinstance(val, str):
        return datetime.date.fromisoformat(val)
    if kind == 'str' and isinstance(val, Amount): 
        return f'{val.dollars}.{str(val.cents).zfill(2)}'
    if kind == 'str' and isinstance(val, datetime.date):
        return f'{val.year}{str(val.month).zfill(2)}{str(val.day).zfill(2)}'
    raise NotImplementedError(f'cast({kind}: {val})')

# Return x combined with y
# For Q's definition, see https://code.kx.com/q/ref/join/
def join(x, y):
    print(f'join({x}: {type(x)}, {y}: {type(y)})')
    if isinstance(x, list) and isinstance(y, list):
        r= copy.deepcopy(x)
        r.extend(y)
    if isinstance(x, list):
        r = copy.deepcopy(x)
        r.append(y)
        return r
    if isinstance(x, tuple): return join(list(x), y)
    raise NotImplementedError(f'join({type(x)}, {type(y)})')







