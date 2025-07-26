import pandas as pd
import matplotlib.pyplot as plt
from viz_ops import plot_time_series


class TestPlotTimeSeries:

    # plot multiple columns from a DataFrame with a DateTime index
    def test_plot_multiple_columns_with_datetime_index(self):

        # Create a sample DataFrame with DateTime index and multiple columns
        dates = pd.date_range("20230101", periods=6)
        data = {"A": [1, 2, 3, 4, 5, 6], "B": [2, 3, 4, 5, 6, 7]}
        df = pd.DataFrame(data, index=dates)

        # Plot the time series
        plot_time_series(df)

        # Check if the plot was created (this is a basic check)
        assert plt.gcf().number == 1
