import pandas as pd


def calculate_dti(monthly_debt, monthly_income):
    return monthly_debt / monthly_income


def calculate_lti(loan_amount, annual_income):
    return loan_amount / annual_income
