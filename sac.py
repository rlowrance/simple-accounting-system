# simply accounting system (version 2)
# Read a directory of text files containing account declarations and journal entries. Skip certain files including those whose name start with "_".
# Write a directory named _{datetime}-summary containing CSV files that balances, ledgers, an income statement, and a balance sheet.
from typing import Any, Dict, List, Self, Set, Union

import collections
import copy
import csv
import dataclasses
from dataclasses import dataclass
import datetime
import io
import os
import unittest

from accountdeclaration import AccountDeclaration, allowed_account_categories
from accountingsystem import AccountingSystem
from journalentry import JournalEntry
from ledgerentry import LedgerEntry
from line import Line
from alignedcsv import AlignedCSV

import parse
import utility as u

# Yield category, name in canonical order
def yield_categories_nanes(accounting_system: AccountingSystem):
    map = u.invert_dict(accounting_system.category_for)
    for account_category in allowed_account_categories:
        if account_category in map:
            for account_name in map[account_category]:
                yield account_category, account_name

def write_csv_from_AlignedCSV(path: str, aligned_csv: AlignedCSV) -> None:
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        for line in aligned_csv.cast('tuple(tuple)'):
            writer.writerow(line)

def write_summary_accounts(path: str, accounting_system: AccountingSystem) -> None:
    r = AlignedCSV(alignments=('left', 'left')).join(('account category', 'account name'))
    for account_category, account_name in yield_categories_nanes(accounting_system):
        r = r.join((account_category, account_name))
    write_csv_from_AlignedCSV(path, r)

def write_summary_balances(path: str, accounting_system: AccountingSystem) -> None:
    r = AlignedCSV(alignments=('left', 'left', 'right', 'right'))
    r = r.join(('account category', 'account name', 'debit balance', 'credit balance'))
    for account_category, account_name in yield_categories_nanes(accounting_system):
        ledger_entry = accounting_system.balances[account_name]
        amount = f'{ledger_entry.amount}'
        if ledger_entry.side == 'debit':
            r = r.join((account_category, account_name, amount, ''))
        else:
            r = r.join((account_category, account_name, '', amount))
    write_csv_from_AlignedCSV(path, r)

def write_summary_counts(path: str, counts:collections.Counter) -> None:
    r = AlignedCSV(alignments=('left', 'right'))
    r = r.join(('line type', 'count'))
    for line_type in sorted(counts.keys()):
        r = r.join((line_type, counts[line_type]))
    write_csv_from_AlignedCSV(path, r)

def write_summary_ledger(path: str, ledger_entries: List[LedgerEntry]) -> None:
    r = AlignedCSV(alignments=('left', 'right', 'right', 'left', 'left', 'left'))
    r = r.join(('date', 'debit', 'credit', 'description', 'source', 'source_location'))
    for ledger_entry in ledger_entries:
        date = f'{ledger_entry.date}'
        amount = f'{ledger_entry.amount}'
        side = ledger_entry.side
        description = ledger_entry.description
        source = ledger_entry.source
        source_location = ledger_entry.source_location
        if side == 'debit':
            r = r.join((date, amount, '', description, source, source_location))
        else:
            r = r.join((date, '', amount, description, source, source_location))
    write_csv_from_AlignedCSV(path, r)

def write_summary_ledgers(directory: str, filename: str, accounting_system: AccountingSystem) -> None:
    for category, name in yield_categories_nanes(accounting_system):
        path = os.path.join(directory, f'_{filename}-ledger-{category}-{name}.csv')
        write_summary_ledger(path, accounting_system.ledgers[name])


# Process a file, producing these summary files
#  _{filename}-accounts.csv
#  _{filename}-counts.csv
#  _{filename}-balances.csv
#  _{filename}-ledgers.csv
def process_file(directory: str, filename: str, accounting_system: AccountingSystem) -> AccountingSystem:
    def skip(line: str) -> bool:
        line = line.strip()
        if line.startswith('#'): return True
        if line.isspace(): return True
        if len(line) == 0: return True
        return False
    file_accounting_system = AccountingSystem.empty()
    counts = collections.Counter()
    print(f'processing file {filename}')
    path = os.path.join(directory, filename)
    last_journal_entry = None
    with open(path, 'r') as file:
        contents = file.read()
        for line_index, line in enumerate(contents.split('\n')):
            print(f'  {line}')
            counts['lines read'] += 1
            line = line.strip()
            if skip(line): continue
            counts['lines processed'] += 1
            command = parse.parse(
                line=Line(line, source=filename, source_location=f'line {line_index+1}'),
                last_journal_entry=last_journal_entry
            )
            file_accounting_system = file_accounting_system.join(command)
            accounting_system = accounting_system.join(command)
            if isinstance(command, AccountDeclaration): counts['account declarations'] += 1
            if isinstance(command, JournalEntry): counts['journal entries'] += 1
            if isinstance(command, JournalEntry): last_journal_entry = command
        # write the summaries
        def make_path(topic: str) -> str: return os.path.join(directory, f'_{filename}-{topic}.csv')
        write_summary_counts(make_path('counts'), counts=counts)
        write_summary_accounts(make_path('accounts'), accounting_system=file_accounting_system)
        write_summary_balances(make_path('balances'), accounting_system=file_accounting_system)
        write_summary_ledgers(directory=directory, filename=filename, accounting_system=file_accounting_system)
        return accounting_system
    
# process files in a directory
def process_files(directory='.') -> None:
    r = AccountingSystem.empty()
    for objname in os.listdir(directory):
        if objname.startswith('.') or objname.startswith('_') or objname.endswith('.py'):
            print(f'skipping {objname}')
            continue
        if not (objname.endswith('.txt') or objname.endswith('.csv')):
            print('skipping {objname}')
            continue
        path = os.path.join(directory, objname)
        if not os.path.isfile(path):
            print('skipping directory {filename}')
        r = process_file(directory=directory, filename=objname, accounting_system=r)
    write_summary_accounts(os.path.join(directory, f'_summary-accounts.csv'), r)
    write_summary_balances(os.path.join(directory, f'_summary-balances.csv'), r)
    for category, name in yield_categories_nanes(r):
        write_summary_ledger(os.path.join(directory, f'_summary-ledger-{category}-{name}'), r.ledgers[name])
    return

def main():
    directory = '.'
    process_files(directory)

if __name__ == '__main__':
    main()






