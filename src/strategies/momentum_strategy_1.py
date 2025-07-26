import yfinance as yf
import pandas as pd


def get_upward_trending_assets(asset_list, lookback_period=14, threshold=0.05):
    """
    Identify assets in an upward trend based on momentum.

    Parameters:
        asset_list (list): List of asset symbols to analyze.
        lookback_period (int): Number of days to calculate momentum.
        threshold (float): Minimum momentum percentage for upward trend.

    Returns:
        list: Assets in an upward trend.
    """
    upward_trending_assets = []

    for symbol in asset_list:
        try:
            data = yf.download(symbol, period=f"{lookback_period + 1}d", interval="1d")
            if data.empty or len(data) < lookback_period:
                continue

            # Calculate momentum as percentage change over the lookback period
            momentum = (data["Close"].iloc[-1] - data["Close"].iloc[0]) / data[
                "Close"
            ].iloc[0]

            if momentum >= threshold:
                upward_trending_assets.append(
                    {
                        "symbol": symbol,
                        "momentum": momentum,
                        "side": "buy",  # For upward trend, we buy
                        "type": "market",
                        "time_in_force": "gtc",
                    }
                )
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    return upward_trending_assets


def get_downward_trending_assets(asset_list, lookback_period=14, threshold=-0.05):
    """
    Identify assets in a downward trend based on momentum.

    Parameters:
        asset_list (list): List of asset symbols to analyze.
        lookback_period (int): Number of days to calculate momentum.
        threshold (float): Maximum momentum percentage for downward trend.

    Returns:
        list: Assets in a downward trend.
    """
    downward_trending_assets = []

    for symbol in asset_list:
        try:
            data = yf.download(symbol, period=f"{lookback_period + 1}d", interval="1d")
            if data.empty or len(data) < lookback_period:
                continue

            # Calculate momentum as percentage change over the lookback period
            momentum = (data["Close"].iloc[-1] - data["Close"].iloc[0]) / data[
                "Close"
            ].iloc[0]

            if momentum <= threshold:
                downward_trending_assets.append(
                    {
                        "symbol": symbol,
                        "momentum": momentum,
                        "side": "sell",  # For downward trend, we sell
                        "type": "market",
                        "time_in_force": "gtc",
                    }
                )
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    return downward_trending_assets


# Example usage
if __name__ == "__main__":
    # Replace with a list of tradable asset symbols
    tradable_assets = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

    upward_trends = get_upward_trending_assets(tradable_assets)
    downward_trends = get_downward_trending_assets(tradable_assets)

    print("Upward Trending Assets:")
    print(upward_trends)

    print("\nDownward Trending Assets:")
    print(downward_trends)

    # Example: Pass the results to the place_order function
    # for asset in upward_trends:
    #     place_order(asset["symbol"], quantity, asset["side"], asset["type"], asset["time_in_force"])
