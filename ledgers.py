# pipeline a csv file with journal entries to a csv file with ledger entries
from typing import List, Union

import collections
import copy
import csv
import datetime
import fileinput
import os
import sys

from sac_types import AccountDeclaration, Amount, JournalEntry, LedgerEntry, make
import utility as u

State = collections.namedtuple('State', 'category_for_account ledgers previous_journal_entry line source location')

class InputError(Exception):
    def __init__(self, msg): self.msg = msg
    def __str__(self): return f'{self.msg}'

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
    if kind == 'str' and isinstance(val, Amount): return f'{val.dollars}.{str(val.cents).zfill(2)}'
    raise NotImplementedError(f'{kind}: {val}')


def fill_date(x: str, y: Union[None, datetime.date]) -> datetime.date:
    assert isinstance(x, str)
    assert y is None or isinstance(y, datetime.date)
    if len(x) == 8:
        return datetime.date(int(x[0:4]), int(x[4:6]), int(x[6:8]))
    if len(x) == 4:
        if y is None: raise InputError(f'missing year in {x}')
        return datetime.date(y.year, int(x[0:2]), int(x[2:2]))
    if len(x) == 2 or len(x) == 1:
        if y is None: raise InputError(f'missing year and month in {x}')
        return datetime.date(y.year, y.month, int(x))
    if len(x) == 0:
        if y is None: raise InputError('missing date without a prior journal entry')
        return y
    raise InputError(f'{x} is not a date in the form YYYYMMDD')

# Return x combined with y
# For Q's definition, see https://code.kx.com/q/ref/join/
def join(x, y):
    if isinstance(x, State) and isinstance(y, str): return join_state_str(x, y)
    raise NotImplementedError(f'join({type(x)}, {type(y)})')

def join_state_str(state: State, y: str) -> State:
    stripped = y.strip()
    if len(stripped) == 0: return state
    if stripped.startswith('#'): return state
    front, _, _ = stripped.partition('#')
    for row in csv.reader([front]):  # parse as a line in a CSV file
        if len(row) == 1: return join_state_account_declaration(state, row[0])
        if len(row) == 5: return join_state_journal_entry(state, row)
        if len(row) == 2: return join_state_journal_entry_abbreviated(state, row)
        raise InputError('line is not an Account Declaration or a Journal Entry')
    return state  # silence a type-checking error

def join_state_account_declaration(state: State, line: str) -> State:
    assert isinstance(state, State)
    assert isinstance(line, str)
    ad = cast('AccountDeclaration', line)
    assert isinstance(ad, AccountDeclaration)
    category, name = ad
    existing_category = state.category_for_account.get(name, None)
    if existing_category is None:
        new_state = copy.deepcopy(state)
        new_state.category_for_account[name] = category
        return new_state
    if category == state.category_for_account[name]: 
        return state
    raise InputError(f'attempt to redefine category for account {name} from {existing_category} to {category}')

def join_state_journal_entry(state: State, items: List[str]) -> State:
    assert isinstance(state, State)
    assert len(items) == 5
    date, amount, debit_account, credit_account, description = list(map(str.strip, items))  # parse str values
    if debit_account not in state.category_for_account: raise InputError(f'account {debit_account} not previously declared')
    if credit_account not in state.category_for_account: raise InputError(f'acccount {credit_account} not previously declared')
    previous_date = None if state.previous_journal_entry is None else state.previous_journal_entry.date
    je = make('JournalEntry', fill_date(date, previous_date), cast('Amount', amount), debit_account, credit_account, description)
    assert isinstance(je, JournalEntry)
    new_ledgers = copy.deepcopy(state.ledgers)
    def ledger_entry(side, account): return make('LedgerEntry', account, je.date, make('Balance', side, je.amount), je.description, state.source, state.location)
    new_ledgers[je.debit_account].append(ledger_entry('debit', debit_account))
    new_ledgers[je.credit_account].append(ledger_entry('credit', credit_account))
    return state._replace(ledgers=new_ledgers, previous_journal_entry=je)

def join_state_journal_entry_abbreviated(state: State, items: List[str]) -> State:
    assert isinstance(state, State)
    assert len(items) == 2
    new_items = copy.deepcopy(items)
    new_items.append(state.previous_journal_entry.debit_account)
    new_items.append(state.previous_journal_entry.credit_account)
    new_items.append(state.previous_journal_entry.description)
    return join_state_journal_entry(state, new_items)

# write ledgers to stdout formated as a CSV file
def produce_output(state: State) -> None:
    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('category', 'account', 'date', 'side', 'amount', 'description', 'line'))
    accounts_for_category = u.invert_dict(state.category_for_account)
    for category in ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense'):
        accounts = accounts_for_category[category]
        for account in sorted(accounts, key=lambda account: account.split()):
            for ledger_entry in sorted(state.ledgers[account], key=lambda ledger_entry: ledger_entry.date):
                assert isinstance(ledger_entry, LedgerEntry)
                writer.writerow((
                    state.category_for_account[ledger_entry.account],
                    ledger_entry.account,
                    f'{str(ledger_entry.date.year)}{str(ledger_entry.date.month).zfill(2)}{str(ledger_entry.date.day).zfill(2)}',
                    ledger_entry.balance.side,
                    cast('str', ledger_entry.balance.amount),
                    ledger_entry.description,
                    ledger_entry.source,
                    ledger_entry.location,
                ))

# Update state with line, possibly raising any InputError
def process_line(state: State, line: str) -> State:
    try:
        state = join(state, line)
        return state
    except InputError as e:
        e.add_note(f'in line: {line.strip()}')
        e.add_note(f'in file {state.source} line number {state.location}')
        raise

def main():
    state = State({}, collections.defaultdict(list), None, None, None, None)
    assert isinstance(state, State)
    if len(sys.argv) > 1:  # process files on the command line
        # directory = '.'
        for filename in sys.argv[1:]:
            state = state._replace(source=filename, previous_journal_entry=None)
            # path = os.path.join(directory, filename)
            with open(filename, 'r') as f:
                for i, line in enumerate(f):
                    state = state._replace(line=line, location=f'{i+1}')
                    state = process_line(state, line)
    else:  # read from standard inx
        state = state._replace(source='(stdin)')
        for i, line in enumerate(fileinput.input()):
            state = state._replace(line=line, location=f'{i+1}')
            state = process_line(state, line)
    assert isinstance(state, State)
    produce_output(state)

if __name__ == '__main__':
    main()
