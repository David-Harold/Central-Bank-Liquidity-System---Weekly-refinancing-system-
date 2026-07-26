from database.db import fetch_all


def check_collateral_admissibility(request_id):
    """
    Check that every collateral item pledged on a request is an admissible type.

    Args:
        request_id (int): requests.request_id

    Returns:
        dict: {
            "stage": "collateral admissibility",
            "result": "PASS" | "FAIL",
            "pledged": [
                {"inventory_id": <int>, "type_name": <str | None>, "admissible": <bool>},
                ...
            ]
        }
    """
    rows = fetch_all(
        """
        SELECT ci.inventory_id, ct.type_name
        FROM request_collateral rc
        JOIN collateral_inventory ci ON ci.inventory_id = rc.inventory_id
        LEFT JOIN collateral_types ct ON ct.collateral_type_id = ci.collateral_type_id
        WHERE rc.request_id = %s
        """,
        (request_id,),
    )

    pledged = [
        {
            "inventory_id": row["inventory_id"],
            "type_name": row["type_name"],
            "admissible": row["type_name"] is not None,
        }
        for row in rows
    ]

    result = "PASS" if pledged and all(item["admissible"] for item in pledged) else "FAIL"

    return {
        "stage": "collateral admissibility",
        "result": result,
        "pledged": pledged,
    }
