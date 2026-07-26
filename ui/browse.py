"""
Task 4.12 - Past weekly operations browser (read-only, both roles).

Nothing in this file ever calls INSERT/UPDATE/DELETE - it's SELECT-only by
construction, which is how "no edit/delete option exists anywhere in this
screen" is actually enforced rather than just promised.
"""
import database.db as db
from ui import reports


def list_past_operations():
    return db.fetch_all("SELECT * FROM weekly_operations ORDER BY operation_id DESC")


def operation_detail(operation_id, viewer):
    summary = reports.operation_summary(operation_id)
    if not summary:
        return None

    query = """SELECT r.request_id, r.bank_id, b.bank_name, r.requested_amount, r.status,
                      a.approved_amount, a.policy_rate,
                      rj.rejection_reason,
                      s.settlement_date, s.repayment_date, s.interest_amount AS interest
               FROM requests r
               JOIN commercial_banks b ON b.bank_id = r.bank_id
               LEFT JOIN allotments a ON a.request_id = r.request_id
               LEFT JOIN rejections rj ON rj.request_id = r.request_id
               LEFT JOIN settlements s ON s.allotment_id = a.allotment_id
               WHERE r.operation_id=%s"""
    params = (operation_id,)
    if viewer["role"] != "central_bank":
        query += " AND r.bank_id=%s"
        params = (operation_id, viewer["bank_id"])
    query += " ORDER BY r.request_id"
    requests = db.fetch_all(query, params)

    return {"summary": summary, "requests": requests}


def screen_browse_past_operations(viewer):
    ops = list_past_operations()
    print("\n=== PAST OPERATIONS ===")
    for op in ops:
        print(f"  #{op['operation_id']} status={op['status']} start={op['start_date']} end={op['end_date']}")
    return ops


def screen_operation_detail(operation_id, viewer):
    detail = operation_detail(operation_id, viewer)
    if not detail:
        print(f"Operation {operation_id} not found.")
        return None
    print(f"\n=== OPERATION {operation_id} DETAIL (read-only) ===")
    print(detail["summary"])
    for r in detail["requests"]:
        print(f"  req#{r['request_id']} bank={r['bank_name']} amount={r['requested_amount']} status={r['status']}")
    return detail
