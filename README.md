<div align="center">
  <h1>Bayesian Inference with ProbLog</h1>
  <p>Exact inference, sampling benchmarks, and causal interventions on Bayesian networks.</p>
  <p><a href="#quick-start"><strong>Quick Start »</strong></a></p>
  <p>
    <img alt="ProbLog 2" src="https://img.shields.io/badge/ProbLog-2-526A8A">
    <img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9%2B-3776AB">
    <img alt="Matplotlib" src="https://img.shields.io/badge/Matplotlib-plots-11557C">
  </p>
</div>

## Architecture

- `models/` contains the burglary alarm network, a noisy-OR fever model with a leak variant, and observational and interventional sprinkler models.
- `scripts/exact.py` runs exact inference across evidence sets and computes causal adjustments and direct interventions.
- `scripts/sampling.py` compares prior and rejection sampling with exact inference, and benchmarks likelihood weighting against rejection sampling at equal draw budgets.

## Quick Start

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
problog models/sprinkler.pl
python scripts/exact.py
```

## Sampling Benchmarks

```sh
problog sample models/sprinkler_prior.pl -N 200000 --oneline --seed 42 > samples.txt
python scripts/sampling.py samples.txt --compare
```

The command writes `sampling-error.png`. Each sample size uses 20 runs. The figure shows the rejection-sampling error for rain given that the sprinkler is on. The fitted log–log slope was **−0.5308**, close to the expected **−0.5**.

![Rejection-sampling mean absolute error by sample size](assets/rejection-error.png)

For rain given cloudy and wet grass, the exact probability was **0.9758**. At 10,000 draws per run, mean absolute error was **0.0022** for rejection sampling and **0.0013** for likelihood weighting.

## Causal Inference

The probability of greener grass was **0.6643** with the sprinkler forced on and **0.3425** with it forced off. Adjusting for either Cloudy or Rain reproduced the sprinkler-on intervention result.

## Verification

Run `python scripts/exact.py` to reproduce the reference probabilities. The burglary posterior given both calls is **0.2842**, and the probability of rain given the sprinkler is on is **0.3000**.
