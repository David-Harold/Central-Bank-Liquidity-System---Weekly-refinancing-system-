"""
Task 4.11 - Reporting module.

Central Bank sees every bank's data in every report. A Bank only ever sees
rows matching its own bank_id, with no way to override that from the menu.
"""
import db


def _scope_bank_id(viewer, requested_bank_id=None):
    if viewer["role"] == "central_bank":
        return requested_bank_id
    return viewer["bank_id"]


def operation_summary(operation_id):
    op = db.fetch_one("SELECT * FROM weekly_operations WHERE operation_id=%s", (operation_id,))
    if not op:
        return None
    totals = db.fetch_one(
        """SELECT
             COUNT(*) AS total_requests,
             SUM(CASE WHEN status='successful' THEN 1 ELSE 0 END) AS approved,
             SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS rejected,
             SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) AS pending
           FROM requests WHERE operation_id=%s""",
        (operation_id,),
    )
    allotted = db.fetch_one(
        """SELECT COALESCE(SUM(a.approved_amount),0) AS total_allotted
           FROM allotments a JOIN requests r ON r.request_id = a.request_id
           WHERE r.operation_id=%s""",
        (operation_id,),
    )
    return {**op, **totals, **allotted}


def full_operation_history():
    return db.fetch_all("SELECT * FROM weekly_operations ORDER BY operation_id DESC")


def rejection_log(viewer, bank_id=None):
    scoped = _scope_bank_id(viewer, bank_id)
    query = """SELECT rj.rejection_id, rj.request_id, r.bank_id, b.name AS bank_name,
                      r.operation_id, r.amount, rj.reason, rj.rejected_at
               FROM rejections rj
               JOIN requests r ON r.request_id = rj.request_id
               JOIN banks b ON b.bank_id = r.bank_id"""
    params = ()
    if scoped is not None:
        query += " WHERE r.bank_id=%s"
        params = (scoped,)
    query += " ORDER BY rj.rejected_at DESC"
    return db.fetch_all(query, params)


def per_bank_borrowing_history(viewer, bank_id=None):
    scoped = _scope_bank_id(viewer, bank_id)
    query = """SELECT r.request_id, r.bank_id, b.name AS bank_name, r.operation_id,
                      r.amount, r.status, a.approved_amount, a.rate,
                      s.settlement_date, s.repayment_date, s.interest
               FROM requests r
               JOIN banks b ON b.bank_id = r.bank_id
               LEFT JOIN allotments a ON a.request_id = r.request_id
               LEFT JOIN settlements s ON s.request_id = r.request_id"""
    params = ()
    if scoped is not None:
        query += " WHERE r.bank_id=%s"
        params = (scoped,)
    query += " ORDER BY r.request_id DESC"
    return db.fetch_all(query, params)


def collateral_inventory_report(viewer, bank_id=None):
    scoped = _scope_bank_id(viewer, bank_id)
    query = """SELECT ci.asset_id, ci.bank_id, b.name AS bank_name,
                      ct.name AS collateral_type, ct.haircut_pct, ci.declared_value
               FROM collateral_inventory ci
               JOIN banks b ON b.bank_id = ci.bank_id
               JOIN collateral_types ct ON ct.type_id = ci.type_id"""
    params = ()
    if scoped is not None:
        query += " WHERE ci.bank_id=%s"
        params = (scoped,)
    query += " ORDER BY ci.bank_id, ci.asset_id"
    return db.fetch_all(query, params)


def screen_reports(viewer):
    """The menu-facing screen: prints every report view, scoped by role."""
    print(f"\n=== REPORTS ({viewer['role']}) ===")
    history = full_operation_history()
    print(f"Operations on file: {len(history)}")

    borrowing = per_bank_borrowing_history(viewer)
    print(f"\nBorrowing history ({len(borrowing)} rows):")
    for row in borrowing:
        print(
            f"  req#{row['request_id']} bank={row['bank_name']} "
            f"amount={row['amount']} status={row['status']}"
        )

    rejections = rejection_log(viewer)
    print(f"\nRejection log ({len(rejections)} rows):")
    for row in rejections:
        print(f"  req#{row['request_id']} bank={row['bank_name']} reason={row['reason']}")

    inventory = collateral_inventory_report(viewer)
    print(f"\nCollateral inventory ({len(inventory)} rows):")
    for row in inventory:
        print(
            f"  asset#{row['asset_id']} bank={row['bank_name']} "
            f"type={row['collateral_type']} value={row['declared_value']}"
        )

    return {"borrowing": borrowing, "rejections": rejections, "inventory": inventory}
