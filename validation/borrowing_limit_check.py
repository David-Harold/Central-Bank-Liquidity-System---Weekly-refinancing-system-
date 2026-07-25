from database.db import fetch_one
def check_borrowing_limit(bank_id, amount):
    """
    Check if the requested amount exceeds the bank's borrowing limit.
    """
    result = fetch_one(
        "SELECT borrowing_limit FROM commercial_banks WHERE bank_id = %s",
        (bank_id,),
    )
    borrowing_limit = result["borrowing_limit"] if result else 0
    return "PASS" if amount <= borrowing_limit else "FAIL"