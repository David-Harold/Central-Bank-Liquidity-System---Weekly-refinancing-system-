from database.db import fetch_all, fetch_one


def value_after_haircut(pledged_value, haircut_percentage):
    """
    Ths is just a calculation it doesn't touch the db

    Args:
        pledged_value (Decimal): The collateral's declared value.
        haircut_percentage (Decimal): Haircut as stored in collateral_types,
            e.g. 10.00 for 10% (column is DECIMAL(5,2), sized for
            percentage points, not a 0-1 fraction).

    Returns:
        Decimal: pledged_value * (1 - haircut_percentage / 100)
    """
    return pledged_value * (1 - (haircut_percentage / 100))


def check_collateral_value(request_id):
    """
    This one sums the post-haircut value of every collateral item pledged on a request
    and check it against the requested amount.

    Args:
        request_id (int): requests.request_id

    Returns:
        dict: {
            "stage": "collateral value after haircut",
            "result": "PASS" | "FAIL",
            "requested_amount": <value>,
            "value_after_haircut": <total post-haircut value>,
        }
    """
    request = fetch_one(
        "SELECT requested_amount FROM requests WHERE request_id = %s",
        (request_id,),
    )
    requested_amount = request["requested_amount"] if request else 0

    rows = fetch_all(
        """
        SELECT ci.declared_value, ct.haircut_percentage
        FROM request_collateral rc
        JOIN collateral_inventory ci ON ci.inventory_id = rc.inventory_id
        JOIN collateral_types ct ON ct.collateral_type_id = ci.collateral_type_id
        WHERE rc.request_id = %s
        """,
        (request_id,),
    )

    total_value_after_haircut = sum(
        value_after_haircut(row["declared_value"], row["haircut_percentage"])
        for row in rows
    )

    result = "PASS" if total_value_after_haircut >= requested_amount else "FAIL"

    return {
        "stage": "collateral value after haircut",
        "result": result,
        "requested_amount": requested_amount,
        "value_after_haircut": total_value_after_haircut,
    }
