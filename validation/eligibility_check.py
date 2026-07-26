from database.db import fetch_one


def check_eligibility(bank_id):
    """
    Check whether a bank is eligible to have its requests validated.

    Args:
        bank_id (int): commercial_banks.bank_id

    Returns:
        dict: {
            "stage": "eligibility",
            "result": "PASS" | "FAIL",
            "eligibility": <str | None>  raw value read from the DB
        }
    """
    row = fetch_one(
        "SELECT eligibility FROM commercial_banks WHERE bank_id = %s",
        (bank_id,),
    )

    eligibility = row["eligibility"] if row else None
    result = "PASS" if eligibility == "eligible" else "FAIL"

    return {
        "stage": "eligibility",
        "result": result,
        "eligibility": eligibility,
    }
