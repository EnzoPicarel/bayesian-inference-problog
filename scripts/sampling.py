"""Compare sampling methods for the sprinkler network."""

import argparse
import math
import random
from pathlib import Path
from statistics import mean

VARIABLES = ("cloudy", "sprinkler", "rain", "wetgrass")
EXACT_RAIN_GIVEN_SPRINKLER = 0.3
# P(rain, wetgrass | cloudy) / P(wetgrass | cloudy)
EXACT_RAIN_GIVEN_CLOUDY_AND_WETGRASS = 0.7272 / 0.7452
SPRINKLER_CPTS = (
    ("cloudy", (), {(): 0.5}),
    ("sprinkler", ("cloudy",), {(False,): 0.5, (True,): 0.1}),
    ("rain", ("cloudy",), {(False,): 0.2, (True,): 0.8}),
    ("wetgrass", ("sprinkler", "rain"), {
        (False, False): 0.0,
        (False, True): 0.90,
        (True, False): 0.90,
        (True, True): 0.99,
    }),
)


def parse_samples(path):
    """Read default or --oneline ProbLog output as Boolean worlds."""
    lines = Path(path).read_text().splitlines()
    if "----------------" in lines:
        lines = "\n".join(lines).split("----------------")

    samples = []
    for index, line in enumerate(lines, start=1):
        sample = {}
        for literal in line.split():
            value = not literal.startswith(r"\+")
            atom = literal.removeprefix(r"\+").removesuffix(".")
            if atom not in VARIABLES or atom in sample:
                raise ValueError(f"Invalid literal {literal!r} in sample {index}")
            sample[atom] = value
        samples.append({atom: sample.get(atom, False) for atom in VARIABLES})
    return samples


def matches(sample, event):
    return all(sample[atom] == value for atom, value in event.items())


def estimate(samples, event):
    """Return the fraction of worlds consistent with the event."""
    if not samples:
        raise ValueError("An estimate requires at least one sample")
    return sum(matches(sample, event) for sample in samples) / len(samples)


def rejection_estimate(samples, query, evidence):
    """Return the estimate and acceptance rate, or None for a missing estimate."""
    accepted = [sample for sample in samples if matches(sample, evidence)]
    atom, value = query
    probability = estimate(accepted, {atom: value}) if accepted else None
    acceptance_rate = len(accepted) / len(samples) if samples else 0.0
    return probability, acceptance_rate


def likelihood_weighting(query, evidence, n, rng=random):
    """Estimate a query from weighted CPT draws, or return None with zero total weight."""
    atom, value = query
    total_weight = 0.0
    matching_weight = 0.0
    for _ in range(n):
        sample = {}
        weight = 1.0
        for variable, parents, cpt in SPRINKLER_CPTS:
            probability = cpt[tuple(sample[parent] for parent in parents)]
            if variable in evidence:
                observed = evidence[variable]
                sample[variable] = observed
                weight *= probability if observed else 1 - probability
            else:
                sample[variable] = rng.random() < probability
        total_weight += weight
        if sample[atom] == value:
            matching_weight += weight
    return matching_weight / total_weight if total_weight else None


def compare_estimators(samples, sizes, runs=20):
    """Compare mean estimates and errors at equal draw budgets for rain given cloudy and wet grass."""
    if len(samples) < max(sizes) * runs:
        raise ValueError(f"The comparison requires at least {max(sizes) * runs} samples")

    rng = random.Random(42)
    query = ("rain", True)
    evidence = {"cloudy": True, "wetgrass": True}
    exact = EXACT_RAIN_GIVEN_CLOUDY_AND_WETGRASS
    for size in sizes:
        rejection_estimates = []
        weighted_estimates = []
        for start in range(0, size * runs, size):
            rejection, _ = rejection_estimate(samples[start:start + size], query, evidence)
            weighted = likelihood_weighting(query, evidence, size, rng)
            if rejection is None or weighted is None:
                raise ValueError(f"An estimate was undefined at N={size}")
            rejection_estimates.append(rejection)
            weighted_estimates.append(weighted)
        yield (
            size,
            mean(rejection_estimates),
            mean(abs(estimate - exact) for estimate in rejection_estimates),
            mean(weighted_estimates),
            mean(abs(estimate - exact) for estimate in weighted_estimates),
        )


def experiment(samples, sizes=(100, 1_000, 10_000), runs=20):
    """Return (size, mean acceptance, mean absolute error) for each setting."""
    if len(samples) < max(sizes) * runs:
        raise ValueError(f"The experiment requires at least {max(sizes) * runs} samples")

    results = []
    for size in sizes:
        acceptance_rates = []
        errors = []
        for start in range(0, size * runs, size):
            probability, acceptance = rejection_estimate(
                samples[start:start + size], ("rain", True), {"sprinkler": True}
            )
            acceptance_rates.append(acceptance)
            if probability is not None:
                errors.append(abs(probability - EXACT_RAIN_GIVEN_SPRINKLER))
        if not errors:
            raise ValueError(f"No accepted draws across {runs} runs of size {size}")
        results.append((size, mean(acceptance_rates), mean(errors)))
    return results


def plot_error(results, path):
    """Plot positive mean errors and return the fitted slope in log space."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    positive = [(size, error) for size, _, error in results if error > 0]
    if len(positive) < 2:
        raise ValueError("At least two positive mean errors are needed for a log-log fit")
    sizes, errors = zip(*positive)
    log_sizes = [math.log(size) for size in sizes]
    log_errors = [math.log(error) for error in errors]
    centered_sizes = [size - mean(log_sizes) for size in log_sizes]
    slope = (
        sum(size * error for size, error in zip(centered_sizes, log_errors))
        / sum(size ** 2 for size in centered_sizes)
    )

    fig, ax = plt.subplots(figsize=(6.4, 3.8), layout="constrained")
    ax.loglog(sizes, errors, "o-", color="#21618c", label="Measured error")
    ax.loglog(
        sizes, [errors[0] * math.sqrt(sizes[0] / size) for size in sizes],
        "--", color="#a04000", label=r"$N^{-1/2}$ reference",
    )
    ax.set(xlabel="Prior draws per run", ylabel="Mean absolute error")
    ax.grid(True, which="major", alpha=0.25)
    ax.legend()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return slope


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samples", type=Path)
    parser.add_argument("--plot", type=Path, default=Path("sampling-error.png"))
    parser.add_argument(
        "--compare", action="store_true", help="compare likelihood weighting and rejection sampling"
    )
    args = parser.parse_args()

    samples = parse_samples(args.samples)
    results = experiment(samples)
    print(f"{len(samples):,} prior samples")
    for sample in samples[:3]:
        print(sample)
    prior = samples[:10_000]
    joint = {"cloudy": True, "sprinkler": False, "rain": True, "wetgrass": True}
    print(f"P(rain) ~ {estimate(prior, {'rain': True}):.4f}")
    print(f"P(cloudy, not sprinkler, rain, wetgrass) ~ {estimate(prior, joint):.4f}")
    for size, acceptance, error in results:
        print(f"N={size:>5}: acceptance={acceptance:.4f}, mean absolute error={error:.6f}")
    print(f"Log-log slope: {plot_error(results, args.plot):.4f}")
    if args.compare:
        print("Estimator comparison: P(rain | cloudy, wetgrass)")
        print(f"Exact probability: {EXACT_RAIN_GIVEN_CLOUDY_AND_WETGRASS:.8f}")
        sizes = [size for size, _, _ in results]
        comparisons = compare_estimators(samples, sizes)
        for size, rejection, rejection_error, weighted, weighted_error in comparisons:
            print(
                f"N={size:>5}: rejection={rejection:.6f} (MAE {rejection_error:.6f}), "
                f"likelihood weighting={weighted:.6f} (MAE {weighted_error:.6f})"
            )


if __name__ == "__main__":
    main()
