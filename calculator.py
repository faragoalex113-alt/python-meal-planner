# calculator.py
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Targets:
    breakfast_min: int = 300
    breakfast_max: int = 450

    lunch_min: int = 700
    lunch_max: int = 950

    dinner_min: int = 450
    dinner_max: int = 600

    # Basic mód ebéd plafon (ha hiányzik reggeli vagy vacsora adat)
    lunch_basic_max: int = 1100


@dataclass(frozen=True)
class DayInput:
    daily_limit: int
    breakfast_kcal: Optional[int] = None      # elfogyasztott
    lunch_kcal: Optional[int] = 0             # elfogyasztott (ajánlás előtt 0)
    dinner_planned_kcal: Optional[int] = None # előre beírt vacsora


@dataclass(frozen=True)
class LunchPlan:
    mode: str  # "precise" vagy "basic"
    remaining_kcal: int
    lunch_range: Tuple[int, int]  # (min, max)
    note: str


def _clamp_nonnegative(x: int) -> int:
    return x if x > 0 else 0


def remaining_kcal(inp: DayInput) -> int:
    """Napi maradék kcal = napi keret - (reggeli + ebéd + tervezett vacsora)."""
    consumed = 0
    if inp.breakfast_kcal is not None:
        consumed += inp.breakfast_kcal
    if inp.lunch_kcal is not None:
        consumed += inp.lunch_kcal
    if inp.dinner_planned_kcal is not None:
        consumed += inp.dinner_planned_kcal

    return inp.daily_limit - consumed


def compute_lunch_plan(inp: DayInput, targets: Targets = Targets()) -> LunchPlan:
    """
    Ebéd cél-tartomány a maradék alapján.
    - Precise mód: ha reggeli és vacsora is meg van adva → ebéd 700–950 (maradékhoz vágva)
    - Basic mód: ha hiányzik reggeli vagy vacsora → ebéd 700–1100 (maradékhoz vágva)
    """
    rem = remaining_kcal(inp)

    precise = (inp.breakfast_kcal is not None) and (inp.dinner_planned_kcal is not None)
    if precise:
        mode = "precise"
        base_min, base_max = targets.lunch_min, targets.lunch_max
        note = "Pontos mód: reggeli és vacsora is megadva."
    else:
        mode = "basic"
        base_min, base_max = targets.lunch_min, targets.lunch_basic_max
        note = "Basic mód: reggeli vagy vacsora hiányzik, az ebéd csak becslés."

    # Ebéd max nem lehet több, mint a maradék (ha maradék negatív, akkor 0)
    lunch_max = min(base_max, _clamp_nonnegative(rem))
    lunch_min = min(base_min, lunch_max)  # ha kevés a maradék, min lecsúszik

    # Extra figyelmeztetések
    if rem < 0:
        note += " FIGYELEM: a megadott értékek túllépik a napi keretet!"
    elif lunch_max < targets.lunch_min:
        note += " FIGYELEM: a maradék 700 alatt van, csak kicsi ebéd fér bele."

    return LunchPlan(
        mode=mode,
        remaining_kcal=rem,
        lunch_range=(lunch_min, lunch_max),
        note=note,
    )






