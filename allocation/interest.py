"""
Task 3.3 - Interest calculation.
"""


def calculate_interest(principal, rate, days=7):
    """interest = principal * rate * (days/365). rate is a decimal (0.045 = 4.5%)."""
    return round(float(principal) * float(rate) * (days / 365), 2)
