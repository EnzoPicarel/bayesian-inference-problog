"""Run exact inference under independent evidence sets."""

from itertools import product
from pathlib import Path

from problog import get_evaluatable
from problog.program import PrologString


MODELS = Path(__file__).resolve().parents[1] / "models"


def evaluate(filename, queries, **evidence):
    """Evaluate query atoms under one evidence set."""
    source = (MODELS / filename).read_text()
    rules = [
        line for line in source.splitlines()
        if not line.lstrip().startswith(("query(", "evidence("))
    ]
    rules.extend(
        f"evidence({atom}, {str(value).lower()})."
        for atom, value in evidence.items()
    )
    rules.extend(f"query({atom})." for atom in queries)
    result = get_evaluatable().create_from(PrologString("\n".join(rules))).evaluate()
    return {str(term): probability for term, probability in result.items()}


def show(model, queries, **evidence):
    probabilities = evaluate(model, queries, **evidence)
    conditions = ", ".join(f"{atom}={value}" for atom, value in evidence.items())
    suffix = f" | {conditions}" if conditions else ""
    for atom in queries:
        print(f"P({atom}{suffix}) = {probabilities[atom]:.8f}")
    return probabilities


def burglary():
    print("Burglary network")
    model = "burglary.pl"
    show(model, ("burglary", "earthquake"), johncalls=True, marycalls=True)
    show(model, ("burglary",), johncalls=True)
    show(model, ("alarm", "johncalls", "burglary", "world_jmanbne"))
    show(model, ("burglary",), earthquake=True)
    show(model, ("burglary", "johncalls"), alarm=True)
    show(model, ("burglary",), alarm=True, earthquake=True)
    show(model, ("johncalls",), alarm=True, marycalls=True)
    show(model, ("johncalls",), marycalls=True)
    print("Overlapping alarm rules")
    for b, e in product((False, True), repeat=2):
        show("burglary_overlapping.pl", ("alarm",), burglary=b, earthquake=e)


def fever():
    print("\nNoisy-OR fever model")
    model = "fever.pl"
    for cold, flu, malaria in product((False, True), repeat=3):
        show(model, ("fever",), cold=cold, flu=flu, malaria=malaria)
    show(model, ("malaria", "flu"), fever=True)
    show(model, ("malaria",), fever=True, flu=True)
    for variant in (model, "fever_leak.pl"):
        print(variant)
        show(variant, ("fever",), cold=False, flu=False, malaria=False)
        show(variant, ("malaria",), fever=True, cold=False, flu=False)


def sprinkler():
    print("\nSprinkler network")
    model = "sprinkler.pl"
    show(model, ("rain",), sprinkler=True)
    show(model, ("rain",), cloudy=True, wetgrass=True)
    show(model, ("rain",), sprinkler=True, wetgrass=True)
    marginals = show(model, ("cloudy", "rain", "sprinkler"))
    wet_when_cloudy = show(model, ("wetgrass",), cloudy=True)["wetgrass"]
    acceptance = marginals["cloudy"] * wet_when_cloudy
    joint = acceptance * show(
        model, ("rain_with_sprinkler_off",), cloudy=True, wetgrass=True
    )["rain_with_sprinkler_off"]
    print(f"P(cloudy, wetgrass) = {acceptance:.8f}")
    print(f"P(cloudy, not sprinkler, rain, wetgrass) = {joint:.8f}")


def causal():
    print("\nCausal sprinkler network")
    model = "sprinkler_causal.pl"
    marginal = show(model, ("cloudy", "rain", "wetgrass"))
    on = show(model, ("cloudy", "greenergrass"), sprinkler=True)["greenergrass"]
    off = show(model, ("greenergrass",), sprinkler=False)["greenergrass"]
    print("Intervene on")
    do_on = show("sprinkler_do.pl", ("cloudy", "rain", "greenergrass"))["greenergrass"]
    print("Intervene off")
    do_off = show("sprinkler_do_false.pl", ("greenergrass",))["greenergrass"]
    for variable, weight in marginal.items():
        present = show(model, ("greenergrass",), sprinkler=True, **{variable: True})
        absent = show(model, ("greenergrass",), sprinkler=True, **{variable: False})
        adjusted = weight * present["greenergrass"] + (1 - weight) * absent["greenergrass"]
        print(f"Adjusted over {variable} = {adjusted:.8f}")
    print(f"Interventional difference = {do_on - do_off:.8f}")
    print(f"Observational difference = {on - off:.8f}")


if __name__ == "__main__":
    burglary()
    fever()
    sprinkler()
    causal()
