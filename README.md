# Central Bank Liquidity System — Weekly Refinancing System

A Python program, backed by a MySQL database, simulating a weekly central bank liquidity operation. The Central Bank sets the rules (eligibility, collateral types, borrowing limits), opens a weekly operation, and reviews loan requests from Commercial Banks, which pledge collateral against the loans they request.

## Contributors

| Name | GitHub |
|---|---|
| David-Harold E. Koffi-Essiben | @David-Harold |
| Cynthia Umwali | @cynthiaumwali |
| Isimbi Nina Henriette | @Isimbi-Nina |
| Aubin Karaha | @aubin-karaha |
| Shyaka Carrick Ngago | @shyakanga |
| Chlomi Justifie Gutabarwa | @xCHLOMIx |

## Project structure

Central-Bank-Liquidity-System
│
├── database/
│   ├── db_schema.sql   ──> creates all 9 tables
│   └── db.py           ──> shared MySQL connection module
│
├── validation/         ──> the 4 loan checks + orchestrator
│
├── allocation/         ──> approve, reject, interest, settlement
│
├── ui/                 ──> Central Bank & Commercial Bank menu screens
│
└── main.py             ──> program entry point, run this to start


## How to run it

1. Install dependencies:

pip install mysql-connector-python bcrypt


2. Create the database and load the schema:

mysql -u root -p < database/db_schema.sql


3. Check `database/db.py` matches your local MySQL host, user, and password.

4. Start the program:

python3 main.py


## What it does

- **First run:** you're prompted to create the Central Bank account.
- **After that:** anyone logs in and is routed to either the Central Bank menu or a Commercial Bank menu, based on their ID.
- **Central Bank:** creates banks, sets eligibility and borrowing limits, defines admissible collateral types, opens/closes weekly operations, reviews and decides on loan requests, and settles approved loans.
- **Commercial Bank:** manages its own collateral inventory, submits one loan request per open operation, checks its request status, and views its own reports.
- Every request runs through 4 checks — eligibility, collateral admissibility, collateral value after haircut, borrowing limit — before the Central Bank approves or rejects it.
- Approved loans settle 7 days later, with interest calculated automatically.
