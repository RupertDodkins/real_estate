import pandas as pd
import numpy as np

from real_estate import mortgage
from real_estate.metadata import Acquisition, Rehab, PreReFi_Rent, Refinance
from real_estate.aggregate import YearlySummary, stocks_rent_performance
from real_estate.plots import plot_timeseries
from real_estate.constants import yearly_months


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
    refi_loan_frac = 0.8,
    title=''
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
        owning_expenses=acq.price['owning_expenses'],
        loan_frac=refi_loan_frac
        )
    
    print(str(acq))
    print(str(rehab))
    print(str(pre_refi))
    print(str(refi))

    year_sum = YearlySummary(acq, rehab, pre_refi, refi, 30)
    print(year_sum.cash_required)
    realestate_df = year_sum.to_dataframe()

    stocks_df = stocks_rent_performance(0, 30, year_sum.cash_required)

    plot_timeseries([('Property Value', 'Stock Value'),  
                     'Return on Initial Investment', 
                     'Total Annual Cashflow'], 
                     realestate_df, stocks_df, title=title)

    return realestate_df, stocks_df