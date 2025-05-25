from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

class MealPrepUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        content_frame = QFrame()
        content_layout = QVBoxLayout()
        content_frame.setLayout(content_layout)
        content_frame.setStyleSheet("""
            QFrame { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 #FFF3E0, stop:1 #FFCCBC); 
                border-radius: 5px;
            }
        """)
        content_frame.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=10, xOffset=2, yOffset=2))
        main_layout.addWidget(content_frame)

        header_label = QLabel("🍽️ Meal Prep Planner")
        header_label.setFont(QFont("Poppins", 24, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #D32F2F; margin: 10px; background-color: transparent;")
        content_layout.addWidget(header_label)

        main_widget = QWidget()
        main_layout_inner = QHBoxLayout()
        main_widget.setLayout(main_layout_inner)
        content_layout.addWidget(main_widget)

        form_widget = QFrame()
        form_layout = QVBoxLayout()
        form_widget.setLayout(form_layout)

        self.dish_input = QLineEdit()
        self.dish_input.setPlaceholderText("Dish Name")
        form_layout.addWidget(QLabel("🍲 Dish Name:"))
        form_layout.addWidget(self.dish_input)

        self.category_input = QComboBox()
        self.category_input.addItems(["Breakfast", "Lunch", "Dinner", "Snack"])
        form_layout.addWidget(QLabel("🗂️ Category:"))
        form_layout.addWidget(self.category_input)

        self.prep_date_input = QDateEdit()
        self.prep_date_input.setCalendarPopup(True)
        self.prep_date_input.setDate(QDate.currentDate())
        form_layout.addWidget(QLabel("📅 Prep Date:"))
        form_layout.addWidget(self.prep_date_input)

        self.portion_input = QSpinBox()
        self.portion_input.setRange(1, 10)
        self.portion_input.setValue(1)
        form_layout.addWidget(QLabel("🔢 Portion Size:"))
        form_layout.addWidget(self.portion_input)

        self.storage_input = QComboBox()
        self.storage_input.addItems(["Fridge", "Freezer", "Pantry"])
        form_layout.addWidget(QLabel("📦 Storage Location:"))
        form_layout.addWidget(self.storage_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter ingredients or notes...")
        self.notes_input.setFixedHeight(60)
        form_layout.addWidget(QLabel("📝 Notes:"))
        form_layout.addWidget(self.notes_input)

        self.save_button = QPushButton("Add")
        form_layout.addWidget(self.save_button)

        self.update_button = QPushButton("Update")
        self.update_button.setEnabled(False)
        form_layout.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setEnabled(False)
        form_layout.addWidget(self.delete_button)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.setStyleSheet("""
            QPushButton { 
                background-color: #FF8A80; 
                color: white; 
                padding: 10px; 
                border-radius: 5px; 
                font-family: Roboto; 
            }
            QPushButton:hover { 
                background-color: #F4511E; 
            }
        """)
        form_layout.addWidget(self.export_button)

        self.student_label = QLabel("Created by: Dhinda Tsamara S., NIM: F1D022005")
        form_layout.addWidget(self.student_label)
        form_layout.addStretch()

        form_widget.setStyleSheet("""
            QFrame { 
                background-color: white; 
                border-radius: 7px; 
                padding: 3px 0px 0px 0px;
            }
        """)
        form_widget.setGraphicsEffect(QGraphicsDropShadowEffect(blurRadius=10, xOffset=2, yOffset=2))
        form_widget.setFixedWidth(350)
        main_layout_inner.addWidget(form_widget)

        table_layout = QVBoxLayout()
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Newest First", "Oldest First"])
        self.sort_combo.setCurrentText("Newest First")
        table_layout.addWidget(self.sort_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by dish name...")
        table_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Dish Name", "Category", "Prep Date", 
                                             "Days Since Prep", "Portion", "Storage", "Notes", ""])
        self.table.setMinimumWidth(870)
        column_widths = [50, 150, 100, 100, 120, 80, 100, 150, 60]
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)
        table_layout.addWidget(self.table)

        main_layout_inner.addLayout(table_layout)

        self.setStyleSheet("""
            QWidget { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 #FFF3E0, stop:1 #FFCCBC); 
            }
            QLabel { 
                color: #D32F2F; 
                font-family: Roboto; 
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox { 
                background-color: white; 
                color: #D32F2F; 
                border: 1px solid #FF8A80; 
                padding: 5px; 
                border-radius: 3px; 
            }
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                padding: 8px; 
                border-radius: 5px; 
                font-family: Roboto; 
            }
            QPushButton:hover { 
                background-color: #388E3C; 
                transition: background-color 0.2s; 
            }
            QPushButton#update_button { 
                background-color: #0288D1; 
            }
            QPushButton#update_button:hover { 
                background-color: #01579B; 
            }
            QPushButton#delete_button { 
                background-color: #D32F2F; 
            }
            QPushButton#delete_button:hover { 
                background-color: #B71C1C; 
            }
            QTableWidget { 
                background-color: transparent; 
                color: #000000; 
                gridline-color: black; 
                border-radius: 5px; 
            }
            QHeaderView::section { 
                background-color: #FF8A80; 
                color: black; 
                padding: 5px; 
            }
        """)
        self.delete_button.setObjectName("delete_button")
        self.update_button.setObjectName("update_button")
        self.export_button.setObjectName("export_button")

    def clear_inputs(self):
        self.dish_input.clear()
        self.category_input.setCurrentIndex(0)
        self.prep_date_input.setDate(QDate.currentDate())
        self.portion_input.setValue(1)
        self.storage_input.setCurrentIndex(0)
        self.notes_input.clear()
        self.delete_button.setEnabled(False)
        self.update_button.setEnabled(False)