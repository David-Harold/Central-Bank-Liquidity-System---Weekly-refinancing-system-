"""
Task 3.2 - Rejection handling.
"""
import db
from operations import AllocationError


def reject_request(request_id, reason):
    """Marks a request 'failed' and logs the Central Bank's typed reason."""
    if not reason or not reason.strip():
        raise AllocationError("A rejection reason is required.")

    request = db.fetch_one("SELECT * FROM requests WHERE request_id=%s", (request_id,))
    if not request:
        raise AllocationError(f"Request {request_id} not found.")
    if request["status"] != "pending":
        raise AllocationError(f"Request {request_id} is '{request['status']}', not pending.")

    db.execute_query(
        "UPDATE requests SET status='failed' WHERE request_id=%s",
        (request_id,),
        commit=True,
    )
    db.execute_query(
        "INSERT INTO rejections (request_id, reason) VALUES (%s,%s)",
        (request_id, reason.strip()),
        commit=True,
    )
    return {"request_id": request_id, "status": "failed", "reason": reason.strip()}
