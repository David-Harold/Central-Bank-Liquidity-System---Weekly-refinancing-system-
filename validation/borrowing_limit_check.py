from database.db import fetch_one
def check_borrowing_limit(request_id):
    """
    Check if the requested amount exceeds the bank's borrowing limit.
    """
    requested_amount = fetch_one(
        "SELECT requested_amount FROM requests WHERE request_id = %s",
        (request_id,),
    )
    borrowing_limit = fetch_one(
        "SELECT borrowing_limit FROM commercial_banks cb JOIN requests r ON cb.bank_id = r.bank_id WHERE r.request_id = %s",
        (request_id,),
    )

    requested_amount = requested_amount["requested_amount"] if requested_amount else 0
    borrowing_limit = borrowing_limit["borrowing_limit"] if borrowing_limit else 0

    result = "PASS" if requested_amount <= borrowing_limit else "FAIL"
    return {
        "stage": "borrowing limit check",
        "result": result,
    }