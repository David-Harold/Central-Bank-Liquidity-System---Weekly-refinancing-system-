"""
Task 4.5 - Central Bank: open/close weekly operation.

Thin screens wired to Component 3's operations.py (Task 3.5) logic.
"""
import operations


def screen_open_operation(rate):
    try:
        result = operations.open_operation(rate)
        print(f"Operation {result['operation_id']} opened at rate {result['policy_rate']}.")
        return result
    except operations.AllocationError as e:
        print(f"Could not open operation: {e}")
        return None


def screen_close_operation(operation_id):
    try:
        result = operations.close_operation(operation_id)
        print(f"Operation {operation_id} closed.")
        return result
    except operations.AllocationError as e:
        print(f"Could not close operation: {e}")
        return None
