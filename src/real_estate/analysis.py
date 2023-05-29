import pandas as pd
import numpy as np

from real_estate import mortgage
from real_estate.metadata import Acquisition, Rehab, PreReFi_Rent, Refinance
from real_estate.aggregate import YearlySummary
from real_estate.plots import plot_timeseries

def generate_stock_performance(start_year, end_year, start_value=100, annual_return=0.08):
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
    years = np.arange(start_year, end_year + 1)
    values = start_value * np.power(1 + annual_return, years - start_year)
    df = pd.DataFrame({'Year': years, 'Value': values})
    df['Return on Initial Investment'] = df['Value']/df.iloc[0]['Value']

    return df 


def property_performance(
    # purchase
    purchase_price = 200e3,
    downpayment = 20e3,
    rehab_cost = 25e3,
    after_repair_value = 225e3,
    value_appreciation = 0.06,
    rent_appreciation = 0.03,
    opex_inflation = 0.03,

    # acquisition
    acq_yearly_interest = 0.065,
    mortgage_years = 30,
    rehab_months = 6,
    yearly_taxes = 2140,
    yearly_insurance = 70,

    # initial rental period
    monthly_rent = 3e3,
    vacancy_frac = 0.05,
    repairs_frac = 0.05,
    capex_frac = 0.05,

    # refinanced rental period 
    ref_yearly_interest = 0.065,
    refinance_months = 9,
    
):
    pre_refi_duration = refinance_months-rehab_months
    acq = Acquisition(
        purchase_price=purchase_price, 
        downpayment=downpayment, 
        yearly_interest=acq_yearly_interest, 
        value_appreciation=value_appreciation, 
        yearly_taxes=yearly_taxes,
        yearly_insurance=yearly_insurance
        )
    rehab = Rehab(
        rehab_months=rehab_months, 
        total_cost=rehab_cost, 
        monthly_PI=acq.price['monthly_PI'], 
        owning_expenses=acq.price['owning_expenses']
        )
    pre_refi = PreReFi_Rent(
        monthly_rent=monthly_rent, 
        vacancy_frac=vacancy_frac, 
        repairs_frac=repairs_frac, 
        capex_frac=capex_frac,
        total_time=pre_refi_duration, 
        monthly_PI=acq.price['monthly_PI'], 
        rent_appreciation=rent_appreciation, 
        opex_inflation=opex_inflation, 
        owning_expenses=acq.price['owning_expenses']
        )
    refi = Refinance(
        monthly_rent=monthly_rent, 
        home_value=after_repair_value, 
        vacancy_frac=vacancy_frac, 
        repairs_frac=repairs_frac, 
        capex_frac=capex_frac, 
        refinance_months=refinance_months, 
        yearly_interest=ref_yearly_interest, 
        value_appreciation=value_appreciation,
        rent_appreciation=rent_appreciation, 
        opex_inflation=opex_inflation, 
        owning_expenses=acq.price['owning_expenses']
        )
    
    print(str(acq))
    print(str(rehab))
    print(str(pre_refi))
    print(str(refi))

    year_sum = YearlySummary(acq, rehab, pre_refi, refi, 30)
    print(year_sum.cash_required)
    df = year_sum.to_dataframe()

    stocks_df = generate_stock_performance(0, 30, year_sum.cash_required)

    metric = 'Return on Initial Investment'
    plot_timeseries(stocks_df[metric], 
                    df[metric], 
                    ['S&P', 'Real Estate', metric])
    return df