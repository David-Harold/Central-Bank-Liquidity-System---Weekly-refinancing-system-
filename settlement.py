"""
Task 3.4 - Settlement logic.
"""
import datetime

import db
from operations import AllocationError
from interest import calculate_interest


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
