
from database.db import fetch_all
from validation.run_validation import run_validation
from allocation.approval import approve_request
from allocation.rejection import reject_request
def get_pending_requests():
    """
    Fetch all pending requests from the database.
    """
    query = "SELECT * FROM requests WHERE status = 'Pending'"
    return fetch_all(query)

def show_validation_result(validation_result):
    """
    Show the validation results for a particular pending request.
    """
    print(f"Validation Results for Request #{validation_result['request_id']}:\n")
    for stage, result in validation_result['stages'].items():
        print(f"{stage}: {result['result']}")
    print(f"\nOverall Result: {validation_result['result']}\n")

def screen_review_pending_request(request_id):
     """
     Screen that selects a pending requests, shows the validation results and prompts the central bank to approve or reject the request.
     """
     req_validation_result = run_validation(request_id)
     if req_validation_result['result'] == 'PASS':
         show_validation_result(req_validation_result)
         approval_result = approve_request(request_id)
         return approval_result
     else:
         show_validation_result(req_validation_result)
         rejection_message = input("Enter rejection reason: ")
         while not rejection_message.strip():   
             print("Rejection reason cannot be empty. Please provide a valid reason.")
             rejection_message = input("Enter rejection reason: ")
         rejection_result = reject_request(request_id, rejection_message)
         return rejection_result