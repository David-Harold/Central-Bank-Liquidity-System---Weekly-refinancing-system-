"""
Component 3 - Allocation & Settlement Logic (Tasks 3.1-3.5).
"""
import datetime

import database.db as db


class AllocationError(Exception):
    """Raised whenever a Component 3 rule is violated (invalid state
    transition, double settlement, operation already open, etc.)."""


#  Task 3.1 
def approve_request(request_id, rate=None):
    """
    Marks a request 'successful' and records an allotment.

    Deliberately does NOT re-check validation results here: per the
    project's business logic, the Central Bank reviews the live PASS/FAIL
    output from Task 2.5 and then decides. Approval reflects the CB's
    judgment call, not an automatic gate re-run.
    """
    request = db.fetch_one("SELECT * FROM requests WHERE request_id=%s", (request_id,))
    if not request:
        raise AllocationError(f"Request {request_id} not found.")
    if request["status"] != "pending":
        raise AllocationError(f"Request {request_id} is '{request['status']}', not pending.")

    if rate is None:
        op = db.fetch_one(
            "SELECT policy_rate FROM weekly_operations WHERE operation_id=%s",
            (request["operation_id"],),
        )
        rate = op["policy_rate"]

    db.execute_query(
        "UPDATE requests SET status='successful' WHERE request_id=%s",
        (request_id,),
        commit=True,
    )
    db.execute_query(
        "INSERT INTO allotments (request_id, approved_amount, rate) VALUES (%s,%s,%s)",
        (request_id, request["amount"], rate),
        commit=True,
    )
    return {
        "request_id": request_id,
        "status": "successful",
        "approved_amount": float(request["amount"]),
        "rate": float(rate),
    }


#  Task 3.2 
def reject_request(request_id, reason):
    """Marks a request 'failed' and logs the Central Bank's typed reason."""
    if not reason or not reason.strip():
        raise AllocationError("A rejection reason is required.")

    request = db.fetch_one("SELECT * FROM requests WHERE request_id=%s", (request_id,))
    if not request:
        raise AllocationError(f"Request {request_id} not found.")
    if request["status"] != "pending":
        raise AllocationError(f"Request {request_id} is '{request['status']}', not pending.")

    db.execute_query(
        "UPDATE requests SET status='failed' WHERE request_id=%s",
        (request_id,),
        commit=True,
    )
    db.execute_query(
        "INSERT INTO rejections (request_id, reason) VALUES (%s,%s)",
        (request_id, reason.strip()),
        commit=True,
    )
    return {"request_id": request_id, "status": "failed", "reason": reason.strip()}


#  Task 3.3 
def calculate_interest(principal, rate, days=7):
    """interest = principal * rate * (days/365). rate is a decimal (0.045 = 4.5%)."""
    return round(float(principal) * float(rate) * (days / 365), 2)


# Task 3.4 
def settle_request(request_id, today=None):
    """
    Settles an approved request: stamps settlement date (today) and
    repayment date (+7 days), computes interest via Task 3.3.
    Guards against settling twice and against settling anything that
    isn't currently 'successful'.
    """
    request = db.fetch_one("SELECT * FROM requests WHERE request_id=%s", (request_id,))
    if not request:
        raise AllocationError(f"Request {request_id} not found.")
    if request["status"] != "successful":
        raise AllocationError(f"Request {request_id} is '{request['status']}', not successful.")

    already = db.fetch_one("SELECT * FROM settlements WHERE request_id=%s", (request_id,))
    if already:
        raise AllocationError(f"Request {request_id} has already been settled.")

    allotment = db.fetch_one("SELECT * FROM allotments WHERE request_id=%s", (request_id,))
    if not allotment:
        raise AllocationError(f"No allotment found for request {request_id}.")

    settlement_date = today or datetime.date.today()
    repayment_date = settlement_date + datetime.timedelta(days=7)
    interest = calculate_interest(allotment["approved_amount"], allotment["rate"], days=7)

    db.execute_query(
        """INSERT INTO settlements
               (request_id, settlement_date, repayment_date, principal, interest)
           VALUES (%s,%s,%s,%s,%s)""",
        (request_id, settlement_date, repayment_date, allotment["approved_amount"], interest),
        commit=True,
    )
    return {
        "request_id": request_id,
        "settlement_date": settlement_date,
        "repayment_date": repayment_date,
        "principal": float(allotment["approved_amount"]),
        "interest": interest,
    }


#  Task 3.5
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
    submission screen) - not this batch's focus, but the rule is owned by
    Component 3 so it lives here rather than being duplicated in the UI."""
    op = db.fetch_one(
        "SELECT status FROM weekly_operations WHERE operation_id=%s", (operation_id,)
    )
    if not op:
        raise AllocationError(f"Operation {operation_id} not found.")
    if op["status"] != "open":
        raise AllocationError(f"Operation {operation_id} is closed - no new submissions accepted.")

