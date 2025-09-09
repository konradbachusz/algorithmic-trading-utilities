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
**Interpretation:**  

- **< 1** → Low risk-adjusted returns.  
- **1 – 2** → Good performance.  
- **2 – 3** → Very good.  
- **> 3** → Excellent.  

## Sortino Ratio

**Definition:** Reward per unit of downside risk only.  
**Interpretation:**  

- Focuses on bad (downside) volatility, ignoring upside swings. Higher is better.  

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

## Volatility / Std Dev

**Definition:** Standard deviation of daily returns; measures total risk.  
**Interpretation:**  

- High → Portfolio swings widely.  
- Low → Stable returns.  

## Value at Risk (VaR)

**Definition:** Maximum expected loss at a given confidence level.  
**Interpretation:**  

- **VaR = -5% at 95% confidence** → 5% chance of losing more than 5% of equity value on any day.  

## Conditional Value at Risk (CVaR)

**Definition:** Average equity value loss beyond the VaR threshold.  
**Interpretation:**  

- Captures tail risk; higher CVaR → worse extreme losses.  

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

## Calmar Ratio

**Definition:** Annualized return divided by max drawdown.  
**Interpretation:**  

- Higher → Better risk-adjusted performance relative to drawdown.  
