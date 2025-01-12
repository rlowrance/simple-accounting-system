# simply accounting system (version 2)
# Read a directory of text files containing account declarations and journal entries. Skip certain files including those whose name start with "_".
# Write a directory named _{datetime}-summary containing CSV files that balances, ledgers, an income statement, and a balance sheet.
import copy
import csv
import dataclasses
from dataclasses import dataclass
import datetime
import io
from typing import Dict, List, Self, Union
import os
import unittest

from accountdeclaration import AccountDeclaration
from accountingsystem import AccountingSystem
from amount import Amount
from columnsreport import ColumnsReport
from filereport import FileReport
from journalentry import JournalEntry
from line import Line
from reportcolumn import ReportColumn







# process files in a directory
def make_accounting_system(directory='.') -> AccountingSystem:
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
        
        print(f'reading file {objname}')
        with open(path, 'r') as file:
            content = file.read()
            last_journal_entry = None
            file_report = FileReport()
            for line_index, line in enumerate(content.split('\n')):
                print(line)
                line = line.strip()
                if line.startswith('#'): continue
                if len(line) == 0: continue
                if line.isspace(): continue
                command = parse(
                    line=Line(text=line, source=objname, source_location=f'line {line_index+1}'),
                    last_journal_entry=last_journal_entry
                )
                if isinstance(command, JournalEntry):
                    last_journal_entry = command
                r = r.join(command)
                fileReport = fileReport.join(command)
            for report_line in fileReport.render():
                print(line)
    return r

def make_reports(accounting_system: AccountingSystem) -> Dict[str, ColumnsReport]:
    r = {}
    r['balances'] = make_report_balances(accounting_system)
    return r

def account_name_for_sorting(s: str) -> List[str]:
    return split_and_strip(s)

# category account balance
def make_report_balances(accounting_system) -> ColumnsReport:
    category_column = []
    account_column = []
    balance_column = []
    for category in AccountDeclaration.allowed_account_categories():
        account_names_for_category = filter(lambda account_name: accounting_system.category_for[account_name] == category, accounting_system.balances.keys())
        sorted_account_name_for_category = sorted(account_names_for_category, key=account_name_for_sorting)
        for account_name in sorted_account_name_for_category:
            category_column.append(category)
            account_column.append(account_name)
            balance_column.append(accounting_system.balances[account_name])
    r = ColumnsReport()
    r = r.join(ReportColumn(alignment='left', items=category_column))
    r = r.join(ReportColumn(alignment='left', items=account_column))
    r = r.join(ReportColumn(alignment='right', items=balance_column))
    return r

def main():
    directory = '.'
    accounting_system = make_accounting_system(directory)
    for report_name, report in make_reports(accounting_system).items():
        print(f'report name: {report_name}')
        for report_line in report.render():
            print(f'  {report_line}')



if __name__ == '__main__':
    #unittest.main()
    main()






