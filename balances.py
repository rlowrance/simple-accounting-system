# pipeline a csv file with journal entries to a csv file with ledger entries
from typing import Any, List, Union

import collections
import copy
import csv
import datetime
import fileinput
import os
import sys


from sac import AccountDeclaration, Amount, Balance, JournalEntry, InputError, LedgerEntry

import sac
import utility as u

State = collections.namedtuple('State', 'balance_for_account category_for_account line source location')
def empty_state(): return State({}, {}, None, None, None)

verbose = True
def vp(*args, **kwargs):
    if True: print(*args, **kwargs)

def add(x, y): return sac.add(x, y)
def cast(x, y): return sac.cast(x, y)
def greater(x, y): return sac.greater(x, y)
def join(x, y) -> Any: 
    vp('join', x, y)
    if isinstance(x, State) and isinstance(y, LedgerEntry): return join_state_ledger_entry(x, y)
    if isinstance(x, State) and isinstance(y, str): return join_state_str(x, y)
    return sac.join(x, y)
def make(x, *args): return sac.make(x, *args)
def subtract(x, y): return sac.subtract(x, y)

def join_state_str(state: State, line: str) -> State:
    assert isinstance(state, State)
    assert isinstance(line, str)
    ledger_entry = cast('LedgerEntry', line)
    return join(state, ledger_entry)

def join_state_ledger_entry(state: State, le: LedgerEntry) -> State:
    vp('join_state_leger_entry', le)
    assert isinstance(state, State)
    assert isinstance(le, LedgerEntry)

    category, account, _, balance, _, _, _ = le
    if account not in state.balance_for_account:
        new_balance_for_account = copy.deepcopy(state.balance_for_account)
        new_balance_for_account[account] = make('Balance', 'debit', make('Amount', 0, 0))
        return join_state_ledger_entry(state._replace(balance_for_account=new_balance_for_account), le)
    new_balance_for_account = copy.deepcopy(state.balance_for_account)
    new_balance_for_account[account] = add(state.balance_for_account[account], balance)

    new_category_for_account = copy.deepcopy(state.category_for_account)
    new_category_for_account[account] = category
    
    return state._replace(balance_for_account=new_balance_for_account,
                          category_for_account=new_category_for_account,
    )

# write ledgers to stdout formated as a CSV file
def produce_output(state: State) -> None:
    breakpoint()
    # to-do: rewrite me
    writer = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(('category', 'account', 'side', 'amount'))
    accounts_for_category = u.invert_dict(state.category_for_account)
    grand_total = make('Balance', 'debit', make('Amount', 0, 0))
    for category in ('Asset', 'Liability', 'Equity', 'Revenue', 'Expense'):
        total_for_category = make('Balance', 'debit', make('Amount', 0, 0))
        accounts = accounts_for_category[category]
        for account in sorted(accounts, key=lambda account: account.split()):
            balance = state.balance_for_account[account]
            writer.writerow((category, account, balance.side, cast('str', balance.amount)))
            total_for_category = add(total_for_category, balance)
            grand_total = add(grand_total, balance)

        writer.writerow((category, '**TOTAL FOR CATEGORY**', total_for_category.side, cast('str', total_for_category.amount)))
    writer.writerow(('**TOTAL ACROSS CATEGORIES**', '', grand_total.side, cast('str', grand_total.amount)))

# Update state with line, possibly raising any InputError
def process_line(state: State, line: str, filename: str, line_number: int) -> State:
    vp('process_line', line)
    # breakpoint()
    stripped_line = line.strip()
    try:
        state = join(
            state._replace(line=stripped_line, location=f'{line_number+1}'),
            stripped_line
            )
        return state
    except InputError as e:
        e.add_note(f'in line: {line}')
        e.add_note(f'in file {state.source} line number {state.location}')
        raise

def main():
    # breakpoint()
    state = empty_state()
    assert isinstance(state, State)
    if len(sys.argv) > 1:  # process files on the command line
        for filename in sys.argv[1:]:
            state = state._replace(source=filename)
            with open(filename, 'r') as f:
                for i, line in enumerate(f):
                    if i == 0: continue  # skip the header line
                    state = process_line(state, line, filename, i)
    else:  # read from standard in
        state = state._replace(source='(stdin)')
        for i, line in enumerate(fileinput.input()):
            if i == 0: continue  # skip the header line
            state = process_line(state, line, '(stdin)', i)
    assert isinstance(state, State)
    produce_output(state)

if __name__ == '__main__':
    main()
