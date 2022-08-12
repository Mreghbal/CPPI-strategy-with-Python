##############################################################################################################

import pandas as pd
import numpy as np

##############################################################################################################

def cppi_running(risky_returns, safe_returns = None, multiplier = 3, start = 1000,
                floor_rate = 0.8, riskfree_rate = 0.03, drawdown = None):
    """
    Run a backtest of the CPPI strategy:

    1- CPPI stands for constant proportion portfolio insurance.
    
    2- Adjust a set of returns for the risky asset.

    3- You can change the values of "cppi_running" function arguments.

    Returns a dictionary containing: Asset Value History, Risk Budget History, Risky Weight History
    """

##################################### Set up the CPPI parameters ############################################

    dates = risky_returns.index
    number_of_steps = len(dates)
    account_value = start
    floor_value = start * floor_rate
    peak = account_value

    if isinstance(risky_returns, pd.Series): 
        risky_returns = pd.DataFrame(risky_returns, columns = ["R"])

    if safe_returns is None:
        safe_returns = pd.DataFrame().reindex_like(risky_returns)
        safe_returns.values[:] = riskfree_rate / 12

########################### Set up some DataFrames for saving intermediate values ###########################

    for step in range(number_of_steps):

        if drawdown is not None:
            peak = np.maximum(peak, account_value)
            floor_value = peak * (1 - drawdown)

        cushion = (account_value - floor_value) / account_value
        risky_weight = multiplier * cushion
        risky_weight = np.minimum(risky_weight, 1)
        risky_weight = np.maximum(risky_weight, 0)
        safe_weight = 1 - risky_weight
        risky_allocation = account_value * risky_weight
        safe_allocation = account_value * safe_weight
        account_value = risky_allocation * (1 + risky_returns.iloc[step]) + safe_allocation * (1 + safe_returns.iloc[step])
        cushion_history.iloc[step] = cushion
        risky_weight_history.iloc[step] = risky_weight
        account_history.iloc[step] = account_value
        floorval_history.iloc[step] = floor_value
        peak_history.iloc[step] = peak
    
    risky_wealth = start * (1 + risky_returns).cumprod()

    account_history = pd.DataFrame().reindex_like(risky_returns)
    risky_weight_history = pd.DataFrame().reindex_like(risky_returns)
    cushion_history = pd.DataFrame().reindex_like(risky_returns)
    floorval_history = pd.DataFrame().reindex_like(risky_returns)
    peak_history = pd.DataFrame().reindex_like(risky_returns)
    
################################ Save the histories for analysis and plotting ###############################

    backtest_result = {"Wealth ": account_history,
                       "Risky Wealth ": risky_wealth, 
                       "Risk Budget ": cushion_history,
                       "Risky Allocation ": risky_weight_history,
                       "Multiplier ": multiplier,
                       "Start Value ": start,
                       "Floor Value Rate ": floor_rate,
                       "Risky_returns ":risky_returns,
                       "Safe_returns ": safe_returns,
                       "Drawdown ": drawdown,
                       "Peak History ": peak_history,
                       "Floor History ": floorval_history}
    return backtest_result