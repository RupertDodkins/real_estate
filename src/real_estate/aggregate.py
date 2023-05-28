import pandas as pd
import numpy as np
from IPython.display import display, HTML

from real_estate.constants import yearly_months

class YearlySummary:
    def __init__(self, acq, rehab, pre_refi, refi, total_years):
        self.acq = acq
        self.rehab = rehab
        self.pre_refi = pre_refi
        self.refi = refi
        self.total_years = total_years
        self.cash_required = self.acq.price['downpayment'] + self.rehab.price['total_cost'] + self.acq.price['closing']
        
        self.rehab_months = self.applicable_months_per_year(self.rehab.time['total_months'], total_years)
        self.rental_months = 12 - self.rehab_months
        self.acq_months = self.applicable_months_per_year(self.refi.time['total_months'], total_years)
        self.refi_months = 12 - self.acq_months
        self.pre_refi_months = self.applicable_months_per_year(self.pre_refi.time['total_months'], total_years) #- self.rehab_months

    def calculate_annual_data(self):
        data = []
        for year in range(0, self.total_years):
            annual_data = {}
            annual_data['Year'] = year
            annual_data['Month'] = year * yearly_months
            annual_data['Renting Months'] = self.rental_months[year]
            annual_data['Total Annual Income'] = self.pre_refi.price['monthly_rent']*(1+self.pre_refi.exponent['yearly_rent_apprec'])**year * annual_data['Renting Months']
            
            annual_data['Operating Expenses'] = self.operating_expenses(year)
            annual_data['Mortgage Payment'] = self.acq.price['monthly_PI'] * self.acq_months[year] + self.refi.price['monthly_PI'] * self.refi_months[year]
            annual_data['Total Annual Expenses'] = annual_data['Operating Expenses'] + annual_data['Mortgage Payment'] + self.rehab.price['total_cost'] * self.rehab_months[year]/self.rehab.time['total_months']
            
            annual_data['Total Annual Cashflow'] = annual_data['Total Annual Income'] - annual_data['Total Annual Expenses']
            annual_data['Cash on Cash ROI'] = annual_data['Total Annual Cashflow'] / self.cash_required
            annual_data['Property Value'] = self.property_value(year)
            
            annual_data['Loan Balance'] = self.acq.mort.df.iloc[year]['Remaining Balance']  # this is a simplification, in reality you would need to calculate this based on the amortization schedule of the loan
            annual_data['Equity'] = annual_data['Property Value'] - annual_data['Loan Balance']

            if year == 0:
                equity_gain = annual_data['Equity']
            else:
                equity_gain = annual_data['Equity'] - data[year-1]['Equity']
            
            annual_data['Equity Gain'] = equity_gain
            annual_data['Annual Profit'] = annual_data['Equity Gain'] + annual_data['Total Annual Cashflow']
            annual_data['Annualized Total Return'] = (annual_data['Annual Profit'] / self.cash_required)

            data.append(annual_data)

        return data

    def to_dataframe(self):
        data = self.calculate_annual_data()
        columns = data[0].keys()
        df = pd.DataFrame(data, columns=columns)
        df.style.set_table_styles([dict(selector="th",props=[('max-width', '50px')])])
        pretty_df = df.applymap(self.format_with_sig_figs)
        display(pretty_df)

        return df
    
    def applicable_months_per_year(self, total_months, total_years):
        rental_months = []
        for year in range(1, total_years + 1):
            if total_months >= 12:
                rental_months.append(12)
                total_months -= 12
            elif total_months > 0:
                rental_months.append(total_months)
                total_months = 0
            else:
                rental_months.append(0)
        return np.array(rental_months)
    
    def property_value(self, year):
        acq_period_value = (self.acq.price['home_value']*(1+self.acq.exponent['yearly_val_apprec'])**year + self.rehab.price['total_cost'])*self.acq_months[year]/12 
        ref_period_value = self.refi.price['home_value']*(1+self.refi.exponent['yearly_val_apprec'])**year *self.refi_months[year]/12
        return acq_period_value + ref_period_value
    
    def operating_expenses(self, year):
        pre_refi_opex = self.pre_refi.price['monthly_OpEx'] * self.pre_refi_months[year] * (1+self.pre_refi.exponent['yearly_rent_apprec'])**year
        refi_opex = self.refi.price['monthly_OpEx'] * self.refi_months[year] * (1+self.refi.exponent['yearly_rent_apprec'])**year
        return pre_refi_opex + refi_opex

    def format_with_sig_figs(self, x):
        if x == 0:
            return "0"
        else:
            return "{:,.2f}".format(round(x, 2 - int(np.floor(np.log10(abs(x))))))
