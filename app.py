# app.py
from __future__ import annotations

from typing import Optional

from calculator import DayInput, compute_lunch_plan
from db import FoodDB
from recommender import recommend_lunch_menus
from models import Menu

DB_PATH = "data/foods_from_csv.db"


def ask_int(prompt: str, allow_empty: bool = False) -> Optional[int]:
    while True:
        s = input(prompt).strip()
        if allow_empty and s == "":
            return None
        try:
            return int(s)
        except ValueError:
            print("Kérlek számot írj.")


def choose_from_list(items: list[dict], title: str, max_show: int = 20) -> Optional[dict]:
    if not items:
        print("Nincs találat.")
        return None

    print(f"\n--- {title} ---")
    show = items[:max_show]
    for i, it in enumerate(show, 1):
        print(f"{i}) {it['name']} ({it['kcal']} kcal)")

    if len(items) > max_show:
        print(f"... (+{len(items) - max_show} további találat, szűkíts kereséssel)")

    n = ask_int("Válassz sorszámot (Enter = mégse): ", allow_empty=True)
    if n is None:
        return None
    if not (1 <= n <= len(show)):
        print("Érvénytelen választás.")
        return None
    return show[n - 1]


def search_and_pick(db: FoodDB, expected_category: str, label: str) -> Optional[dict]:
    while True:
        q = input(f"\n{label} keresés (pl. 'whopper', Enter = mégse): ").strip()
        if q == "":
            return None
        hits = db.search_by_name(q, limit=25)
        hits = [h for h in hits if h["category"] == expected_category]
        pick = choose_from_list(hits, f"Találatok: {label}")
        if pick:
            return pick
        # ha nem választott, mehet új keresés


def yes_no(prompt: str, default: bool = False) -> bool:
    d = "I/n" if default else "i/N"
    s = input(f"{prompt} ({d}): ").strip().lower()
    if s == "":
        return default
    return s in ("i", "igen", "y", "yes")


def build_custom_lunch(db: FoodDB) -> Optional[Menu]:
    print("\n=== SAJÁT EBÉD ÖSSZERAKÁSA ===")
    main = search_and_pick(db, "main", "Főétel")
    if not main:
        print("Mégse.")
        return None

    side = None
    drink = None

    if yes_no("Kérsz köretet?", default=True):
        side = search_and_pick(db, "side", "Köret")

    if yes_no("Kérsz italt?", default=True):
        drink = search_and_pick(db, "drink", "Ital")

    return Menu(main=main, side=side, drink=drink)


def modify_menu_loop(db: FoodDB, menu: Menu, show_macros: bool) -> Menu:
    while True:
        print("\n--- AKTUÁLIS MENÜ ---")
        print(menu.pretty(show_macros=show_macros))

        print("\nMódosítás:")
        print("1) Ital módosítás")
        print("2) Köret/Saláta módosítás")
        print("3) Főétel csere")
        print("4) Szósz/Öntet módosítás")
        print("0) Kész")

        choice = ask_int("Választás: ")

        if choice == 0:
            return menu

        if choice == 1:
            if menu.drink is not None and yes_no("Kivegyük az italt?", default=True):
                menu.drink = None
            else:
                d = search_and_pick(db, "drink", "Ital")
                if d:
                    menu.drink = d

        elif choice == 2:
            # ide jön a C logika: side vagy salad
            if menu.side is not None and yes_no("Kivegyük a köretet/salátát?", default=True):
                menu.side = None
            else:
                which = input("Köret vagy Saláta? (k/s): ").strip().lower()
                if which.startswith("s"):
                    s = search_and_pick(db, "salad", "Saláta")
                else:
                    s = search_and_pick(db, "side", "Köret")
                if s:
                    menu.side = s

        elif choice == 3:
            m = search_and_pick(db, "main", "Főétel")
            if m:
                menu.main = m

        elif choice == 4:
            if menu.sauce is not None and yes_no("Kivegyük a szószt/öntetet?", default=True):
                menu.sauce = None
            else:
                s = search_and_pick(db, "sauce", "Szósz/Öntet")
                if s:
                    menu.sauce = s

        else:
            print("Ismeretlen opció.")

def main():
    print("=== Menü Planner (PDF -> DB) MVP ===")
    show_macros = yes_no("Mutassam a makrókat is a menüknél?", default=False)

    daily = ask_int("Napi keret kcal (pl. 1850): ")
    breakfast = ask_int("Reggeli elfogyasztva (Enter = nincs megadva): ", allow_empty=True)
    dinner_planned = ask_int("Vacsora tervezett (Enter = nincs megadva): ", allow_empty=True)

    inp = DayInput(
        daily_limit=daily,
        breakfast_kcal=breakfast,
        lunch_kcal=0,
        dinner_planned_kcal=dinner_planned,
    )

    plan = compute_lunch_plan(inp)
    print("\n--- NAPI KALKULÁCIÓ ---")
    print(plan.note)
    print("Maradék kcal:", plan.remaining_kcal)
    print("Ebéd cél tartomány:", plan.lunch_range)

    db = FoodDB(DB_PATH)

    # Program ajánl 5 menüt
    menus = recommend_lunch_menus(db, plan.lunch_range, n=5)
    print("\n=== EBÉD AJÁNLATOK ===")
    if not menus:
        print("Nincs találat ebbe a tartományba. Próbáld meg más kerettel / basic módban.")
    else:
        for i, m in enumerate(menus, 1):
            print(f"\n{i})")
            print(m.pretty())

    print("\n6) Saját ebéd összerakása")

    pick = ask_int("\nVálassz 1-5 vagy 6 (Enter = kilép): ", allow_empty=True)
    if pick is None:
        print("Kilépés.")
        return

    chosen: Optional[Menu] = None

    if 1 <= pick <= 5:
        if pick <= len(menus):
            chosen = menus[pick - 1]
        else:
            print("Nincs ilyen ajánlat.")
            return
    elif pick == 6:
        chosen = build_custom_lunch(db)
        if not chosen:
            return
    else:
        print("Érvénytelen választás.")
        return

    # Módosító loop
    chosen = modify_menu_loop(db, chosen, show_macros=show_macros)

    print("\n=== VÉGSŐ MENÜ ===")
    print(chosen.pretty())
    print(m.pretty(show_macros=show_macros))

if __name__ == "__main__":
    main()