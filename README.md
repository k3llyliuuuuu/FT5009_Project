# FT5009 Group Project: Smart Flow Strategies

Do institutional or retail investors' weekly SGX fund flows give better trading signals? This project collects the SGX Weekly Top 10 fund-flow reports released from January 2019 to September 2026, backtests long/short strategies that follow each investor group, enhances the institutional strategy with a trend filter, and evaluates performance, trading feasibility and risk.

## Reproduce all results

From this folder, with Python 3.12, preferably in a fresh virtual environment:

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
python -m pip install -r requirements.txt
python run_all.py
```

Use the locked versions in `requirements.txt` (pandas 2.3.3). Member 1's audit fails under pandas 3, whose `DataFrame.stack()` keeps missing values.

`run_all.py` runs offline and stops at the first failing step:

1. `member 2/run_member2.py` rebuilds Member 1's source extraction, market inputs, baseline backtests, tests and audit in an isolated copy under `member 2/work/`, so `member 1/` is never rewritten. It then runs the enhancement, all nine strategy/cost paths, the evaluation and the Member 2 tests, and writes the risk handoff.
2. The five Member 3 scripts compute volatility and VaR from Member 2's results.

A full run takes about two minutes. Later runs reuse Member 2's verified copy of Member 1's inputs while Member 1's files are unchanged. `run_all.py` enables Python's UTF-8 mode for every step; without it, Windows writes Member 1's extracted CSVs in the local code page and later reads fail. Options:

- `python run_all.py --rebuild-inputs` forces a fresh reconstruction of Member 1's inputs.
- `python run_all.py --member3-only` reruns Part 5 from Member 2's existing results (about 30 seconds).

Each member folder can also be run on its own; see its README.

Reproduction was verified on Windows with Python 3.12.10 and the locked packages: every CSV result matched the committed files. Git may still list some outputs as modified after a rerun, with no change in content:

- `.csv.gz` files: Windows writes CRLF line endings inside the compressed files.
- PDF and PNG figures: embedded creation metadata differs; the images are pixel-identical.
- `member 2/results/validation.json` and `artifact_sha256.json`: they record the Python version and file hashes, which change with the platform and line endings.

Discard these changes rather than committing them. A rerun also regenerates `member 2/results/MEMBER2_REPORT.md` and `MEMBER2_REPORT_A4.pdf`, which are not kept in the repository.

## Project structure

| Folder | Assignment parts | Contents |
|---|---|---|
| `member 1/01_SGX_Flow_Collection/` | 1a | 399 original SGX Weekly Top 10 reports (archived), parser and dataset checks |
| `member 1/02_Baseline_Backtesting/` | 1a, 1b, 2a, 2b | Daily prices, volume and benchmark; eligibility rules; backtesting engine; retail and institutional baselines |
| `member 2/` | 3a, 3b, 4a, 4b, 4c | 126-day SMA trend-confirmation enhancement; performance, subperiod, cost and liquidity evaluation; risk handoff |
| `member 3/` | 5a, 5b | Realised and rolling volatility; 99% historical-simulation VaR, coverage gaps and VaR backtests |

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
