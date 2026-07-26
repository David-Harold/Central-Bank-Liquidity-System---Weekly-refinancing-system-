"""
Task 4.7 - Central Bank: settle an approved request.

Lists approved-but-unsettled requests, lets the Central Bank pick one, and
settles it via Component 3's settlement.py (Task 3.4).
"""
import db
import settlement


def screen_settle_request(viewer):
    pending_settlement = db.fetch_all(
        """SELECT r.request_id, r.bank_id, b.name AS bank_name, r.amount
           FROM requests r
           JOIN banks b ON b.bank_id = r.bank_id
           LEFT JOIN settlements s ON s.request_id = r.request_id
           WHERE r.status='successful' AND s.settlement_id IS NULL
           ORDER BY r.request_id"""
    )
    if not pending_settlement:
        print("No approved requests are waiting on settlement.")
        return pending_settlement
    print("Approved requests awaiting settlement:")
    for r in pending_settlement:
        print(f"  #{r['request_id']}  {r['bank_name']}  amount={r['amount']}")
    return pending_settlement


def settle_selected_request(request_id):
    try:
        result = settlement.settle_request(request_id)
        print(
            f"Request {request_id} settled. "
            f"Settlement date: {result['settlement_date']}, "
            f"repayment date: {result['repayment_date']}, "
            f"interest: {result['interest']}"
        )
        return result
    except settlement.AllocationError as e:
        print(f"Could not settle request {request_id}: {e}")
        return None
