from database.db import fetch_one
from validation.eligibility_check import check_eligibility
from validation.collateral_admissibility_check import check_collateral_admissibility
from validation.collateral_value_after_haircut import check_collateral_value
from validation.borrowing_limit_check import check_borrowing_limit
def run_validation(request_id):
    """
    Run the validation flow for a specific commercial bank request.
    """
    req = fetch_one(
        "SELECT bank_id FROM requests WHERE request_id = %s",
        (request_id,),
    )
    bank_id = req["bank_id"] if req else None
    eligibility_result = check_eligibility(bank_id)
    collateral_admissibility_result = check_collateral_admissibility(request_id)
    collateral_value_result = check_collateral_value(request_id)
    borrowing_limit_result = check_borrowing_limit(request_id)

    stages = {
        "eligibility": eligibility_result,
        "collateral_admissibility": collateral_admissibility_result,
        "collateral_value": collateral_value_result,
        "borrowing_limit": borrowing_limit_result
    }

    final_result = "PASS" if all(stage["result"] == "PASS" for stage in stages.values()) else "FAIL"

    return {
        "stage": "Overall validation",
        "request_id": request_id,
        "stages": stages,
        "result": final_result
    }