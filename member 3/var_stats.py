"""Part 5b (step 3, statistics): VaR coverage gaps and losses beyond VaR (exceptions)."""
import math
import numpy as np
import pandas as pd
from volatility import OUT, STRATEGIES
from var import CONFIDENCE

PERIODS = {'full': ('2019-01-01', '2026-09-30'),             # same boundaries as Member 2
           '2019–2021': ('2019-01-01', '2021-12-31'),
           '2022–2023': ('2022-01-01', '2023-12-31'),
           '2024–Sep2026': ('2024-01-01', '2026-09-30')}
GAPS = ['missing_return', 'insufficient_history']


def chi2_1_pvalue(lr):
    """Upper-tail probability of a chi-squared variable with one degree of freedom."""
    return math.erfc(math.sqrt(max(lr, 0.)/2))


def xlogy(x, y):
    return 0. if x == 0 else x*math.log(y)


def kupiec(exceptions, p=1-CONFIDENCE):
    """Unconditional coverage: is the exception rate consistent with 1%? Returns (LR, p-value)."""
    n, x = len(exceptions), int(np.sum(exceptions))
    if n == 0:
        return np.nan, np.nan
    lr = -2*(xlogy(n-x, 1-p) + xlogy(x, p) - xlogy(n-x, 1-x/n) - xlogy(x, x/n))
    return lr, chi2_1_pvalue(lr)


def christoffersen(exceptions):
    """Independence: is an exception more likely right after another one? Returns (LR, p-value).

    Uses consecutive available forecasts; gap days are skipped rather than treated as no exception.
    """
    e = np.asarray(exceptions, dtype=int)
    if len(e) < 2 or e.sum() == 0:
        return np.nan, np.nan
    prev, cur = e[:-1], e[1:]
    n00, n01 = int(((prev == 0) & (cur == 0)).sum()), int(((prev == 0) & (cur == 1)).sum())
    n10, n11 = int(((prev == 1) & (cur == 0)).sum()), int(((prev == 1) & (cur == 1)).sum())
    pi0 = n01/(n00+n01) if n00+n01 else 0.
    pi1 = n11/(n10+n11) if n10+n11 else 0.
    pi = (n01+n11)/(n00+n01+n10+n11)
    restricted = xlogy(n00+n10, 1-pi) + xlogy(n01+n11, pi)
    unrestricted = xlogy(n00, 1-pi0) + xlogy(n01, pi0) + xlogy(n10, 1-pi1) + xlogy(n11, pi1)
    lr = -2*(restricted-unrestricted)
    return lr, chi2_1_pvalue(lr)


def summary(table):
    """Coverage and exception statistics by strategy and period."""
    rows = []
    for s in STRATEGIES:
        for period, (lo, hi) in PERIODS.items():
            f = table[(table.strategy == s) & table.forecast_date.between(lo, hi)]
            ok = f[f.status.eq('complete')]
            exceptions = (ok.actual_net_return < -ok.var_pct).to_numpy()
            cash = int(f.status.eq('cash_only').sum())
            k, c = kupiec(exceptions), christoffersen(exceptions)
            rows.append(dict(strategy=s, period=period, forecast_dates=len(f),
                             complete=len(ok), cash_only=cash,
                             coverage_gaps=int(f.status.isin(GAPS).sum()),
                             coverage_rate=len(ok)/(len(f)-cash),   # among invested dates
                             expected_exceptions=len(ok)*(1-CONFIDENCE),
                             exceptions=int(exceptions.sum()),
                             exception_rate=exceptions.mean(),
                             kupiec_lr=k[0], kupiec_p=k[1],
                             christoffersen_lr=c[0], christoffersen_p=c[1]))
    return pd.DataFrame(rows)


def gap_episodes(table):
    """Group consecutive gap dates and list the held securities whose returns were missing."""
    rows = []
    for s in STRATEGIES:
        f = table[table.strategy == s].reset_index(drop=True)
        gap = f.status.isin(GAPS)
        run = (gap != gap.shift()).cumsum()                      # new id whenever gap flips
        for _, g in f[gap].groupby(run[gap]):
            securities = sorted({x for v in g.missing_securities.fillna('') for x in v.split(';') if x})
            rows.append(dict(strategy=s, first_date=g.forecast_date.iloc[0].date(),
                             last_date=g.forecast_date.iloc[-1].date(), sessions=len(g),
                             status=g.status.iloc[0], securities=';'.join(securities)))
    return pd.DataFrame(rows)


def main():
    table = pd.read_csv(OUT/'var_forecasts.csv', parse_dates=['forecast_date'])  # run var.py first
    stats, episodes = summary(table), gap_episodes(table)
    stats.to_csv(OUT/'var_summary.csv', index=False)
    episodes.to_csv(OUT/'coverage_gap_episodes.csv', index=False)

    pd.set_option('display.width', 200)
    print(stats.round(4).to_string(index=False))
    print(f'\n{len(episodes)} gap episodes; sessions per strategy:')
    print(episodes.groupby('strategy', sort=False).sessions.agg(['count', 'sum']).to_string())


if __name__ == '__main__':
    main()
