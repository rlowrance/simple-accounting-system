import collections
import datetime

AccountDeclaration = collections.namedtuple('AccountDeclaration', 'category name')
Amount = collections.namedtuple('Amount', 'dollars cents')
Balance = collections.namedtuple('Balance', 'side amount')
JournalEntry = collections.namedtuple('JournalEntry', 'date amount debit_account credit_account description')
LedgerEntry = collections.namedtuple('LedgerEntry', 'account date balance description source location')

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