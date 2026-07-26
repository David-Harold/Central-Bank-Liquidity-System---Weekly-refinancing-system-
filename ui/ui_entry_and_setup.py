#!/usr/bin/python3

import database.db as db

from ui import auth_setup
from ui import inventory
from ui import loan_request
from ui import status
from ui import requests as requests_ui
from ui import opclose
from ui import settle
from ui import reports
from ui import browse


# Small input helpers 

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




def _get_open_operation_id():
    row = db.fetch_one("SELECT operation_id FROM weekly_operations WHERE LOWER(status) = 'open'")
    return row["operation_id"] if row else None



# Central Bank menu


def _cb_open_operation():
    if _get_open_operation_id() is not None:
        print("An operation is already open. Close it before opening a new one.")
        return
    rate_pct = _prompt_float(">>> Enter the policy rate as a percentage (e.g. 5 for 5%): ")
    rate = rate_pct / 100
    opclose.screen_open_operation(rate)


def _cb_close_operation():
    operation_id = _get_open_operation_id()
    if operation_id is None:
        print("There is no open operation to close.")
        return
    opclose.screen_close_operation(operation_id)


def _cb_review_pending_requests():
    pending = requests_ui.get_pending_requests()
    if not pending:
        print("\nNo pending requests.")
        return
    print("\nPending requests:")
    for r in pending:
        print(f"  #{r['request_id']}  bank_id={r['bank_id']}  amount={r['requested_amount']}")
    request_id = _prompt_int(">>> Enter request ID to review: ")
    requests_ui.screen_review_pending_request(request_id)


def _cb_settle_request(viewer):
    pending_settlement = settle.screen_settle_request(viewer)
    if not pending_settlement:
        return
    request_id = _prompt_int(">>> Enter request ID to settle: ")
    settle.settle_selected_request(request_id)


def _browse_past_operations(viewer):
    ops = browse.screen_browse_past_operations(viewer)
    if not ops:
        return
    operation_id = _prompt_int(">>> Enter operation ID for detail (blank to skip): ", allow_blank=True)
    if operation_id is not None:
        browse.screen_operation_detail(operation_id, viewer)


CENTRAL_BANK_MENU_TEXT = """
==== CENTRAL BANK MENU ====

1. Create a new bank
2. Set/update bank eligibility
3. Define admissible collateral type & haircut
4. Set/update bank borrowing limit
5. Open a new weekly operation
6. Close current weekly operation
7. Review pending requests
8. Settle an approved request
9. View reports
10. View past weekly operations (read-only)
11. Log out
"""


def central_bank_menu_loop(viewer):
    handlers = {
        1: lambda: auth_setup.screen_create_commercial_bank(),
        2: lambda: auth_setup.screen_set_bank_eligibility(),
        3: lambda: auth_setup.screen_define_collateral_type(),
        4: lambda: auth_setup.screen_set_borrowing_limit(),
        5: lambda: _cb_open_operation(),
        6: lambda: _cb_close_operation(),
        7: lambda: _cb_review_pending_requests(),
        8: lambda: _cb_settle_request(viewer),
        9: lambda: reports.screen_reports(viewer),
        10: lambda: _browse_past_operations(viewer),
    }
    while True:
        print(CENTRAL_BANK_MENU_TEXT)
        choice = _prompt_int(">>> ")
        if choice == 11:
            print("Logging out.\n")
            return
        handler = handlers.get(choice)
        if handler is None:
            print("Invalid input. Try again.")
            continue
        try:
            handler()
        except Exception as e:
            print(f"Something went wrong: {e}")



# Bank menu


def _bank_manage_inventory(bank_id):
    print("""
1. View admissible collateral types
2. View my inventory
3. Add collateral to my inventory
""")
    sub = _prompt_int(">>> ")
    if sub == 1:
        inventory.screen_view_admissible_types()
    elif sub == 2:
        inventory.screen_view_inventory(bank_id)
    elif sub == 3:
        inventory.screen_view_admissible_types()
        collateral_type_id = _prompt_int(">>> Enter collateral type ID: ")
        declared_value = input(">>> Enter declared value: ").strip()
        inventory.screen_add_collateral(bank_id, collateral_type_id, declared_value)
    else:
        print("Invalid input.")


def _bank_check_status(bank_id):
    requests_list = status.screen_list_my_requests(bank_id)
    if not requests_list:
        return
    request_id = _prompt_int(">>> Enter request ID for detail (blank to skip): ", allow_blank=True)
    if request_id is not None:
        status.screen_check_status(bank_id, request_id)


BANK_MENU_TEXT = """
==== BANK MENU ====

1. Change password
2. Manage collateral inventory
3. Submit a loan request
4. Check status of my request
5. View my reports
6. View my past weekly operations (read-only)
7. Log out
"""


def bank_menu_loop(viewer):
    bank_id = viewer["bank_id"]
    handlers = {
        1: lambda: auth_setup.screen_change_password(bank_id),
        2: lambda: _bank_manage_inventory(bank_id),
        3: lambda: loan_request.loan_request_screen(bank_id),
        4: lambda: _bank_check_status(bank_id),
        5: lambda: reports.screen_reports(viewer),
        6: lambda: _browse_past_operations(viewer),
    }
    while True:
        print(BANK_MENU_TEXT)
        choice = _prompt_int(">>> ")
        if choice == 7:
            print("Logging out.\n")
            return
        handler = handlers.get(choice)
        if handler is None:
            print("Invalid input. Try again.")
            continue
        try:
            handler()
        except Exception as e:
            print(f"Something went wrong: {e}")



def start_application():
    print("=" * 60)
    print(" CENTRAL BANK LIQUIDITY & WEEKLY REFINANCING SYSTEM")
    print("=" * 60)

    while True:
        if not auth_setup.central_bank_exists():
            auth_setup.create_central_bank()
            continue  

        viewer = auth_setup.login()
        if viewer["role"] == "central_bank":
            central_bank_menu_loop(viewer)
        else:
            bank_menu_loop(viewer)
        