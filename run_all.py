"""Reproduce every reported result offline: Member 1 inputs, Member 2 Parts 3-4, Member 3 Part 5.

Member 2's runner rebuilds Member 1's extraction, baseline, tests and audit in an isolated copy
under `member 2/work/`, so the `member 1/` folder is never rewritten. Member 3 then reads
Member 2's results. Any failing step stops the run.
"""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
MEMBER3 = ['volatility.py', 'rolling_volatility.py', 'var.py', 'var_plot.py', 'var_stats.py']
# UTF-8 mode makes open() default to UTF-8 on every OS. Without it, Windows writes Member 1's
# extracted CSVs in the locale code page (e.g. cp1252) and later UTF-8 reads fail.
ENV = {**os.environ, 'PYTHONUTF8': '1'}


def run(label, args):
    print(f'\n=== {label} ===', flush=True)
    start = time.time()
    subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, env=ENV, check=True)
    print(f'--- {label}: done in {time.time()-start:.0f}s', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebuild-inputs', action='store_true',
                        help="force Member 2 to reconstruct a fresh copy of Member 1's inputs")
    parser.add_argument('--member3-only', action='store_true',
                        help="rerun Part 5 only, from Member 2's existing results")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        print(f'Warning: validated with Python 3.12; running {sys.version.split()[0]}', flush=True)
    start = time.time()
    if not args.member3_only:
        member2 = [ROOT/'member 2/run_member2.py'] + (['--rebuild-inputs'] if args.rebuild_inputs else [])
        run('Members 1-2: data, baselines, enhancement and evaluation (Parts 1-4)', member2)
    for script in MEMBER3:
        run(f'Member 3: {script} (Part 5)', [ROOT/'member 3'/script])
    print(f'\nAll steps completed in {time.time()-start:.0f}s.')


if __name__ == '__main__':
    main()
