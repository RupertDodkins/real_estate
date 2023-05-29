import numpy as np
from real_estate.mortgage import Mortgage
from real_estate.constants import yearly_months

class Acquisition():
    """ Could inherent a Mortgage object if it could contain several methods """
    def __init__(self, purchase_price, downpayment, yearly_interest, value_appreciation, monthly_HOA=0, 
                 yearly_insurance=1250, yearly_taxes=0, monthly_utilities=200):
        self.time = {}
        self.price = {
            'home_value': purchase_price,
            'downpayment': downpayment,
            'mortgage': np.nan,
            'monthly_PI': np.nan,
            'yearly_taxes': yearly_taxes,
            'monthly_HOA': monthly_HOA,
            'yearly_insurance': yearly_insurance,
            'monthly_utilities': monthly_utilities
        } 
        self.exponent ={
            'yearly_interest': yearly_interest,
            'yearly_val_apprec': value_appreciation
        }
        self.mort = None
        
        self.derive_properties()
        
    def derive_properties(self):
#         super().__init__(self.price['yearly_interest'], 30, self.price['price'])
        self.price['loan_fees'] = 0.01 * self.price['home_value']
        self.price['mortgage'] = self.price['home_value'] - self.price['downpayment'] + self.price['loan_fees']
        self.price['closing'] = self.price['home_value'] * 0.01 
        if self.price['yearly_taxes'] == 0:
            self.price['yearly_taxes'] = self.price['home_value'] * 0.0111
        self.price['monthly_taxes'] = self.price['yearly_taxes']/yearly_months
        self.price['monthly_insurance'] = self.price['yearly_insurance']/yearly_months
        self.mort = Mortgage(self.exponent['yearly_interest'], self.price['mortgage'])
        self.price['owning_expenses'] = self.sum_owning_expenses()
        self.price['monthly_PI'] = self.mort.monthly_PI

    def sum_owning_expenses(self):
        own_ex = self.price['monthly_taxes'] + self.price['monthly_insurance'] + self.price['monthly_HOA'] + self.price['monthly_utilities']
        own_ex += self.mort.df.iloc[0]['Mortgage Insurance']
        return own_ex
    
    def __str__(self):
        return (
            '\nAcquisition:\n'
            f"Down Payment: ${self.price['downpayment']}\n"
            f"Loan Amount: ${self.price['mortgage']}\n"
            f"Loan Points/Fees: ${self.price['loan_fees']}\n"
            f"Loan Interest Rate: {self.exponent['yearly_interest']*100}%\n"
            f"Monthly P&I: ${self.price['monthly_PI']:.2f}\n"
            f"Home Value Appreciaion: ${self.exponent['yearly_val_apprec']*100}%"
         )
        
class Rehab():
    def __init__(self, rehab_months, total_cost, monthly_PI, owning_expenses, monthly_insurance=0, other_costs = 0):
        self.time = {
            'total_months' : rehab_months
        }
        self.price= {
            'total_cost': total_cost,
            'monthly_insurance': monthly_insurance,
            'other': other_costs,
            'holding_cost': np.nan,
            'monthly_PI': monthly_PI,
            'owning_expenses': owning_expenses
        } 
        self.exponent = {
        }

        self.derive_properties()
        
    def derive_properties(self):
        self.price['monthly_rehab'] = self.price['total_cost']*self.time['total_months']/yearly_months
        self.price['holding_cost'] = (self.price['monthly_PI'] + self.price['owning_expenses']) * self.time['total_months']
        self.price['monthly_total'] = self.price['monthly_rehab'] + self.price['owning_expenses'] + self.price['monthly_PI']
        
    def __str__(self):
        return (
            '\nRehab:\n'
            f"Holding costs: ${self.price['holding_cost']:.2f}\n"
            f"Monthly P&I: ${self.price['monthly_PI']:.2f}\n"
            f"Rehab time: {self.time['total_months']} months\n"
            f"Owning expenses: ${self.price['owning_expenses']}"
        )
    
class PreReFi_Rent():
    """ Could inherent a Mortgage object if """
    def __init__(self, monthly_rent, vacancy_frac, repairs_frac, capex_frac, total_time, 
                monthly_PI, rent_appreciation, opex_inflation, owning_expenses):
        self.time = {
            'total_months': total_time
        }
        self.price =  {
            'monthly_rent': monthly_rent,
            'vacancy_frac': vacancy_frac,
            'repairs_frac': repairs_frac,
            'capex_frac': capex_frac,
            'owning_expenses': owning_expenses,
            'monthly_PI': monthly_PI
        } 
        self.exponent = {
            'yearly_rent_apprec': rent_appreciation,
            'yearly_opex_inflation': opex_inflation,
            }
        self.derive_properties()
        
    def derive_properties(self):
        self.price['monthly_vacancy'] = self.price['monthly_rent']*self.price['vacancy_frac']
        self.price['monthly_repairs'] = self.price['monthly_rent']*self.price['repairs_frac']
        self.price['monthly_capex'] = self.price['monthly_rent']*self.price['capex_frac']
        self.price['monthly_OpEx'] = self.sum_opex()
        self.price['monthly_expenses'] = self.price['monthly_OpEx'] + self.price['monthly_PI']
        self.price['monthly_cashflow'] = self.price['monthly_rent'] - self.price['monthly_expenses']
        self.price['NOI'] = (self.price['monthly_cashflow'] + self.price['monthly_PI']) * yearly_months  # googled NOI vs cash flow

    def sum_opex(self):
        exp_sum = self.price['monthly_vacancy'] + self.price['monthly_capex'] \
        + self.price['owning_expenses'] + self.price['monthly_repairs'] #+ self.price['monthly_PI']
        return exp_sum
    
    def __str__(self):
        return (
            '\nInitial Rental Period:\n'
            f"Monthly Income: ${self.price['monthly_rent']}\n"
            f"Monthly Expenses: ${self.price['monthly_expenses']:.2f}\n"
            f"Monthly Cashflow: ${self.price['monthly_cashflow']:.2f}\n"
            f"NOI: ${self.price['NOI']}"
        )

class Refinance():
    """ Could inherent a Mortgage object if """
    def __init__(self, monthly_rent, home_value, vacancy_frac, repairs_frac, capex_frac, refinance_months, yearly_interest, value_appreciation,
                 rent_appreciation, opex_inflation, owning_expenses):
        self.time =  {
            'total_months': refinance_months
        }
        self.price =  {
            'monthly_rent': monthly_rent,
            'home_value': home_value,
            'vacancy_frac': vacancy_frac,
            'repairs_frac': repairs_frac,
            'capex_frac': capex_frac,
            'monthly_PI': np.nan,
            'owning_expenses': owning_expenses
        } 
        self.exponent = {
            'yearly_interest': yearly_interest, #0#0.065
            'yearly_val_apprec': value_appreciation,
            'yearly_rent_apprec': rent_appreciation,
            'yearly_opex_inflation': opex_inflation,
        }
        self.mort = None
        self.derive_properties()

    def derive_properties(self):
        self.price['monthly_vacancy'] = self.price['monthly_rent']*self.price['vacancy_frac']
        self.price['monthly_repairs'] = self.price['monthly_rent']*self.price['repairs_frac']
        self.price['monthly_capex'] = self.price['monthly_rent']*self.price['capex_frac']
        self.price['loan_fees'] = 0.01 * self.price['home_value']
        self.price['mortgage'] = 0.8 * self.price['home_value'] + self.price['loan_fees']
        
        self.mort = Mortgage(self.exponent['yearly_interest'], self.price['mortgage'])
        self.price['monthly_PI'] = self.mort.monthly_PI
        # self.price['monthly_PI'] = monthly_PI(self.exponent['yearly_interest'], 30, self.price['mortgage'])
        self.price['monthly_OpEx'] = self.sum_opex()
        self.price['monthly_expenses'] = self.price['monthly_OpEx'] + self.price['monthly_PI']
        self.price['monthly_cashflow'] = self.price['monthly_rent'] - self.price['monthly_expenses']
        self.price['NOI'] = (self.price['monthly_cashflow'] + self.price['monthly_PI']) * yearly_months  # googled NOI vs cash flow

    def sum_opex(self):
        exp_sum = self.price['monthly_vacancy'] + self.price['monthly_capex'] \
        + self.price['owning_expenses'] + self.price['monthly_repairs'] #+ self.price['monthly_PI']
        return exp_sum
    
    def __str__(self):
        return (
            "\nRefinance:\n"
            f"Loan Amount: ${self.price['mortgage']}\n"
            f"Loan Points/Fees: ${self.price['loan_fees']}\n"
            f"Loan Interest Rate: {self.exponent['yearly_interest']*100}%\n"
            f"Monthly P&I: ${self.price['monthly_PI']:.2f}\n"
            f"Home Value Appreciaion: {self.exponent['yearly_val_apprec']*100}%"
        )