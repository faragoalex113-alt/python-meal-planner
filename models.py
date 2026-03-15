# models.py
from dataclasses import dataclass
from typing import Optional, Dict, Any

Food = Dict[str, Any]


@dataclass
class Menu:
    main: Food
    side: Optional[Food] = None   # lehet "side" vagy "salad"
    drink: Optional[Food] = None
    sauce: Optional[Food] = None  # külön extra

    def total_kcal(self) -> int:
        return (
            int(self.main["kcal"])
            + (int(self.side["kcal"]) if self.side else 0)
            + (int(self.drink["kcal"]) if self.drink else 0)
            + (int(self.sauce["kcal"]) if self.sauce else 0)
        )

    def _sum(self, key: str) -> float:
        return (
            float(self.main.get(key, 0.0))
            + (float(self.side.get(key, 0.0)) if self.side else 0.0)
            + (float(self.drink.get(key, 0.0)) if self.drink else 0.0)
            + (float(self.sauce.get(key, 0.0)) if self.sauce else 0.0)
        )

    def total_protein(self) -> float:
        return self._sum("protein_g")

    def total_carbs(self) -> float:
        return self._sum("carbs_g")

    def total_fat(self) -> float:
        return self._sum("fat_g")

    def pretty(self, show_macros: bool = False) -> str:
        parts = [
            f'Főétel: {self.main["name"]} ({self.main["kcal"]} kcal)',
            f'Köret/Saláta: {self.side["name"]} ({self.side["kcal"]} kcal)' if self.side else "Köret/Saláta: nincs",
            f'Ital: {self.drink["name"]} ({self.drink["kcal"]} kcal)' if self.drink else "Ital: nincs",
            f'Szósz/Öntet: {self.sauce["name"]} ({self.sauce["kcal"]} kcal)' if self.sauce else "Szósz/Öntet: nincs",
            f"Összesen: {self.total_kcal()} kcal",
        ]

        if show_macros:
            parts.append(
                "Makrók (összes): "
                f"P {self.total_protein():.1f} g | "
                f"CH {self.total_carbs():.1f} g | "
                f"Zsír {self.total_fat():.1f} g"
            )

        return "\n".join(parts)