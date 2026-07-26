"""
Task 3.1 - Approval handling.
"""
import database.db as db
from allocation.operations import AllocationError


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
        "INSERT INTO allotments (request_id, approved_amount, policy_rate) VALUES (%s,%s,%s)",
        (request_id, request["requested_amount"], rate),
        commit=True,
    )
    return {
        "request_id": request_id,
        "status": "successful",
        "approved_amount": float(request["requested_amount"]),
        "policy_rate": float(rate),
    }
