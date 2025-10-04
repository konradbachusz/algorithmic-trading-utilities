# Benchmark Interpretation

This document explains each portfolio and risk metric from the `PerformanceMetrics` module and how to interpret it. Designed for users with varying levels of quantitative or algorithmic trading experience.

## Alpha (α)

**Definition:** Measures how much your portfolio outperforms (or underperforms) the benchmark after adjusting for market risk.  
**Interpretation:**  

- **α > 0** → Portfolio added value beyond the benchmark.  
- **α ≈ 0** → Portfolio performed like the benchmark.  
- **α < 0** → Portfolio underperformed relative to the benchmark.  

## Beta (β)

**Definition:** Measures portfolio sensitivity to market movements (systematic risk).  
**Interpretation:**  

- **β = 1** → Moves in line with the market.  
- **β < 1** → Less volatile than the market.  
- **β > 1** → More volatile than the market.  
- **β < 0** → Moves opposite to the market.  

## Sharpe Ratio

**Definition:** Reward per unit of total risk (volatility).  
**Interpretation:** (For an annualized Sharpe Ratio)

- **< 1** → Low risk-adjusted returns.  
- **1 – 2** → Good performance.  
- **2 – 3** → Very good.  
- **> 3** → Excellent.  

## Sortino Ratio

**Definition:** Reward per unit of downside risk only.  
**Interpretation:**  

- Focuses on bad (downside) volatility, ignoring upside swings. Higher is better.  
- **Magnitude guidelines:**  
  - **< 1** → Poor risk-adjusted performance relative to downside risk.  
  - **1 – 2** → Acceptable. Portfolio manages downside reasonably.  
  - **2 – 3** → Good. Portfolio captures upside well while limiting losses.  
  - **> 3** → Excellent. Portfolio efficiently maximizes returns with minimal downside.  

## Total Return

**Definition:** Overall growth of the portfolio over the period.  
**Interpretation:**  

- Positive → Portfolio value increased.  
- Negative → Portfolio lost value.  

## Maximum Drawdown (Max DD)

**Definition:** Largest peak-to-trough equity value loss.  
**Interpretation:**  

- Smaller is better; large values indicate high potential greater loss risk.  

## Average Drawdown

**Definition:** Mean of all drawdowns over the period.  
**Interpretation:**  

- Shows typical loss during downturns. Lower is better.  

## Drawdown Duration

**Definition:** Longest period the portfolio stayed below its previous peak.  
**Interpretation:**  

- Short → Quick recovery.  
- Long → Prolonged losses, higher stress.  
- **Example:** If your portfolio peak was on Jan 1 at \$100, fell to \$80 on Feb 1, and recovered back to \$100 by Mar 1, the drawdown duration is 2 months (Feb 1 → Mar 1).  

## Volatility

**Definition:** Standard deviation of daily returns; measures total risk.  
**Interpretation:**  

- High → Portfolio swings widely.  
- Low → Stable returns.  
- **Magnitude guidelines / intuitive example:**  
  - Daily volatility of 1% → moderate fluctuations; losing \$1 on \$100 is common.  
  - Daily volatility of 3% → aggressive swings; losing \$3 on \$100 is typical.  
  - Annualized volatility ≈ daily volatility × √252.  
  - Helps compare “smoothness” of different portfolios.  

## Value at Risk (VaR)

**Definition:** Maximum expected loss at a given confidence level.  
**Interpretation:**  

- **VaR = -5% at 95% confidence** → 5% chance of losing more than 5% of equity value on any day.  

## Conditional Value at Risk (CVaR)

**Definition:** Average equity value loss beyond the VaR threshold.  
**Interpretation:**  

- Captures tail risk; higher CVaR → worse extreme losses.  
- **Magnitude guidelines / intuitive example:**  
  - 95% CVaR of -8% → If the worst 5% of days occur, the average loss is 8% of the portfolio.  
  - Useful for understanding extreme risk exposure, beyond just the maximum expected loss (VaR).  

## Skewness

**Definition:** Measures asymmetry of returns distribution.  
**Interpretation:**  

- **Positive** → More frequent small losses, rare large gains.  
- **Negative** → More frequent small gains, rare large losses.  

## Kurtosis

**Definition:** Measures “tailedness” of returns distribution.  
**Interpretation:**  

- High → Extreme returns more likely than normal.  
- Low → Returns cluster near the mean.  
- **Magnitude / intuitive example:**  
  - Kurtosis ≈ 3 → Close to normal distribution; typical fluctuations dominate.  
  - Kurtosis > 5 → “Fat tails”; more extreme losses or gains than expected.  
  - Helps assess risk of rare but large events.  

## Calmar Ratio

**Definition:** Annualized return divided by max drawdown.  
**Interpretation:**  

- Higher → Better risk-adjusted performance relative to drawdown.  
- **Magnitude guidelines / intuitive example:**  
  - Calmar Ratio < 0.5 → Portfolio returns are low compared to drawdown risk.  
  - 0.5 – 1 → Moderate; reasonable balance of risk and reward.  
  - 1 – 2 → Good; strong returns relative to risk.  
  - \> 2 → Excellent; portfolio achieves high return with relatively small drawdowns.  
