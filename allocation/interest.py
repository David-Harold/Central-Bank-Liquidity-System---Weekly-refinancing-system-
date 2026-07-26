"""
Task 3.3 - Interest calculation.

`rate` is a decimal fraction (e.g. 0.045 for 4.5%), not a percentage.
"""


def calculate_interest(principal, rate, days=7):
    """interest = principal * rate * (days/365)."""
    return round(float(principal) * float(rate) * (days / 365), 2)
