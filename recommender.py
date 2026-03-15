# recommender.py
import random
from typing import List, Optional, Tuple

from db import FoodDB
from models import Menu, Food


def _pick_subset(items: List[Food], max_items: int) -> List[Food]:
    if len(items) <= max_items:
        return items
    return random.sample(items, max_items)


def recommend_lunch_menus(
    db: FoodDB,
    kcal_range: Tuple[int, int],
    n: int = 5,
    allow_side_or_salad: bool = True,
    allow_drink: bool = True,
    allow_sauce: bool = True,
    seed: Optional[int] = None,
) -> List[Menu]:
    if seed is not None:
        random.seed(seed)

    kcal_min, kcal_max = kcal_range
    if kcal_max <= 0 or kcal_max < kcal_min:
        return []

    mains = db.list_by_category("main")

    sides: List[Food] = []
    if allow_side_or_salad:
        sides = db.list_by_category("side") + db.list_by_category("salad")

    drinks = db.list_by_category("drink") if allow_drink else []
    sauces = db.list_by_category("sauce") if allow_sauce else []

    mains = _pick_subset(mains, 60)
    sides = _pick_subset(sides, 50)
    drinks = _pick_subset(drinks, 40)
    sauces = _pick_subset(sauces, 40)

    side_options: List[Optional[Food]] = [None] + sides
    drink_options: List[Optional[Food]] = [None] + drinks
    sauce_options: List[Optional[Food]] = [None] + sauces

    valid: List[Menu] = []

    for main in mains:
        if main["kcal"] > kcal_max:
            continue

        for side in side_options:
            base1 = main["kcal"] + (side["kcal"] if side else 0)
            if base1 > kcal_max:
                continue

            for drink in drink_options:
                base2 = base1 + (drink["kcal"] if drink else 0)
                if base2 > kcal_max:
                    continue

                for sauce in sauce_options:
                    total = base2 + (sauce["kcal"] if sauce else 0)
                    if kcal_min <= total <= kcal_max:
                        valid.append(Menu(main=main, side=side, drink=drink, sauce=sauce))

    if not valid:
        return []

    random.shuffle(valid)

    picked: List[Menu] = []
    seen = set()
    for m in valid:
        key = (
            m.main["id"],
            m.side["id"] if m.side else None,
            m.drink["id"] if m.drink else None,
            m.sauce["id"] if m.sauce else None,
        )
        if key in seen:
            continue
        seen.add(key)
        picked.append(m)
        if len(picked) >= n:
            break

    return picked