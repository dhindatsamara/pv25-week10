import sys
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QColor
from app_ui import MealPrepUI
from database import MealDatabase

class MealPrepApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meal Prep Planner")
        self.setGeometry(100, 100, 1200, 600)
        self.current_meal_id = None
        self.sort_order = "newest"
        try:
            self.db = MealDatabase()
            self.ui = MealPrepUI()
            self.setCentralWidget(self.ui)
            self.ui.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.setup_connections()
            self.load_table()
            self.adjustSize()
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Failed to initialize app: {e}")

    def setup_connections(self):
        try:
            self.ui.save_button.clicked.connect(self.save_meal)
            self.ui.update_button.clicked.connect(self.update_meal)
            self.ui.delete_button.clicked.connect(self.delete_meal)
            self.ui.export_button.clicked.connect(self.export_to_csv)
            self.ui.search_input.textChanged.connect(self.filter_table)
            self.ui.sort_combo.currentTextChanged.connect(self.sort_table)
            self.ui.table.cellClicked.connect(self.load_meal_for_edit)
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect signals: {e}")

    def validate_inputs(self, dish_name, category, prep_date, storage_location):
        valid_categories = ["Breakfast", "Lunch", "Dinner", "Snack"]
        valid_storage = ["Fridge", "Freezer", "Pantry"]
        try:
            today = datetime.now().date()
            prep_date_obj = datetime.strptime(prep_date, "%Y-%m-%d").date()
            if not dish_name.strip():
                return False, "Dish name cannot be empty!"
            if category not in valid_categories:
                return False, "Invalid category selected!"
            if prep_date_obj > today:
                return False, "Prep date cannot be in the future!"
            if storage_location not in valid_storage:
                return False, "Invalid storage location selected!"
            return True, ""
        except ValueError:
            return False, "Invalid date format!"

    def save_meal(self):
        try:
            dish_name = self.ui.dish_input.text().strip()
            category = self.ui.category_input.currentText()
            prep_date = self.ui.prep_date_input.date().toString("yyyy-MM-dd")
            portion_size = self.ui.portion_input.value()
            storage_location = self.ui.storage_input.currentText()
            notes = self.ui.notes_input.toPlainText().strip()
            is_valid, error_message = self.validate_inputs(dish_name, category, prep_date, storage_location)
            if not is_valid:
                QMessageBox.warning(self, "Input Error", error_message)
                return
            meal_id, error_message = self.db.add_meal(dish_name, category, prep_date, portion_size, storage_location, notes)
            if meal_id:
                QMessageBox.information(self, "Success", "Meal added successfully!")
                self.load_table()
                self.ui.clear_inputs()
                self.current_meal_id = None
            else:
                QMessageBox.warning(self, "Error", f"Failed to add meal: {error_message}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save meal: {e}")

    def update_meal(self):
        try:
            if self.current_meal_id is None:
                QMessageBox.warning(self, "Selection Error", "No meal selected for update!")
                return
            dish_name = self.ui.dish_input.text().strip()
            category = self.ui.category_input.currentText()
            prep_date = self.ui.prep_date_input.date().toString("yyyy-MM-dd")
            portion_size = self.ui.portion_input.value()
            storage_location = self.ui.storage_input.currentText()
            notes = self.ui.notes_input.toPlainText().strip()
            is_valid, error_message = self.validate_inputs(dish_name, category, prep_date, storage_location)
            if not is_valid:
                QMessageBox.warning(self, "Input Error", error_message)
                return
            changes, error_message = self.db.update_meal(
                self.current_meal_id, dish_name, category, prep_date, portion_size, storage_location, notes
            )
            if changes > 0:
                QMessageBox.information(self, "Success", "Meal updated successfully!")
                self.load_table()
                self.ui.clear_inputs()
                self.ui.save_button.setEnabled(True)
                self.current_meal_id = None
            else:
                QMessageBox.warning(self, "Error", f"Failed to update meal: {error_message}")
        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Failed to update meal: {e}")

    def delete_meal(self):
        try:
            row = self.ui.table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a meal to delete!")
                return
            meal_id = int(self.ui.table.item(row, 0).text())
            confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                changes, error_message = self.db.delete_meal(meal_id)
                if changes > 0:
                    QMessageBox.information(self, "Deleted", "Meal deleted successfully.")
                    self.load_table()
                    self.ui.clear_inputs()
                    self.current_meal_id = None
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete meal: {error_message}")
        except Exception as e:
            QMessageBox.critical(self, "Delete Error", f"Failed to delete meal: {e}")

    def export_to_csv(self):
        try:
            csv_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "meals_export.csv", "CSV Files (*.csv)")
            if csv_path:
                path, error_message = self.db.export_to_csv(csv_path)
                if path:
                    QMessageBox.information(self, "Export Success", f"Data exported to {path}")
                else:
                    QMessageBox.warning(self, "Export Failed", f"Export failed: {error_message}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")

    def load_table(self):
        try:
            self.ui.table.setRowCount(0)
            meals = self.db.get_all_meals()
            self.update_expired_notes(meals)
            meals = self.db.get_all_meals()
            meals.sort(key=lambda x: datetime.strptime(x[3], "%Y-%m-%d"), reverse=(self.sort_order == "newest"))
            for meal in meals:
                self.insert_row(meal)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load table: {e}")

    def filter_table(self):
        try:
            search_text = self.ui.search_input.text().lower()
            self.ui.table.setRowCount(0)
            meals = self.db.search_meals(search_text)
            self.update_expired_notes(meals)
            meals = self.db.search_meals(search_text)
            meals.sort(key=lambda x: datetime.strptime(x[3], "%Y-%m-%d"), reverse=(self.sort_order == "newest"))
            for meal in meals:
                self.insert_row(meal)
        except Exception as e:
            QMessageBox.critical(self, "Filter Error", f"Failed to filter table: {e}")

    def insert_row(self, meal):
        category_colors = {
            "Breakfast": QColor("#FFF9C4"),
            "Lunch": QColor("#C8E6C9"),
            "Dinner": QColor("#B3E5FC"),
            "Snack": QColor("#E2BAED")
        }
        today = datetime.now().date()
        row = self.ui.table.rowCount()
        self.ui.table.insertRow(row)
        try:
            prep_date = datetime.strptime(meal[3], "%Y-%m-%d").date()
        except ValueError:
            prep_date = today
        days_since = (today - prep_date).days
        expired = days_since > 5
        bg_color = QColor("#363131") if expired else category_colors.get(meal[2], QColor("#FFFFFF"))
        fg_color = QColor("#FFFFFF") if expired else QColor("#000000")
        for col, value in enumerate(meal):
            if col == 6 and expired:
                value = "EXPIRED"
            elif col == 6 and len(value) > 20:
                value = value[:20] + "..."
            item = QTableWidgetItem(str(value))
            item.setBackground(bg_color)
            item.setForeground(fg_color)
            self.ui.table.setItem(row, col if col < 4 else col + 1, item)
        days_item = QTableWidgetItem(str(days_since))
        days_item.setBackground(bg_color)
        days_item.setForeground(fg_color)
        self.ui.table.setItem(row, 4, days_item)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda _, r=row: self.load_meal_for_edit(r))
        self.ui.table.setCellWidget(row, 8, edit_btn)

    def load_meal_for_edit(self, row):
        try:
            self.current_meal_id = int(self.ui.table.item(row, 0).text())
            self.ui.dish_input.setText(self.ui.table.item(row, 1).text())
            self.ui.category_input.setCurrentText(self.ui.table.item(row, 2).text())
            date_parts = self.ui.table.item(row, 3).text().split("-")
            self.ui.prep_date_input.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            self.ui.portion_input.setValue(int(self.ui.table.item(row, 5).text()))
            self.ui.storage_input.setCurrentText(self.ui.table.item(row, 6).text())
            meal = next((m for m in self.db.get_all_meals() if m[0] == self.current_meal_id), None)
            self.ui.notes_input.setPlainText(meal[6] if meal else "")
            self.ui.save_button.setEnabled(False)
            self.ui.update_button.setEnabled(True)
            self.ui.delete_button.setEnabled(True)
            self.ui.table.selectRow(row)
        except Exception as e:
            QMessageBox.critical(self, "Edit Load Error", f"Failed to load meal for editing: {e}")

    def update_expired_notes(self, meals):
        today = datetime.now().date()
        for meal in meals:
            try:
                prep_date = datetime.strptime(meal[3], "%Y-%m-%d").date()
                if (today - prep_date).days > 5 and meal[6] != "EXPIRED":
                    self.db.update_notes(meal[0], "EXPIRED")
            except ValueError:
                continue

    def sort_table(self, sort_text):
        self.sort_order = "newest" if sort_text == "Newest First" else "oldest"
        self.load_table()

    def closeEvent(self, event):
        try:
            self.db.close()
            event.accept()
        except Exception as e:
            QMessageBox.critical(self, "Close Error", f"Failed to close database: {e}")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MealPrepApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application startup error: {e}")