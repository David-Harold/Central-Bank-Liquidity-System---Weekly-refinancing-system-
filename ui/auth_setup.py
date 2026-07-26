#!/usr/bin/python3

import bcrypt

import database.db as db


def _prompt_int(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number.")


def _prompt_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a number.")


def _prompt_yes_no(prompt):
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please answer y or n.")



#Central Bank creation

def central_bank_exists():
    row = db.fetch_one("SELECT central_bank_id FROM central_bank LIMIT 1")
    return row is not None


def create_central_bank():
    print("\n===== CREATE CENTRAL BANK =====\n")
    cb_id = input(">>> Enter your ID: ").strip()
    pwd = input(">>> Enter your password: ")
    pwd_hash = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt(10)).decode("utf-8")

    ok = db.execute_query(
        "INSERT INTO central_bank (central_bank_id, password_hash) VALUES (%s, %s)",
        (cb_id, pwd_hash),
    )
    if ok:
        print("Central bank successfully created!\n")
    else:
        print("Could not create central bank. Please try again.\n")
    return bool(ok)



# Login


def login():
    """Loops until a successful login, then returns a viewer dict."""
    print("\n===== LOGIN =====\n")
    while True:
        login_id = input(">>> Enter your ID or Bank name: ").strip()
        pwd = input(">>> Enter your password: ").encode("utf-8")

        central_bank = db.fetch_one(
            "SELECT * FROM central_bank WHERE central_bank_id = %s", (login_id,)
        )
        commercial_bank = db.fetch_one(
            "SELECT * FROM commercial_banks WHERE bank_name = %s", (login_id,)
        )

        if central_bank:
            if bcrypt.checkpw(pwd, central_bank["password_hash"].encode("utf-8")):
                print("\nSuccessfully logged in as Central Bank.")
                return {"role": "central_bank", "central_bank_id": central_bank["central_bank_id"]}
            print("Incorrect password. Try again!\n")
        elif commercial_bank:
            if bcrypt.checkpw(pwd, commercial_bank["password_hash"].encode("utf-8")):
                print(f"\nSuccessfully logged in as {commercial_bank['bank_name']}.")
                return {
                    "role": "bank",
                    "bank_id": commercial_bank["bank_id"],
                    "bank_name": commercial_bank["bank_name"],
                }
            print("Incorrect password. Try again!\n")
        else:
            print("No bank found with those credentials.\n")



# Task 4.4 screens: create bank / eligibility / collateral types / borrowing_limits


def screen_create_commercial_bank():
    print("\n==== CREATE COMMERCIAL BANK ====\n")
    bank_name = input(">>> Enter bank name: ").strip()
    password = input(">>> Enter bank initial password: ").encode("utf-8")
    borrowing_limit = _prompt_float(">>> Enter borrowing limit: ")
    pwd_hash = bcrypt.hashpw(password, bcrypt.gensalt(10)).decode("utf-8")

    # Per the business rules a new bank always starts as NOT eligible
    # ("none") until the Central Bank explicitly approves it later via the
    # "Set/update bank eligibility" screen - it is never set at creation.
    ok = db.execute_query(
        "INSERT INTO commercial_banks (bank_name, password_hash, eligibility, borrowing_limit) "
        "VALUES (%s, %s, %s, %s)",
        (bank_name, pwd_hash, "none", borrowing_limit),
    )
    if ok:
        print(f"\nCommercial bank '{bank_name}' created (eligibility: none).")
    else:
        print("\nCommercial bank creation failed!")


def screen_set_bank_eligibility():
    banks = db.fetch_all("SELECT bank_id, bank_name, eligibility FROM commercial_banks ORDER BY bank_id")
    if not banks:
        print("\nNo banks exist yet.")
        return
    print("\nBanks:")
    for b in banks:
        print(f"  #{b['bank_id']}  {b['bank_name']}  eligibility={b['eligibility']}")
    bank_id = _prompt_int(">>> Enter bank ID to update: ")
    eligible = _prompt_yes_no(">>> Mark this bank eligible? [y/n]: ")
    ok = db.execute_query(
        "UPDATE commercial_banks SET eligibility = %s WHERE bank_id = %s",
        ("eligible" if eligible else "none", bank_id),
    )
    print("Eligibility updated." if ok else "Update failed - check the bank ID.")


def screen_define_collateral_type():
    print("\n==== DEFINE ADMISSIBLE COLLATERAL TYPE ====\n")
    type_name = input(">>> Collateral type name: ").strip()
    haircut = _prompt_float(">>> Haircut percentage (e.g. 10 for 10%): ")
    ok = db.execute_query(
        "INSERT INTO collateral_types (type_name, haircut_percentage) VALUES (%s, %s)",
        (type_name, haircut),
    )
    print(f"'{type_name}' added as admissible (haircut {haircut}%)." if ok else "Could not add type.")


def screen_set_borrowing_limit():
    banks = db.fetch_all("SELECT bank_id, bank_name, borrowing_limit FROM commercial_banks ORDER BY bank_id")
    if not banks:
        print("\nNo banks exist yet.")
        return
    print("\nBanks:")
    for b in banks:
        print(f"  #{b['bank_id']}  {b['bank_name']}  limit={b['borrowing_limit']}")
    bank_id = _prompt_int(">>> Enter bank ID to update: ")
    limit = _prompt_float(">>> New borrowing limit: ")
    ok = db.execute_query(
        "UPDATE commercial_banks SET borrowing_limit = %s WHERE bank_id = %s",
        (limit, bank_id),
    )
    print("Borrowing limit updated." if ok else "Update failed - check the bank ID.")


def screen_change_password(bank_id):
    new_pwd = input(">>> Enter your new password: ").encode("utf-8")
    pwd_hash = bcrypt.hashpw(new_pwd, bcrypt.gensalt(10)).decode("utf-8")
    ok = db.execute_query(
        "UPDATE commercial_banks SET password_hash = %s WHERE bank_id = %s",
        (pwd_hash, bank_id),
    )
    print("Password updated." if ok else "Could not update password.")