"""
Task 3.5 - Weekly operation state management.

Also defines AllocationError, the shared exception every Component 3 module
raises for invalid state transitions - imported from here by approval.py,
rejection.py, and settlement.py so a single `except AllocationError` catches
errors from any of them.
"""
import datetime

import db


class AllocationError(Exception):
    """Raised whenever a Component 3 rule is violated (invalid state
    transition, double settlement, operation already open, etc.)."""


def open_operation(rate):
    """Enforces 'only one weekly operation open at a time'."""
    open_op = db.fetch_one("SELECT * FROM weekly_operations WHERE status='open'")
    if open_op:
        raise AllocationError(
            f"Cannot open a new operation: operation {open_op['operation_id']} is already open."
        )
    op_id = db.execute_query(
        "INSERT INTO weekly_operations (policy_rate, status) VALUES (%s,'open')",
        (rate,),
        commit=True,
    )
    return {"operation_id": op_id, "policy_rate": rate, "status": "open"}


def close_operation(operation_id):
    op = db.fetch_one("SELECT * FROM weekly_operations WHERE operation_id=%s", (operation_id,))
    if not op:
        raise AllocationError(f"Operation {operation_id} not found.")
    if op["status"] != "open":
        raise AllocationError(f"Operation {operation_id} is already '{op['status']}'.")

    db.execute_query(
        "UPDATE weekly_operations SET status='closed', closed_at=%s WHERE operation_id=%s",
        (datetime.datetime.now(), operation_id),
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
