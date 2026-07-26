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

    # fetch this bank's existing requests for this operation
    requests = fetch_all(
        "SELECT * FROM requests WHERE bank_id = %s AND operation_id = %s",
        (bank_id, operation_id)
    )

    if requests:
        print("You have already submitted a request for this operation.")
        return

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

    print("\nYour available collateral:")
    for item in collateral_inventory:
        print(f"  [{item['inventory_id']}] {item['type_name']} - {item['declared_value']}")

    selected_collateral_ids = input("Enter inventory ID(s) to pledge (comma-separated): ")
    try:
        selected_ids = [int(x.strip()) for x in selected_collateral_ids.split(",") if x.strip()]
    except ValueError:
        print("Invalid input. Please enter valid inventory IDs.")
        return

    if not selected_ids:
        print("No collateral selected. Request cancelled.")
        return

    valid_ids = {item["inventory_id"] for item in collateral_inventory}
    invalid_selection = [i for i in selected_ids if i not in valid_ids]
    if invalid_selection:
        print(f"Invalid inventory ID(s): {invalid_selection}. Request cancelled.")
        return

    execute_query(
        "INSERT INTO requests (bank_id, operation_id, requested_amount, status) VALUES (%s, %s, %s, 'Pending')",
        (bank_id, operation_id, amount)
    )

    new_request = fetch_one(
        "SELECT request_id FROM requests WHERE bank_id = %s AND operation_id = %s",
        (bank_id, operation_id)
    )
    request_id = new_request["request_id"]

    for inv_id in selected_ids:
        execute_query(
            "INSERT INTO request_collateral (request_id, inventory_id) VALUES (%s, %s)",
            (request_id, inv_id)
        )

    print(f"Request submitted successfully. Request ID: {request_id}, Amount: {amount}")