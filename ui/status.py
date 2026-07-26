import database.db as db


def list_my_requests(bank_id):
    return db.fetch_all(
        """SELECT request_id, operation_id, requested_amount, status
           FROM requests
           WHERE bank_id = %s
           ORDER BY request_id DESC""",
        (bank_id,),
    )


def get_request_status(bank_id, request_id):
    request = db.fetch_one(
        """SELECT request_id, bank_id, operation_id, requested_amount, status
           FROM requests
           WHERE request_id = %s AND bank_id = %s""",
        (request_id, bank_id),
    )
    if not request:
        return None

    request["rejection_reason"] = None
    if request["status"].lower() == "failed":
        rejection = db.fetch_one(
            "SELECT rejection_reason FROM rejections WHERE request_id = %s "
            "ORDER BY rejection_id DESC LIMIT 1",
            (request_id,),
        )
        if rejection:
            request["rejection_reason"] = rejection["rejection_reason"]

    return request


#  screens (called by the Bank menu shell with it's collected input) from a user 

def screen_list_my_requests(bank_id):
    """Shown first, so the bank can see which request_id to check in detail."""
    requests = list_my_requests(bank_id)
    print("\nYour requests:")
    if not requests:
        print("  (none submitted yet)")
    for r in requests:
        print(
            f"  #{r['request_id']}  operation={r['operation_id']}  "
            f"amount={r['requested_amount']}  status={r['status'].upper()}"
        )
    return requests


def screen_check_status(bank_id, request_id):
    request = get_request_status(bank_id, request_id)
    if not request:
        print(f"Request {request_id} not found for your bank.")
        return None

    print(f"\nRequest #{request['request_id']}  status: {request['status'].upper()}")
    if request["status"].lower() == "failed":
        reason = request["rejection_reason"] or "(no reason on file)"
        print(f"Rejection reason: {reason}")
    return request

