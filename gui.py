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
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt

from calculator import DayInput, compute_lunch_plan
from db import FoodDB
from recommender import recommend_lunch_menus


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "foods_from_csv.db"


class MealPlannerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Meal Planner")
        self.resize(1000, 750)

        self.db = FoodDB(str(DB_PATH))
        self.current_menus = []

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel("Meal Planner - Lunch Recommender")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title)

        # Inputs
        daily_layout = QHBoxLayout()
        daily_label = QLabel("Napi keret (kcal):")
        self.daily_input = QLineEdit()
        self.daily_input.setPlaceholderText("pl. 1850")
        daily_layout.addWidget(daily_label)
        daily_layout.addWidget(self.daily_input)
        main_layout.addLayout(daily_layout)

        breakfast_layout = QHBoxLayout()
        breakfast_label = QLabel("Reggeli elfogyasztva:")
        self.breakfast_input = QLineEdit()
        self.breakfast_input.setPlaceholderText("pl. 349 (üresen hagyható)")
        breakfast_layout.addWidget(breakfast_label)
        breakfast_layout.addWidget(self.breakfast_input)
        main_layout.addLayout(breakfast_layout)

        dinner_layout = QHBoxLayout()
        dinner_label = QLabel("Vacsora tervezett:")
        self.dinner_input = QLineEdit()
        self.dinner_input.setPlaceholderText("pl. 600 (üresen hagyható)")
        dinner_layout.addWidget(dinner_label)
        dinner_layout.addWidget(self.dinner_input)
        main_layout.addLayout(dinner_layout)

        self.show_macros_checkbox = QCheckBox("Mutassa a makrókat")
        self.high_protein_checkbox = QCheckBox("High protein mód")
        main_layout.addWidget(self.show_macros_checkbox)
        main_layout.addWidget(self.high_protein_checkbox)

        # Buttons
        button_row = QHBoxLayout()

        self.recommend_button = QPushButton("Ajánlj ebédet")
        self.recommend_button.clicked.connect(self.recommend_meals)
        button_row.addWidget(self.recommend_button)

        self.refresh_button = QPushButton("Új ajánlások")
        self.refresh_button.clicked.connect(self.recommend_meals)
        button_row.addWidget(self.refresh_button)

        main_layout.addLayout(button_row)

        # Plan summary
        self.plan_summary = QTextEdit()
        self.plan_summary.setReadOnly(True)
        self.plan_summary.setMaximumHeight(140)
        main_layout.addWidget(self.plan_summary)

        # Two-column layout
        content_row = QHBoxLayout()

        # Left side: recommendation list
        left_layout = QVBoxLayout()
        left_title = QLabel("Ajánlott menük")
        left_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_layout.addWidget(left_title)

        self.menu_list = QListWidget()
        self.menu_list.itemClicked.connect(self.show_selected_menu)
        left_layout.addWidget(self.menu_list)

        content_row.addLayout(left_layout, 1)

        # Right side: selected menu details
        right_layout = QVBoxLayout()
        right_title = QLabel("Kiválasztott menü részletei")
        right_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(right_title)

        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        right_layout.addWidget(self.details_box)

        content_row.addLayout(right_layout, 1)

        main_layout.addLayout(content_row)

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

            self.current_menus = menus

            summary_lines = [
                "--- NAPI KALKULÁCIÓ ---",
                plan.note,
                f"Maradék kcal: {plan.remaining_kcal}",
                f"Ebéd cél tartomány: {plan.lunch_range}",
                "",
                "Mód: High Protein" if high_protein else "Mód: Normál ajánlás",
            ]
            self.plan_summary.setPlainText("\n".join(summary_lines))

            self.menu_list.clear()
            self.details_box.clear()

            if not menus:
                self.menu_list.addItem("Nincs találat ebben a tartományban.")
                return

            for i, menu in enumerate(menus, 1):
                title = (
                    f"{i}. {menu.main['name']} | "
                    f"{menu.total_kcal()} kcal | "
                    f"{menu.total_protein():.1f} g protein"
                )
                item = QListWidgetItem(title)
                item.setData(Qt.ItemDataRole.UserRole, i - 1)
                self.menu_list.addItem(item)

            # Első ajánlat automatikus megjelenítése
            self.menu_list.setCurrentRow(0)
            self.show_menu_details(0, show_macros=show_macros)

        except ValueError as e:
            QMessageBox.warning(self, "Hiba", f"Hibás adat: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Váratlan hiba", str(e))

    def show_selected_menu(self, item: QListWidgetItem):
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is None:
            return

        show_macros = self.show_macros_checkbox.isChecked()
        self.show_menu_details(index, show_macros=show_macros)

    def show_menu_details(self, index: int, show_macros: bool):
        if not (0 <= index < len(self.current_menus)):
            return

        menu = self.current_menus[index]
        self.details_box.setPlainText(menu.pretty(show_macros=show_macros))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MealPlannerGUI()
    window.show()
    sys.exit(app.exec())