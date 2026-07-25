"""
UI screens for Tasks 4.5, 4.7, 4.11, 4.12.

Each screen function prints to the console AND returns a structured result,
so it can be driven by menu.py and also asserted on directly in tests.
"""
import db
import allocation
import reporting
import browse


# --- Task 4.5 --------------------------------------------------------------
def screen_open_operation(rate):
    try:
        result = allocation.open_operation(rate)
        print(f"Operation {result['operation_id']} opened at rate {result['policy_rate']}.")
        return result
    except allocation.AllocationError as e:
        print(f"Could not open operation: {e}")
        return None


def screen_close_operation(operation_id):
    try:
        result = allocation.close_operation(operation_id)
        print(f"Operation {operation_id} closed.")
        return result
    except allocation.AllocationError as e:
        print(f"Could not close operation: {e}")
        return None


# --- Task 4.7 ----------------------------------------------------------
def screen_settle_request(viewer):
    """List approved-but-unsettled requests so the Central Bank can pick one."""
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
        result = allocation.settle_request(request_id)
        print(
            f"Request {request_id} settled. "
            f"Settlement date: {result['settlement_date']}, "
            f"repayment date: {result['repayment_date']}, "
            f"interest: {result['interest']}"
        )
        return result
    except allocation.AllocationError as e:
        print(f"Could not settle request {request_id}: {e}")
        return None


# --- Task 4.11 ---------------------------------------------------------
def screen_reports(viewer):
    """Menu of report views, scoped by viewer role (Task 4.11)."""
    print(f"\n=== REPORTS ({viewer['role']}) ===")
    history = reporting.full_operation_history()
    print(f"Operations on file: {len(history)}")

    borrowing = reporting.per_bank_borrowing_history(viewer)
    print(f"\nBorrowing history ({len(borrowing)} rows):")
    for row in borrowing:
        print(
            f"  req#{row['request_id']} bank={row['bank_name']} "
            f"amount={row['amount']} status={row['status']}"
        )

    rejections = reporting.rejection_log(viewer)
    print(f"\nRejection log ({len(rejections)} rows):")
    for row in rejections:
        print(f"  req#{row['request_id']} bank={row['bank_name']} reason={row['reason']}")

    inventory = reporting.collateral_inventory_report(viewer)
    print(f"\nCollateral inventory ({len(inventory)} rows):")
    for row in inventory:
        print(
            f"  asset#{row['asset_id']} bank={row['bank_name']} "
            f"type={row['collateral_type']} value={row['declared_value']}"
        )

    return {"borrowing": borrowing, "rejections": rejections, "inventory": inventory}


# --- Task 4.12 ---------------------------------------------------------
def screen_browse_past_operations(viewer):
    ops = browse.list_past_operations()
    print("\n=== PAST OPERATIONS ===")
    for op in ops:
        print(f"  #{op['operation_id']} status={op['status']} rate={op['policy_rate']} opened={op['opened_at']}")
    return ops


def screen_operation_detail(operation_id, viewer):
    detail = browse.operation_detail(operation_id, viewer)
    if not detail:
        print(f"Operation {operation_id} not found.")
        return None
    print(f"\n=== OPERATION {operation_id} DETAIL (read-only) ===")
    print(detail["summary"])
    for r in detail["requests"]:
        print(f"  req#{r['request_id']} bank={r['bank_name']} amount={r['amount']} status={r['status']}")
    return detail

