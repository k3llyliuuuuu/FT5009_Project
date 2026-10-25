# FT5009 Member 3

Risk analysis (Part 5) for Smart Retail Flow FT5009, Smart Insti Flow FT5009 and the enhanced institutional strategy. Inputs are Member 2's `results/` and `results/risk_handoff/`; upstream files are never modified. Results are written to `results/`.

## Run

From the repository root, with Python 3.12 and Member 2's locked dependencies:

```bash
python -m pip install -r "member 2/requirements-lock.txt"
python "member 3/volatility.py"
python "member 3/rolling_volatility.py"
python "member 3/var.py"
python "member 3/var_plot.py"
python "member 3/var_stats.py"
```

Run `var.py` before `var_plot.py` and `var_stats.py`, which read its output. The pipeline runs offline in about 30 seconds.

| Script | Purpose | Part |
|---|---|---|
| `volatility.py` | Annualised realised volatility | 5a |
| `rolling_volatility.py` | Rolling 21-trading-day volatility and figure | 5a |
| `var.py` | Daily one-day 99% historical-simulation VaR | 5b |
| `var_plot.py` | VaR figures | 5b |
| `var_stats.py` | Coverage-gap and VaR-exception statistics | 5b |

## Methods

- **Volatility.** Sample standard deviation (ddof 1) of daily net returns × √252. The rolling measure uses the latest 21 net returns, ending on day t.
- **VaR.** For each session t from 2 January 2019 to 30 September 2026:
  - Take the signed end-of-day weights at the previous close t−1 (long positive, short negative; cash carries no market risk).
  - Apply them to exactly 500 aligned daily asset returns ending at t−1, which gives 500 simulated portfolio returns. The first window starts on 4 January 2017, so pre-2019 prices fill the initial window.
  - VaR (%) is minus the 5th worst simulated return, i.e. the empirical 1% quantile without interpolation.
  - Dollar VaR = VaR (%) × net NAV at the previous close.
  - Only information available at the previous close is used.
- **Coverage gaps.** If any held security lacks one of its 500 returns, the date has no forecast (`missing_return`) and the responsible securities are listed. Dates are never dropped, missing returns are never filled with zero and the window is never shortened. All-cash dates have zero VaR (`cash_only`).
- **Exceptions.** An exception is a realised net loss larger than VaR, counted on dates with a complete forecast only. Kupiec's test checks whether the exception rate is consistent with 1%; Christoffersen's test checks whether exceptions cluster. Both are reported for the full period and Member 2's three subperiods.

## Outputs

| File | Contents |
|---|---|
| `results/annualised_volatility.csv` | Daily and annualised realised volatility per strategy |
| `results/rolling_volatility.csv` | Daily rolling 21-day annualised volatility |
| `results/var_forecasts.csv` | One row per strategy and date: origin date, previous NAV, holdings count, status, VaR % and S$, realised net return, missing securities |
| `results/var_summary.csv` | Coverage, expected and actual exceptions, Kupiec and Christoffersen tests by strategy and period |
| `results/coverage_gap_episodes.csv` | Consecutive gap sessions and the securities responsible |
| `results/figures/rolling_volatility.*` | Rolling 21-day volatility of the three strategies |
| `results/figures/var_forecasts_pct.*` | Realised net returns, −VaR, exceptions and shaded gap sessions |
| `results/figures/var_forecasts_sgd.*` | Dollar VaR of the three strategies |

## Notes and limitations

- Realised net returns include transaction costs and borrow on rebalance days, whereas VaR measures market risk on the held positions only. The exception count is therefore slightly overstated.
- Every coverage gap comes from the 29 unverified extreme returns that Member 1 quarantined in `asset_returns_for_var.csv.gz`. Read Member 1's `REQUIREMENTS_AUDIT.md` before interpreting the results; its data limitations apply to every risk figure.
- Historical simulation adapts slowly to new regimes, and the 99% quantile rests on five observations.
- Rerunning the scripts rewrites the PDF figures with a new creation timestamp, so Git may show them as modified even though their content is unchanged.
