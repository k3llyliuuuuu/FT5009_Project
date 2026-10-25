# FT5009 Group Project (Project Group 1)

This project compares the trading signals in institutional and retail investors' weekly SGX fund flows. It collects the SGX Weekly Top 10 fund-flow reports released from January 2019 to September 2026, backtests long/short strategies that follow each investor group, enhances the institutional strategy with a trend filter, and evaluates performance, trading feasibility and risk.

## Reproduce all results

From this folder, with Python 3.12, preferably in a fresh virtual environment:

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
python -m pip install -r requirements.txt
python run_all.py
```

Use the locked versions in `requirements.txt`; the code is not compatible with pandas 3.

`run_all.py` runs offline and executes the following steps in order, each starting once the previous step has completed successfully:

1. `member 2/run_member2.py` rebuilds Member 1's source extraction, market inputs, baseline backtests, tests and audit in an isolated copy under `member 2/work/`, so `member 1/` is never rewritten. It then runs the enhancement, all nine strategy/cost paths, the evaluation and the Member 2 tests, and writes the risk handoff.
2. The five Member 3 scripts compute volatility and VaR from Member 2's results.

A full run takes about two minutes. Later runs reuse Member 2's verified copy of Member 1's inputs while Member 1's files are unchanged. Options:

- `python run_all.py --rebuild-inputs` forces a fresh reconstruction of Member 1's inputs.
- `python run_all.py --member3-only` reruns Part 5 from Member 2's existing results (about 30 seconds).

Each member folder can also be run on its own; see its README.

Reproduction was verified with Python 3.12 and the locked packages: every CSV result matched the submitted files. After a rerun, some compressed CSVs, figures and checksum files may differ byte-for-byte because of platform line endings and file metadata; their content is unchanged.

## Project structure

| Location | Parts | Contents |
|---|---|---|
| `member 1/` | 1–2 | SGX report collection and parsing (`01_SGX_Flow_Collection/`); daily prices, benchmark, eligibility rules, backtesting engine and the retail and institutional baselines (`02_Baseline_Backtesting/`) |
| `member 2/` | 3–4 | 126-day SMA trend-confirmation enhancement; performance, subperiod, cost and liquidity evaluation; risk handoff |
| `member 3/` | 5 | Realised and rolling volatility; 99% historical-simulation VaR, coverage gaps and VaR backtests |
| Project root | 6 | Final report; `run_all.py`, `README.md` and `requirements.txt` for one-step reproduction of all results |

Read `member 1/REQUIREMENTS_AUDIT.md` before interpreting any result: its data coverage, eligibility and trading limitations apply to every part.

## Where reported results come from

| Result | File |
|---|---|
| Extracted weekly flow signals | `member 1/01_SGX_Flow_Collection/flows_extracted.csv` |
| Eligibility, exclusions and data quality | `member 1/02_Baseline_Backtesting/initial_eligibility_audit.csv`, `data_quality_exclusions.csv` |
| Baseline results | `member 1/02_Baseline_Backtesting/baseline_handoff_summary.csv` |
| Enhancement decisions | `member 2/results/enhancement_decisions.csv` |
| Performance metrics, full period and subperiods | `member 2/results/performance.csv` |
| Cumulative returns and drawdowns | `member 2/results/figures/net_returns_drawdowns.png` |
| Gross, net and doubled-cost comparison | `member 2/results/figures/cost_stress.png` |
| Turnover and liquidity | `member 2/results/liquidity_summary.csv`, `liquidity_extreme_trades.csv` |
| Annualised realised volatility | `member 3/results/annualised_volatility.csv` |
| Rolling 21-day volatility | `member 3/results/figures/rolling_volatility.png` |
| Daily VaR forecasts (% and S$) | `member 3/results/var_forecasts.csv`, `figures/var_forecasts_pct.png`, `figures/var_forecasts_sgd.png` |
| VaR coverage gaps and exceptions | `member 3/results/var_summary.csv`, `coverage_gap_episodes.csv` |

## Common conventions

- Three strategies: Smart Retail Flow FT5009, Smart Insti Flow FT5009, and the enhanced institutional strategy.
- Each starts with S$1,000,000; 49% long and 49% short targets, 10% name cap; trades at the first close after each weekly report.
- Cost scenarios: gross; net (20 bps one-way plus 3% annual borrow); doubled transaction cost (40 bps plus 3% borrow).
- Sample: January 2019 to September 2026, with subperiods 2019–2021, 2022–2023 and January 2024–September 2026; 252 trading days per year.

## Data sources

- SGX Weekly Top 10 institutional and retail fund-flow reports: https://www.sgx.com/stock-exchange/data-reports?reportType=203
- Daily prices, volume and corporate actions: Yahoo Finance chart data (download receipts in `member 1/02_Baseline_Backtesting/market_download_manifest.json`).
- Benchmark: State Street SPDR Straits Times Index ETF (ES3) NAV and distribution history, used as a total-return proxy.

Restored large data files stay inside their archives; do not upload expanded vendor CSVs or the `work/` folders.
