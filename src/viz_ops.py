import matplotlib.pyplot as plt


def plot_time_series(df):
    # Visualize df as a time series line graph

    # Select the columns you want to plot
    columns_to_plot = df.columns.tolist()  # Replace with your desired columns

    # Create the line plot
    plt.figure(figsize=(12, 6))  # Adjust figure size as needed
    for column in columns_to_plot:
        plt.plot(df.index, df[column], label=column)

    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title("Time Series Line Graph")
    plt.legend()
    plt.grid(True)
    plt.show()


# TODO unit test
def compare_portfolio_and_benchmark(df, title):
    """
    Plots a simple time series line chart for each column in the given DataFrame.
    Parameters:
        df (pd.DataFrame): DataFrame with a datetime-like index and one or more columns to plot.
        title (str): Title of the plot.
    Displays:
        A matplotlib plot showing each column of the DataFrame as a separate line, with legend, grid, and axis labels.
    """

    plt.figure(figsize=(12, 6))
    for column in df.columns:
        plt.plot(df.index, df[column], label=column)
    plt.xlabel("Date")
    if len(df.columns) == 1:
        plt.ylabel(df.columns[0])
    else:
        plt.ylabel("Returns")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()
