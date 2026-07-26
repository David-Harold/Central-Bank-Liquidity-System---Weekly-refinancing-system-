from database.db import execute_query, fetch_all, fetch_one

def get_operation_id():
    """
    Fetch the operation ID from the database.
    """
    query = "SELECT operation_id FROM weekly_operations WHERE status = 'Open'"
    result = fetch_one(query)
    return result["operation_id"] if result else None

def get_bank_inventory(bank_id):
    """
    Returns this bank's collateral inventory, joined with type name.
    """
    query = """
        SELECT ci.inventory_id, ct.type_name, ci.declared_value
        FROM collateral_inventory ci
        JOIN collateral_types ct ON ct.collateral_type_id = ci.collateral_type_id
        WHERE ci.bank_id = %s
    """
    return fetch_all(query, (bank_id,))

def loan_request_screen(bank_id):
    operation_id = get_operation_id()
    if not operation_id:
        print("No open operation found. Please contact the system administrator.")
        return

    if operation_id:
        # fetch  requests for this operation
        requests = fetch_all(
            """SELECT * FROM requests WHERE bank_id = %s AND operation_id = %s""",
            (bank_id, operation_id)
        )

    if not requests:
        amount = input("Enter the requested amount: ")
        try:
            amount = float(amount)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return
        collateral_inventory = get_bank_inventory(bank_id)
        if not collateral_inventory:
            print("Please add assets as collateral first.")
            return
        execute_query(
            """INSERT INTO requests (bank_id, operation_id, requested_amount, status) VALUES (%s, %s, %s, 'Pending')""",
            (bank_id, operation_id, amount)
        )