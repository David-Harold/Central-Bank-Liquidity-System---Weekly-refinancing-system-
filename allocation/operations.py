"""
Task 3.5 - Weekly operation state management.

Also defines AllocationError, the shared exception every Component 3 module
raises for invalid state transitions - imported from here by approval.py,
rejection.py, and settlement.py so a single `except AllocationError` catches
errors from any of them.

Depends on weekly_operations having a `policy_rate DECIMAL(6,4)` column in
addition to `start_date`/`end_date`/`status` - confirm this is added to the
schema before relying on it.
"""
import datetime

import database.db as db


class AllocationError(Exception):
    """Raised whenever a Component 3 rule is violated (invalid state
    transition, double settlement, operation already open, etc.)."""


def open_operation(rate):
    """Enforces 'only one weekly operation open at a time'. `rate` is a
    decimal fraction (e.g. 0.045 for 4.5%)."""
    open_op = db.fetch_one("SELECT * FROM weekly_operations WHERE status='open'")
    if open_op:
        raise AllocationError(
            f"Cannot open a new operation: operation {open_op['operation_id']} is already open."
        )

    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=7)
    op_id = db.execute_query(
        "INSERT INTO weekly_operations (policy_rate, start_date, end_date, status) "
        "VALUES (%s,%s,%s,'open')",
        (rate, today, end_date),
        commit=True,
    )
    return {
        "operation_id": op_id,
        "policy_rate": rate,
        "start_date": today,
        "end_date": end_date,
        "status": "open",
    }


def close_operation(operation_id):
    op = db.fetch_one("SELECT * FROM weekly_operations WHERE operation_id=%s", (operation_id,))
    if not op:
        raise AllocationError(f"Operation {operation_id} not found.")
    if op["status"] != "Open":
        raise AllocationError(f"Operation {operation_id} is already '{op['status']}'.")

    db.execute_query(
<<<<<<< HEAD
        "UPDATE weekly_operations SET status='Closed' WHERE operation_id=%s",
=======
        "UPDATE weekly_operations SET status='closed' WHERE operation_id=%s",
>>>>>>> ecae3a3b18086a1f5f14f0aa04df0494d488b147
        (operation_id,),
        commit=True,
    )
    return {"operation_id": operation_id, "status": "closed"}


def assert_operation_open_for_submission(operation_id):
    """Enforces 'no submissions once closed'. Used by Task 4.9 (bank
    submission screen)."""
    op = db.fetch_one(
        "SELECT status FROM weekly_operations WHERE operation_id=%s", (operation_id,)
    )
    if not op:
        raise AllocationError(f"Operation {operation_id} not found.")
    if op["status"] != "open":
        raise AllocationError(f"Operation {operation_id} is closed - no new submissions accepted.")
