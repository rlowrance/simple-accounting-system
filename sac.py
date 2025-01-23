import collections
import copy
import datetime

from typing import List

import utility as u

AccountDeclaration = collections.namedtuple('AccountDeclaration', 'category name')
Amount = collections.namedtuple('Amount', 'dollars cents')
Balance = collections.namedtuple('Balance', 'side amount')
JournalEntry = collections.namedtuple('JournalEntry', 'date amount debit_account credit_account description')
LedgerEntry = collections.namedtuple('LedgerEntry', 'category account date balance description source location')


class InputError(Exception):
    def __init__(self, msg): self.msg = msg
    def __str__(self): return f'{self.msg}'


# Return type-checked value x
def checked(x, kind):
    assert isinstance(x, kind)
    return x

# add x + y
def add(x, y):
    if isinstance(x, Amount) and isinstance(y, Amount):
        return make('Amount', x.dollars+y.dollars, x.cents+y.cents)
    if isinstance(x, Balance) and isinstance(y, Balance):
        if x.side == y.side: return make('Balance', x.side, add(x.amount, y.amount))
        if greater(x.amount, y.amount): return make('Balance', x.side, subtract(x.amount, y.amount))
        if greater(y.amount, x.amount): return make('Balance', y.side, subtract(y.amount, x.amount))
        return make('Balance', x.side, make('Amount', 0, 0))
    raise NotImplementedError(f'add({type(x)}, {type(y)}')

# Is x > y?
def greater(x, y) -> bool:
    if isinstance(x, Amount) and isinstance(y, Amount):
        if x.dollars > y.dollars: return True
        if x.dollars == y.dollars and x.cents > y.cents: return True
        return False
    raise NotImplementedError(f'greater({type(x)}, {type(y)})')


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
        category, account, date, balance, description, source, location = args
        return LedgerEntry(
            checked(category, str),
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
def cast(kind, value):
    if kind == 'Amount' and isinstance(value, str):
        dollars, _, cents = value.partition('.')
        return make(
            'Amount',
            0 if dollars == '' else int(dollars),
            0 if cents == '' else int(cents)
        )
    if kind == 'AccountDeclaration' and isinstance(value, str):
        error_msg = 'Account Declaration was not like: Asset Accounts Receivable'
        splits = u.split_and_strip(value)
        if len(splits) < 2: raise InputError(error_msg)
        try:
            return make('AccountDeclaration', splits[0], ' '.join(splits[1:]))
        except AssertionError:
            raise InputError(error_msg)
    if kind == 'JournalEntry' and isinstance(value, str):
        error_msg = 'Journal Entry was not like: date, amount, debit_account, credit_account, description'
        items = u._cast_liststr_csvline(value)
        if len(items) != 5: raise InputError(error_msg)
        try:
            date, amount, debit_account, credit_account, description = items
            return make('JournalEntry', cast('datetime.date', date), cast('Amount', amount), debit_account, credit_account, description)
        except AssertionError:
            raise InputError(error_msg)
    if kind == 'LedgerEntry' and isinstance(value, str):
        items = u._cast_liststr_csvline(value)
        assert len(items) == 8  # don't return a nice error because the ledger file is created by an upstream program
        category, account, date, side, amount, description, line, location = items
        datetime_date = cast('datetime.date', date)
        balance = make('Balance', side, cast('Amount', amount))
        return make('LedgerEntry', category, account, datetime_date, balance, description, line, location)
    if kind == 'datetime.date' and isinstance(value, str):
        return datetime.date.fromisoformat(value)
    if kind == 'str' and isinstance(value, Amount): 
        return f'{value.dollars}.{str(value.cents).zfill(2)}'
    if kind == 'str' and isinstance(value, datetime.date):
        return f'{value.year}{str(value.month).zfill(2)}{str(value.day).zfill(2)}'
    raise NotImplementedError(f'cast({kind}: {value})')

# Return x combined with y
# For Q's definition, see https://code.kx.com/q/ref/join/
def join(x, y):
    if isinstance(x, list) and isinstance(y, list):
        r= copy.deepcopy(x)
        r.extend(y)
    if isinstance(x, list):
        r = copy.deepcopy(x)
        r.append(y)
        return r
    if isinstance(x, tuple): return join(list(x), y)
    raise NotImplementedError(f'join({type(x)}, {type(y)})')


# Return x - y
def subtract(x, y):
    if isinstance(x, Amount) and isinstance(y, Amount): return make('Amount', x.dollars-y.dollars, x.cents-y.cents)
    raise NotImplementedError(f'subtract({type(x)}, {type(y)}')




