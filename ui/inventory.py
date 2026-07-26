import database.db as db


class InventoryError(Exception):
    """Raised when an inventory action can't be completed as requested."""


def list_admissible_types():
    return db.fetch_all(
        "SELECT collateral_type_id, type_name, haircut_percentage "
        "FROM collateral_types ORDER BY type_name"
    )


def list_bank_inventory(bank_id):
    return db.fetch_all(
        """SELECT ci.inventory_id, ci.declared_value,
                  ct.collateral_type_id, ct.type_name, ct.haircut_percentage
           FROM collateral_inventory ci
           JOIN collateral_types ct ON ct.collateral_type_id = ci.collateral_type_id
           WHERE ci.bank_id = %s
           ORDER BY ci.inventory_id DESC""",
        (bank_id,),
    )


def add_collateral(bank_id, collateral_type_id, declared_value):
    try:
        declared_value = float(declared_value)
    except (TypeError, ValueError):
        raise InventoryError("Declared value must be a number.")
    if declared_value <= 0:
        raise InventoryError("Declared value must be a positive number.")

    ctype = db.fetch_one(
        "SELECT collateral_type_id, type_name FROM collateral_types "
        "WHERE collateral_type_id = %s",
        (collateral_type_id,),
    )
    if not ctype:
        raise InventoryError(
            f"Collateral type {collateral_type_id} is not an admissible type."
        )

    db.execute_query(
        "INSERT INTO collateral_inventory (bank_id, collateral_type_id, declared_value) "
        "VALUES (%s, %s, %s)",
        (bank_id, collateral_type_id, declared_value),
    )
    return {
        "bank_id": bank_id,
        "collateral_type_id": collateral_type_id,
        "type_name": ctype["type_name"],
        "declared_value": declared_value,
    }


#  screens (t will be called by the Bank menu shell with the collected input from  a user) 

def screen_view_admissible_types():
    types = list_admissible_types()
    print("\nAdmissible collateral types:")
    if not types:
        print("  (the Central Bank hasn't defined any collateral types yet)")
    for t in types:
        print(
            f"  {t['collateral_type_id']}. {t['type_name']}  "
            f"(haircut {t['haircut_percentage']}%)"
        )
    return types


def screen_view_inventory(bank_id):
    inventory = list_bank_inventory(bank_id)
    print("\nYour collateral inventory:")
    if not inventory:
        print("  (empty - add an asset first)")
    for item in inventory:
        print(
            f"  #{item['inventory_id']}  {item['type_name']}  "
            f"value={item['declared_value']}  haircut={item['haircut_percentage']}%"
        )
    return inventory


def screen_add_collateral(bank_id, collateral_type_id, declared_value):
    """
    Expects collateral_type_id and declared_value already collected by
    the menu shell (e.g. after showing screen_view_admissible_types()
    and prompting for a value).
    """
    try:
        result = add_collateral(bank_id, collateral_type_id, declared_value)
        print(f"Added: {result['type_name']} - value {result['declared_value']} to your inventory.")
        return result
    except InventoryError as e:
        print(f"Could not add asset: {e}")
        return None
