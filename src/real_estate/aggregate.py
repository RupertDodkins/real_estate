import pandas as pd
import numpy as np
from IPython.display import display

from real_estate.constants import yearly_months


def format_with_sig_figs(x):
    if x == 0:
        return "0"
    else:
        return "{:,.2f}".format(round(x, 2 - int(np.floor(np.log10(abs(x))))))

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

        print(f'\nInitial real estate cash required {self.cash_required}')
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
            
            annual_data['Loan Balance'] = self.acq.mort.df.iloc[year]['Remaining Balance'] 
            annual_data['Equity'] = annual_data['Property Value'] - annual_data['Loan Balance']

            if year == 0:
                equity_gain = annual_data['Equity'] - self.cash_required
            else:
                equity_gain = annual_data['Equity'] - data[year-1]['Equity']
            
            annual_data['Equity Gain'] = equity_gain
            annual_data['Annual Profit'] = annual_data['Equity Gain'] + annual_data['Total Annual Cashflow']

            if year == 0:
                annual_data['Return on Equity'] = annual_data['Annual Profit'] / self.cash_required
            else:
                annual_data['Return on Equity'] = annual_data['Annual Profit'] / data[year-1]['Equity']

            annual_data['Cummulative Profit'] = np.sum([d['Annual Profit'] for d in data]) + annual_data['Annual Profit']
            annual_data['Return on Initial Investment'] = annual_data['Cummulative Profit'] / self.cash_required

            data.append(annual_data)

        return data

    def to_dataframe(self):
        data = self.calculate_annual_data()
        columns = data[0].keys()
        df = pd.DataFrame(data, columns=columns)
        df.style.set_table_styles([dict(selector="th",props=[('max-width', '50px')])])
        pretty_df = df.applymap(format_with_sig_figs)
        print('Real Estate Performance')
        display(pretty_df.head())

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
        pre_refi_opex = self.pre_refi.price['monthly_OpEx'] * self.pre_refi_months[year] * (1+self.pre_refi.exponent['yearly_opex_inflation'])**year
        refi_opex = self.refi.price['monthly_OpEx'] * self.refi_months[year] * (1+self.refi.exponent['yearly_opex_inflation'])**year
        return pre_refi_opex + refi_opex


def stocks_rent_performance(margi, rent, total_years=30):
    """
    Function to generate a pandas DataFrame for a timeseries of stock performance.

    Args:
        start_year: The year to start the simulation.
        end_year: The year to end the simulation.
        start_value: The starting value of the stock. Defaults to 100.
        annual_return: The annual return rate. Defaults to 0.08 (8%).

    Returns:
        A pandas DataFrame with columns 'Year' and 'Value' representing the stock value for each year.
    """
    years = np.arange(total_years)
    df = pd.DataFrame(
        {
        'Year': years, 
        # 'Return on Initial Investment': df['Value']/df.iloc[0]['Value'],
        'Total Annual Income': 0,
        'Operating Expenses': rent.price['monthly_opex'] * yearly_months * np.power(1 + rent.exponent['opex_inflation'], years),
        'Rent Payment': rent.price['monthly_rent'] * yearly_months * np.power(1 + rent.exponent['rent_appreciation'], years),
        'Total Annual Expenses': 0,
        'Total Annual Cashflow': 0,
        'Cash on Cash ROI': 0,
        'Stock Value':  margi.price['stock_value'] * np.power(1 + margi.exponent['yearly_val_apprec'], years),
        'Loan Balance': margi.mort.df['Remaining Balance'],
        'Equity': 0,
        'Equity Gain': 0,
        'Annual Profit': 0,
        'Return on Equity': 0,
        'Cummulative Profit': 0,
        'Return on Initial Investment': 0
        }
    )
    df['Total Annual Expenses'] = df['Operating Expenses'] + df['Rent Payment']
    df['Total Annual Cashflow'] = df['Total Annual Income'] - df['Total Annual Expenses']
    df['Cash on Cash ROI'] = df['Total Annual Cashflow'] / margi.price['downpayment']
    df['Equity'] = df['Stock Value'] - df['Loan Balance']
    df['Equity Gain']= df['Equity'].diff()
    df.at[0, 'Equity Gain'] = df.iloc[0]['Equity'] - margi.price['downpayment']
    df['Annual Profit'] = df['Equity Gain'] + df['Total Annual Cashflow']
    df['Return on Equity']= df['Annual Profit'] / np.roll(df['Equity'], 1)
    df.at[0, 'Return on Equity'] = df.iloc[0]['Annual Profit'] /margi.price['downpayment']
    df['Cummulative Profit'] = df['Annual Profit'].cumsum()
    df['Return on Initial Investment'] = df['Cummulative Profit'] / margi.price['downpayment']

    pretty_df = df.applymap(format_with_sig_figs)
    print('Stock Performance')
    display(pretty_df.head())

    return df 