import sys

sys.path.insert(1, "algorithmic_trading_utilities")
from common.quantitative_tools import remove_highly_correlated_columns


class TestRemoveHighlyCorrelatedColumns:

    # removes columns with correlation above threshold
    def test_removes_highly_correlated_columns(self):
        import pandas as pd

        data = {"A": [1, 2, 3, 4, 5], "B": [2, 3, 4, 5, 6], "C": [0, 5, 1, 3, 6]}
        df = pd.DataFrame(data)
        threshold = 0.9

        result_df = remove_highly_correlated_columns(df, threshold)

        assert "A" not in result_df.columns
        assert "B" in result_df.columns
        assert "C" in result_df.columns
