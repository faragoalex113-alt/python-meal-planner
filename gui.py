from pathlib import Path
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QMessageBox,
)

from calculator import DayInput, compute_lunch_plan
from db import FoodDB
from recommender import recommend_lunch_menus


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "foods_from_csv.db"


class MealPlannerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Meal Planner")
        self.resize(800, 700)

        self.db = FoodDB(str(DB_PATH))

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel("Meal Planner - Lunch Recommender")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # Daily limit
        daily_layout = QHBoxLayout()
        daily_label = QLabel("Napi keret (kcal):")
        self.daily_input = QLineEdit()
        self.daily_input.setPlaceholderText("pl. 1850")
        daily_layout.addWidget(daily_label)
        daily_layout.addWidget(self.daily_input)
        main_layout.addLayout(daily_layout)

        # Breakfast
        breakfast_layout = QHBoxLayout()
        breakfast_label = QLabel("Reggeli elfogyasztva:")
        self.breakfast_input = QLineEdit()
        self.breakfast_input.setPlaceholderText("pl. 349 (üresen hagyható)")
        breakfast_layout.addWidget(breakfast_label)
        breakfast_layout.addWidget(self.breakfast_input)
        main_layout.addLayout(breakfast_layout)

        # Dinner
        dinner_layout = QHBoxLayout()
        dinner_label = QLabel("Vacsora tervezett:")
        self.dinner_input = QLineEdit()
        self.dinner_input.setPlaceholderText("pl. 600 (üresen hagyható)")
        dinner_layout.addWidget(dinner_label)
        dinner_layout.addWidget(self.dinner_input)
        main_layout.addLayout(dinner_layout)

        # Checkboxes
        self.show_macros_checkbox = QCheckBox("Mutassa a makrókat")
        self.high_protein_checkbox = QCheckBox("High protein mód")

        main_layout.addWidget(self.show_macros_checkbox)
        main_layout.addWidget(self.high_protein_checkbox)

        # Button
        self.recommend_button = QPushButton("Ajánlj ebédet")
        self.recommend_button.clicked.connect(self.recommend_meals)
        main_layout.addWidget(self.recommend_button)

        # Output
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        main_layout.addWidget(self.output_box)

        self.setLayout(main_layout)

    def parse_int_or_none(self, text: str):
        text = text.strip()
        if text == "":
            return None
        return int(text)

    def recommend_meals(self):
        try:
            daily_limit = self.parse_int_or_none(self.daily_input.text())
            breakfast_kcal = self.parse_int_or_none(self.breakfast_input.text())
            dinner_kcal = self.parse_int_or_none(self.dinner_input.text())

            if daily_limit is None:
                raise ValueError("A napi keret megadása kötelező.")

            day_input = DayInput(
                daily_limit=daily_limit,
                breakfast_kcal=breakfast_kcal,
                lunch_kcal=0,
                dinner_planned_kcal=dinner_kcal,
            )

            plan = compute_lunch_plan(day_input)

            show_macros = self.show_macros_checkbox.isChecked()
            high_protein = self.high_protein_checkbox.isChecked()

            menus = recommend_lunch_menus(
                self.db,
                plan.lunch_range,
                n=5,
                high_protein=high_protein,
            )

            lines = []
            lines.append("--- NAPI KALKULÁCIÓ ---")
            lines.append(plan.note)
            lines.append(f"Maradék kcal: {plan.remaining_kcal}")
            lines.append(f"Ebéd cél tartomány: {plan.lunch_range}")
            lines.append("")

            if high_protein:
                lines.append("=== HIGH PROTEIN EBÉD AJÁNLATOK ===")
            else:
                lines.append("=== EBÉD AJÁNLATOK ===")

            if not menus:
                lines.append("Nincs találat ebben a tartományban.")
            else:
                for i, menu in enumerate(menus, 1):
                    lines.append("")
                    lines.append(f"{i})")
                    lines.append(menu.pretty(show_macros=show_macros))

            self.output_box.setPlainText("\n".join(lines))

        except ValueError as e:
            QMessageBox.warning(self, "Hiba", f"Hibás adat: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Váratlan hiba", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MealPlannerGUI()
    window.show()
    sys.exit(app.exec())