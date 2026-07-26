"""
Task 3.4 - Settlement logic.

"""
import datetime

import database.db as db
from allocation.operations import AllocationError
from allocation.interest import calculate_interest


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
    if request["status"].lower() != "successful":
        raise AllocationError(f"Request {request_id} is '{request['status']}', not successful.")

    allotment = db.fetch_one("SELECT * FROM allotments WHERE request_id=%s", (request_id,))
    if not allotment:
        raise AllocationError(f"No allotment found for request {request_id}.")

    # settlements has no request_id column - it links back to the request
    # only via allotment_id, so "already settled" has to be checked there.
    already = db.fetch_one(
        "SELECT * FROM settlements WHERE allotment_id=%s", (allotment["allotment_id"],)
    )
    if already:
        raise AllocationError(f"Request {request_id} has already been settled.")

    settlement_date = today or datetime.date.today()
    repayment_date = settlement_date + datetime.timedelta(days=7)
    interest = calculate_interest(allotment["approved_amount"], allotment["policy_rate"], days=7)

    db.execute_query(
        """INSERT INTO settlements
               (allotment_id, settlement_date, repayment_date, interest_amount)
           VALUES (%s,%s,%s,%s)""",
        (allotment["allotment_id"], settlement_date, repayment_date, interest),
    )
    return {
        "request_id": request_id,
        "settlement_date": settlement_date,
        "repayment_date": repayment_date,
        "principal": float(allotment["approved_amount"]),
        "interest": interest,
    }