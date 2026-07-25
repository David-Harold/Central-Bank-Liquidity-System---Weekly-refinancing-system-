
from validation.run_validation import run_validation
from validation.borrowing_limit_check import check_borrowing_limit
from validation.eligibility_check import check_eligibility
from validation.collateral_admissibility_check import (
    check_collateral_admissibility,
)
from validation.collateral_value_after_haircut import (
    check_collateral_value,
)

TEST_BANK_ID = 9001
TEST_REQUEST_ID = 9001

if __name__ == "__main__":
    print(check_eligibility(TEST_BANK_ID))
    print(check_collateral_admissibility(TEST_REQUEST_ID))
    print(check_collateral_value(TEST_REQUEST_ID))
    print(check_borrowing_limit(TEST_REQUEST_ID))
    print(run_validation(TEST_REQUEST_ID))
