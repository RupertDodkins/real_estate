import pandas as pd
import numpy as np

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