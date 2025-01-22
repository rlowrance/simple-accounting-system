# run accounting for all of Roy's accounts
python3 ledgers.py roy-accounts.csv roy-*.csv >_roy.ledgers.csv
python3 balances.py _roy.ledgers.csv
