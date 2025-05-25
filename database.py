from datetime import datetime
import sqlite3
import csv
import os
import tempfile

class MealDatabase:
    def __init__(self, db_name="meals.db"):
        script_dir = os.path.dirname(__file__)
        self.db_path = os.path.join(script_dir, db_name)
        if not os.access(script_dir, os.W_OK):
            print(f"Script directory not writable: {script_dir}")
            self.db_path = os.path.join(tempfile.gettempdir(), db_name)
            print(f"Falling back to temp directory: {self.db_path}")

        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.create_table()
            print(f"Database connected: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise

    def create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dish_name TEXT NOT NULL,
                    category TEXT,
                    prep_date TEXT,
                    portion_size INTEGER,
                    storage_location TEXT,
                    notes TEXT
                )
            """)
            self.conn.commit()
            print("Table created or verified")
        except sqlite3.Error as e:
            print(f"Table creation error: {e}")
            raise

    def add_meal(self, dish_name, category, prep_date, portion_size, storage_location, notes):
        try:
            dish_name = dish_name.strip() if dish_name else ""
            category = category.strip() if category else ""
            prep_date = prep_date.strip() if prep_date else ""
            storage_location = storage_location.strip() if storage_location else ""
            notes = notes.strip() if notes else ""

            if not dish_name:
                raise sqlite3.IntegrityError("Dish name cannot be empty")

            self.cursor.execute("""
                INSERT INTO meals (dish_name, category, prep_date, portion_size, storage_location, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dish_name, category, prep_date, portion_size, storage_location, notes))
            self.conn.commit()
            meal_id = self.cursor.lastrowid
            print(f"Meal added: {dish_name}, ID: {meal_id}")
            return meal_id, None
        except sqlite3.IntegrityError as e:
            print(f"Add meal integrity error: {e}")
            return None, f"Database integrity error: {e}"
        except sqlite3.OperationalError as e:
            print(f"Add meal operational error: {e}")
            return None, f"Database operational error: {e}"
        except sqlite3.Error as e:
            print(f"Add meal error: {e}")
            return None, f"Database error: {e}"
        except Exception as e:
            print(f"Unexpected add meal error: {e}")
            return None, f"Unexpected error: {e}"

    def update_meal(self, meal_id, dish_name, category, prep_date, portion_size, storage_location, notes):
        try:
            dish_name = dish_name.strip() if dish_name else ""
            category = category.strip() if category else ""
            prep_date = prep_date.strip() if prep_date else ""
            storage_location = storage_location.strip() if storage_location else ""
            notes = notes.strip() if notes else ""

            if not dish_name:
                raise sqlite3.IntegrityError("Dish name cannot be empty")

            self.cursor.execute("""
                UPDATE meals SET dish_name = ?, category = ?, prep_date = ?, portion_size = ?, 
                                storage_location = ?, notes = ?
                WHERE id = ?
            """, (dish_name, category, prep_date, portion_size, storage_location, notes, meal_id))
            self.conn.commit()
            changes = self.conn.total_changes
            print(f"Meal updated: ID {meal_id}, Changes: {changes}")
            return changes, None
        except sqlite3.IntegrityError as e:
            print(f"Update meal integrity error: {e}")
            return 0, f"Database integrity error: {e}"
        except sqlite3.OperationalError as e:
            print(f"Update meal operational error: {e}")
            return 0, f"Database operational error: {e}"
        except sqlite3.Error as e:
            print(f"Update meal error: {e}")
            return 0, f"Database error: {e}"
        except Exception as e:
            print(f"Unexpected update meal error: {e}")
            return 0, f"Unexpected error: {e}"
    
    def update_notes(self, meal_id, notes):
        try:
            notes = notes.strip() if notes else ""
            self.cursor.execute("UPDATE meals SET notes = ? WHERE id = ?", (notes, meal_id))
            self.conn.commit()
            changes = self.conn.total_changes
            print(f"Notes updated for meal ID {meal_id}: {notes}, Changes: {changes}")
            return changes, None
        except sqlite3.Error as e:
            print(f"Update notes error: {e}")
            return 0, f"Database error: {e}"
        except Exception as e:
            print(f"Unexpected update notes error: {e}")
            return 0, f"Unexpected error: {e}"

    def delete_meal(self, meal_id):
        try:
            self.cursor.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
            self.conn.commit()
            changes = self.conn.total_changes
            print(f"Meal deleted: ID {meal_id}, Changes: {changes}")
            return changes, None
        except sqlite3.Error as e:
            print(f"Delete meal error: {e}")
            return 0, f"Database error: {e}"
        except Exception as e:
            print(f"Unexpected delete meal error: {e}")
            return 0, f"Unexpected error: {e}"

    def get_all_meals(self):
        try:
            self.cursor.execute("SELECT * FROM meals")
            meals = self.cursor.fetchall()
            print(f"Fetched {len(meals)} meals")
            return meals
        except sqlite3.Error as e:
            print(f"Get all meals error: {e}")
            return []

    def search_meals(self, dish_name):
        try:
            self.cursor.execute("SELECT * FROM meals WHERE dish_name LIKE ?", (f"%{dish_name}%",))
            meals = self.cursor.fetchall()
            print(f"Search found {len(meals)} meals for query: {dish_name}")
            return meals
        except sqlite3.Error as e:
            print(f"Search meals error: {e}")
            return []

    def export_to_csv(self, csv_path):
        try:
            with open(csv_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Dish Name", "Category", "Prep Date", "Days Since Prep", 
                                "Portion Size", "Storage Location", "Notes"])
                meals = self.get_all_meals()
                today = datetime.now().date()
                for meal in meals:
                    prep_date = datetime.strptime(meal[3], "%Y-%m-%d").date()
                    days_since_prep = (today - prep_date).days
                    writer.writerow([meal[0], meal[1], meal[2], meal[3], days_since_prep, 
                                    meal[4], meal[5], meal[6]])
            print(f"Exported to CSV: {csv_path}")
            return csv_path, None
        except (sqlite3.Error, IOError) as e:
            print(f"Export to CSV error: {e}")
            return None, f"Export error: {e}"
        except Exception as e:
            print(f"Unexpected export to CSV error: {e}")
            return None, f"Unexpected error: {e}"

    def close(self):
        try:
            self.conn.close()
            print("Database connection closed")
        except sqlite3.Error as e:
            print(f"Close database error: {e}")