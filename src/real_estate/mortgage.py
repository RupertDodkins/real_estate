import numpy as np
import pandas as pd

class Mortgage():
    def __init__(self, yearly_interest, loan_amount, mort_insur_frac=0.01, total_years=30):
        self.yearly_interest = yearly_interest
        self.total_years = total_years
        self.loan_amount = loan_amount
        self.mort_insur_frac = mort_insur_frac
        
        # self.yearly_interest /= 100
        self.monthly_interest = self.yearly_interest / 12
        self.num_payments = total_years * 12
        self.monthly_PI = self.calc_monthly_PI()
        self.df = self.amortization_df()
    
    def calc_monthly_PI(self):
        monthly_PI = self.loan_amount * (self.monthly_interest * np.power(1 + self.monthly_interest, self.num_payments)) / (np.power(1 + self.monthly_interest, self.num_payments) - 1)
        return monthly_PI
    
    def amortization_df(self):

        # # Compute monthly payment
        # monthly_payment = principal * (monthly_interest * np.power(1 + monthly_interest, self.num_payments)) / (np.power(1 + monthly_interest, self.num_payments) - 1)
        
        # Create an array for the number of payments
        payment_num = np.arange(1, self.num_payments + 1)

        # Calculate cumulative interest factor
        interest_factor = np.power(1 + self.monthly_interest, payment_num)
        
        # Compute the remaining balance for each payment
        remaining_balance = self.loan_amount * interest_factor - (self.monthly_PI / self.monthly_interest) * (interest_factor - 1)
        
        # Compute the interest for each payment
        interest_payment = remaining_balance * self.monthly_interest
        
        # Subtract to get the principal for each payment
        principal_payment = self.monthly_PI - interest_payment

        # Compute monthly mortgage insurance payment
        mortgage_insurance_payment = np.where((self.loan_amount - np.cumsum(principal_payment)) > 0.8 * self.loan_amount, self.loan_amount * self.mort_insur_frac / 12, 0)
        
        # Add mortgage insurance to monthly payment
        total_monthly_payment = self.monthly_PI + mortgage_insurance_payment

        # Put these arrays into a DataFrame
        data = {
            'Payment': total_monthly_payment,
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Mortgage Insurance': mortgage_insurance_payment,
            'Remaining Balance': remaining_balance
        }
        amortization_schedule = pd.DataFrame(data)
        return amortization_schedule