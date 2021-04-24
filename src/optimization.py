
import numpy as np
import pandas as pd
import os

# define some functions
def calc_portfolio(mu, expected_return, cov_matrix):
    """
    Uses Markowitz portfolio optimization to calculate asset 
    allocation for lowest risk (AKA minimum variance) portfolio 
    given the following variables:
    - a target level of return (mu),
    - a vector of expected returns for available assets (expected_return)
    - a covariance matrix of returns for available assets (cov_matrix)

    Also calculates the total variance and standard deviation for each portfolio.
    """

    # calculate asset allocation
    ones = np.matrix([[1] for item in expected_return])
    x1 = calc_x1(expected_return, cov_matrix, ones)
    x2 = calc_x2(expected_return, cov_matrix)
    x3 = calc_x3(expected_return, cov_matrix, ones)
    lambda1 = calc_lambda1(x1, x2, x3, mu)
    lambda2 = calc_lambda2(x1, x2, x3, mu)
    weights = calc_weights(cov_matrix, lambda1, lambda2, expected_return, ones)

    # add results to dictionary object 
    portfolio_details = {}
    portfolio_details['mu'] = mu
    
    # capture all weights, no matter how many assets
    for i, val in enumerate(weights):
        portfolio_details["w%s" % i] = val[0,0]

    # calculate portfolio variance and standard deviation
    portfolio_details['tot_var'] = (weights.T * cov_matrix * weights)[0,0]
    portfolio_details['std_dev'] = np.sqrt(portfolio_details['tot_var'])

    return portfolio_details

def calc_x1(expected_return, cov_matrix, ones):
    return expected_return.T * cov_matrix.I * ones

def calc_x2(expected_return, cov_matrix):
    return expected_return.T * cov_matrix.I * expected_return

def calc_x3(expected_return, cov_matrix, ones):
    return ones.T * cov_matrix.I * ones

def calc_lambda1(x1, x2, x3, mu):
    return (x3 * mu - x1) / (x2 * x3 - np.square(x1))

def calc_lambda2(x1, x2, x3, mu):
    return (x2 - x1 * mu) / (x2 * x3 - np.square(x1))

def calc_weights(cov_matrix, lambda1, lambda2, expected_return, ones):
    return cov_matrix.I * (lambda1[0,0] * expected_return + lambda2[0,0] * ones)

def optimize_portfolio(returns_vector, mu, C, assets):
    """
    Constructs the minimum variance portfolio for each level of target 
    return in the returns vector using the list of asssets provided
    based on the expected return of each asset and their covariance matrix.
    """

    results = pd.DataFrame()

    r_sub = np.matrix([[r] for r in mu[assets]])
    C_sub = np.matrix(C.loc[assets, assets])

    for target_return in returns_vector:
        min_var_portfolio = calc_portfolio(target_return, r_sub, C_sub)
        results = results.append(min_var_portfolio, ignore_index=True)
    
    return results
