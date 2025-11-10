from typing import List, Iterable

def pretty_print_steps(title: str, steps: Iterable[str]) -> None:
    """Print a titled, enumerated list of steps."""
    print(f"\n=== {title} ===")
    for i, step in enumerate(steps, start=1):
        print(f"{i:>2}. {step}")


def brush_teeth() -> List[str]:
    """Algorithm: brushing teeth."""
    return [
        "Turn on water and wet the brush",
        "Put a pea of toothpaste on the brush",
        "Brush outer surfaces in circular motions (30–45 sec)",
        "Brush inner surfaces (30–45 sec)",
        "Brush chewing surfaces (30 sec)",
        "Gently brush the tongue (10–15 sec)",
        "Spit and rinse the mouth",
        "Rinse the brush and let it dry"
    ]


def do_laundry() -> List[str]:
    """Algorithm: doing laundry."""
    return [
        "Sort clothes by color and fabric",
        "Check pockets and zippers, turn delicates inside out",
        "Load the drum up to about 2/3 full",
        "Add detergent and softener if needed",
        "Choose program and temperature",
        "Press start and wait until finished",
        "Take out clothes and hang/lay to dry"
    ]


def make_coffee() -> List[str]:
    """Algorithm: making coffee (pour-over/French press)."""
    return [
        "Boil water and let it cool to ~92–96C",
        "Grind beans medium (or prepare ground coffee)",
        "Preheat equipment (dripper/press/cup) with hot water",
        "Bloom coffee with a little water (30–40 sec)",
        "Pour remaining water to target volume",
        "Wait for extraction and serve",
        "Optionally add milk/sugar",
        "Enjoy"
    ]


def cook_omelet() -> List[str]:
    """Algorithm: cooking an omelet."""
    return [
        "Crack 2–3 eggs into a bowl",
        "Add a pinch of salt and pepper; optionally milk/cream",
        "Whisk until smooth",
        "Heat pan and melt some butter/oil",
        "Pour the mixture; cook on medium heat",
        "Lift edges with a spatula to distribute mixture",
        "Add filling (cheese/herbs/veggies) if desired",
        "Fold in half and serve"
    ]


def prepare_backpack() -> List[str]:
    """Algorithm: preparing a backpack before leaving."""
    return [
        "Check weather and route",
        "Pack documents/wallet/keys/phone",
        "Add water and a small snack",
        "Take charger/power bank if needed",
        "Add first-aid items if relevant",
        "Check carry comfort and weight",
        "Close zippers and secure pockets"
    ]


def start_day() -> List[str]:
    """Bonus: composite algorithm that calls other functions."""
    steps: List[str] = []
    steps.append("Wake up and do a quick stretch (1–2 min)")
    steps.extend(brush_teeth())
    steps.extend(make_coffee())
    steps.extend(prepare_backpack())
    return steps