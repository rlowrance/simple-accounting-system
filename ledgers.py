# pipeline a csv file with journal entries to a csv file with ledger entries
from typing import List, Union

import collections
import copy
import csv
import datetime
import fileinput
import os
import sys

from sac import AccountDeclaration, Amount, JournalEntry, InputError, LedgerEntry
import sac
import utility as u

State = collections.namedtuple('State', 'category_for_account ledger_entries_for_account previous_journal_entry line source location')

# Return y views as the type of x
def cast(x, y):
    return sac.cast(x, y)

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

def join(x, y):
    print('join', type(x), y, type(y))
    if isinstance(x, State) and isinstance(y, AccountDeclaration):
        return join_state_account_declaration(x, y)
    if isinstance(x, State) and isinstance(y, JournalEntry):
        return join_state_journal_entry(x, y)
    if isinstance(x, State) and isinstance(y, str):
        return join_state_str(x, y)
    if isinstance(x, State) and isinstance(y, str): return join_state_str(x, y)
    return sac.join(x, y)
    
def join_state_str(state: State, y: str) -> State:
    #breakpoint()
    print('join_state_str', str)
    if len(y) == 0: return state
    if y.startswith('#'): return state
    front, _, _ = y.partition('#')
    for row1 in csv.reader([front]):  # parse as a line in a CSV file
        row = list(map(str.strip, row1))  # remove any leading or trailing white space
        if len(row) == 1: return join_state_account_declaration_str(state, row[0])
        if len(row) > 5: raise InputError('line has more than five CSV columns')
        if len(row) <= 5: return join_state_journal_entry_str(state, row)
    return state  # silence a type-checking error

def join_state_account_declaration(state: State, ad: AccountDeclaration) -> State:
    assert isinstance(state, State)
    assert isinstance(ad, AccountDeclaration)
    category, account = ad
    existing_category = state.category_for_account.get(account, None)
    if existing_category is None:
        new_state = copy.deepcopy(state)
        new_state.category_for_account[account] = category
        return new_state
    if category == state.category_for_account[account]: 
        return state
    raise InputError(f'attempt to redefine category for account {account} from {existing_category} to {category}')

def join_state_account_declaration_str(state: State, line: str) -> State:
    print('join_state_account_declaration', line)
    assert isinstance(state, State)
    assert isinstance(line, str)
    ad = cast('AccountDeclaration', line)
    assert isinstance(ad, AccountDeclaration)
    return join_state_account_declaration(state, ad)

def join_state_journal_entry(state: State, je: JournalEntry) -> State:
    assert isinstance(state, State)
    assert isinstance(je, JournalEntry)
    def ledger_entry(side: str, account: str) -> LedgerEntry:
        return sac.make('LedgerEntry', account, je.date, sac.make('Balance', side, je.amount), je.description, state.source, state.location)
    new_ledgers = copy.deepcopy(state.ledger_entries_for_account)
    new_ledgers[je.debit_account].append(ledger_entry('debit', je.debit_account))
    new_ledgers[je.credit_account].append(ledger_entry('credit', je.credit_account))
    return state._replace(
        ledger_entries_for_account=new_ledgers,
        previous_journal_entry=je)

def join_state_journal_entry_str(state: State, items: List[str]) -> State:
    print('join_state_journal_entry', items)
    assert len(items) > 1
    if len(items) == 5:
        date, amount, debit_account, credit_account, description = items
        pje = state.previous_journal_entry
        if len(date) != 8 and pje is None: raise InputError('missing complete date in form YYYYMMDD')
        if len(date) != 8:
            previous_date = cast('str', pje.date)
            if len(date) == 0: date = previous_date
            elif len(date) == 1: date = previous_date[0:6] + date.zfill(2)
            elif len(date) == 2: date = previous_date[0:6] + date
            elif len(date) == 4: date = previous_date[0:4] + date
            else: raise InputError('abbreviated date not of length 1, 2, or 4')
        if len(amount) == 0 and pje is None: raise InputError('missing amount')
        if len(amount) == 0: amount = cast('str', pje.amount)
        if len(debit_account) == 0 and pje is None: raise InputError('missing debit account')
        if len(debit_account) == 0: debit_account = pje.debit_account
        if len(credit_account) == 0 and pje is None: raise InputError('missing credit account')
        if len(credit_account) == 0: credit_account = pje.credit_account
        if len(description) == 0 and pje is not None and len(pje.description) > 0: description = pje.description

        if debit_account not in state.category_for_account: raise InputError(f'account {debit_account} not previously declared')
        if credit_account not in state.category_for_account: raise InputError(f'account {credit_account} not previously declared')
        new_je = sac.make(
            'JournalEntry', 
            cast('datetime.date', date),
            cast('Amount',  amount), 
            debit_account, 
            credit_account, 
            description)
        assert isinstance(new_je, JournalEntry)
        return join(state, new_je)

    else:
        return join_state_journal_entry_str(state, join(items, ''))

def join_state_journal_entry_abbreviated(state: State, items: List[str]) -> State:
    assert isinstance(state, State)
    assert len(items) == 2
    new_items = copy.deepcopy(items)
    new_items.append(state.previous_journal_entry.debit_account)
    new_items.append(state.previous_journal_entry.credit_account)
    new_items.append(state.previous_journal_entry.description)
    return join_state_journal_entry_str(state, new_items)

# write ledgers to stdout formated as a CSV file
def produce_output(state: State) -> None:
    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('category', 'account', 'date', 'side', 'amount', 'description', 'line'))
    accounts_for_category = u.invert_dict(state.category_for_account)
    for category in ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense'):
        accounts = accounts_for_category[category]
        for account in sorted(accounts, key=lambda account: account.split()):
            for ledger_entry in sorted(state.ledger_entries_for_account[account], key=lambda ledger_entry: ledger_entry.date):
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

# join line to state, raising any InputError
def process_line(state: State, line: str) -> State:
    try:
        return join(state, line)
    except InputError as e:
        e.add_note(f'in line: {line}')
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
                    stripped = line.strip()
                    state = state._replace(line=stripped, location=f'{i+1}')
                    state = process_line(state, stripped)
    else:  # read from standard in
        state = state._replace(source='(stdin)')
        for i, line in enumerate(fileinput.input()):
            stripped = line.strip()
            state = state._replace(line=stripped, location=f'{i+1}')
            state = process_line(state, stripped)
    assert isinstance(state, State)
    produce_output(state)

if __name__ == '__main__':
    main()
