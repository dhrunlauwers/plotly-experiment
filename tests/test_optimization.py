import sys
import pytest
import numpy as np
import pandas as pd

module_path = '../'
if module_path not in sys.path: sys.path.append(module_path)

from src.optimization import optimize_portfolio, calc_portfolio

class TestCalcPortfolio(object):
    """
    To test whether calc_portfolio function returns minimum variance portfolio
    as shown in the following example (See page 9).
    
    https://faculty.washington.edu/ezivot/econ424/portfolioTheoryMatrix.pdf
    """

    def test_on_three_assets(self):
        """
        Simple example with three assets.
        """

        # Test Arguments
        test_argument_r = np.matrix([[0.0427], [0.0015], [0.0285]])
        test_argument_C = np.matrix([[0.0100, 0.0018, 0.0011],
                                    [0.0018, 0.0109, 0.0026],
                                    [0.0011, 0.0026, 0.0199]])
        test_argument_expected_return = 0.02489

        # Expected Results
        expected_mu = test_argument_expected_return
        expected_w0 = 0.4411
        expected_w1 = 0.3657
        expected_w2 = 0.1933
        expected_std_dev = 0.07268
        expected_tot_var = 0.005282

        # Actual results
        actual_result = calc_portfolio(test_argument_expected_return, test_argument_r, test_argument_C)

        # Assert all answers are correct
        assert actual_result['mu'] == expected_mu
        assert round(actual_result['w0'],4) == expected_w0
        assert round(actual_result['w1'],4) == expected_w1
        assert round(actual_result['w2'],4) == expected_w2
        assert round(actual_result['std_dev'],5) == expected_std_dev
        assert round(actual_result['tot_var'],6) == expected_tot_var



