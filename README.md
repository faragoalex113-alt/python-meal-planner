# python-meal-planner
Python CLI application that recommends meals based on a daily calorie target using SQLite.
# python-meal-planner
Python CLI application that recommends meals based on a daily calorie target using SQLite.

# Python Meal Planner

Personal Python project that recommends meal combinations based on a daily calorie target.

The application reads structured food data from an Excel/CSV table, converts it into an SQLite database, and generates meal suggestions that fit within a defined calorie range.

This project is currently under active development.

---

## Features

- Daily calorie budget calculation
- Meal recommendation within calorie range
- Optional macro nutrient display (protein, carbs, fat)
- Custom meal builder
- Food data stored in SQLite database
- Food categories (main, side, salad, sauce, drink, dessert)

---

## Technologies Used

- Python
- SQLite
- Pandas
- Excel / CSV data processing

---

## Project Structure
meal-planner
│
├── app.py
├── calculator.py
├── db.py
├── models.py
├── recommender.py
│
├── xlsx_to_db.py
│
├── data
│ └── foods_from_csv.db
│
├── requirements.txt
└── README.md

---

## How to Run

Clone the repository:
git clone https://github.com/faragoalex113-alt/python-meal-planner.git


Install dependencies:
pip install -r requirements.txt


Run the program:
python app.py


---

## Future Improvements

- High protein recommendation mode
- Meal logging / daily tracking
- Smarter recommendation scoring
- GUI interface

---

## Author

Personal learning project built while studying Python and data related tools.
