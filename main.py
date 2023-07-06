# Import PyQt5's widgets to be used throughout the program
import io
import math
import os
import shutil
import sqlite3
from datetime import time
import time

import canvas as canvas
# folium v0.12.1 - Used to display geographical data
import folium
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets, QtWebEngineWidgets, QtPrintSupport
from PyQt5.QtCore import Qt, QRunnable, pyqtSlot, QThreadPool, QUrl, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QDesktopServices, QPainter, QPainterPath, QTextOption
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *
from folium.plugins import MarkerCluster
import hashlib
# import class functions
import create_widget_functions
import user_details
from create_widget_functions import VerticalTabWidget, ChatGPTWindowWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.backends.backend_pdf as pdf_backend
from openpyxl import Workbook

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

REDEEM_BUTTON_STYLESHEET = '''
                        QPushButton {
                            background-color: rgb(12, 96, 50);
                            color: white;
                            border-radius:10px; 
                            font-size:10pt
                        }

                        QPushButton:hover {
                            background-color: gray;
                        }
                    '''

PROFILE_BUTTON_STYLESHEET = '''
                        QPushButton {
                            background-color: rgb(12, 96, 50);
                            color: white;
                            border-radius:25px; 
                            font-size:10pt
                        }

                        QPushButton:hover {
                            background-color: gray;
                        }
                    '''

SEND_BUTTON_STYLESHEET = '''
                        QPushButton {
                            background-color: rgb(12, 96, 50);
                            color: white;
                            border-radius:15px; 
                            font-size:10pt
                        }

                        QPushButton:hover {
                            background-color: gray;
                        }
                    '''

RESOLVED_BUTTON_STYLESHEET = '''
                        QPushButton {
                            background-color: rgb(12, 96, 50);
                            color: white;
                            border-radius:10px; 
                            font-size:10pt
                        }

                        QPushButton:hover {
                            background-color: gray;
                        }
                    '''



sqliteConnection = sqlite3.connect('identifier.sqlite')
cursor = sqliteConnection.cursor()
sqlite_select_query = """SELECT * from events"""
cursor.execute(sqlite_select_query)
events = cursor.fetchall()

cursor.execute("SELECT *, RANK() OVER(ORDER BY points DESC) 'Rank' from students")
students = cursor.fetchall()

cursor.execute("SELECT FIRST_NAME, LAST_NAME, POINTS FROM students")
student_rows = cursor.fetchall()

first_name = ""
last_name = ""

output_file = 'output_file.xlsx'
if os.path.exists(output_file):
    os.remove(output_file)
    print(f"Deleted existing file: {output_file}")

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

workbook = Workbook()

for table in tables:
    table_name = table[0]
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    results = cursor.fetchall()

    # Create a new sheet for each table
    sheet = workbook.create_sheet(title=table_name)

    # Write the headers
    headers = [description[0] for description in cursor.description]
    sheet.append(headers)

    # Write the data rows
    for row in results:
        sheet.append(row)

# Save the workbook to an Excel file
workbook.save('output_file.xlsx')


# Create a new excel file the day before presenting !!!!VERY IMPORTANT!!!!!
def sort_key(student_rows):
    return student_rows[2]


student_rows.sort(key=sort_key, reverse=True)
cursor.close()

event_combobox_selection = ""
rating_combobox_selection = ""
description_box = ""

name_annoucement_text_stuff = ""
details_annoucement_text_stuff = ""

"""
Class that sets up the main window for the entire application.
The entire frame with all it's elements are implemented in this class."""


class ResolvePopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Resolution")
        layout = QVBoxLayout(self)

        self.text_field = QLineEdit(self)
        layout.addWidget(self.text_field)

        submit_button = QPushButton("Submit", self)
        layout.addWidget(submit_button)

        submit_button.clicked.connect(self.handle_resolution)

    def handle_resolution(self):
        resolution = self.text_field.text()
        first_name = "Wallace"
        last_name = "McCarthy"
        points = 0
        status = "N/A"

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        query = "INSERT INTO main.NOTIFICATIONS (points, description, first_name, last_name, status) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (points, resolution, first_name, last_name, status))

        print("Inserted into notifications")

        sqliteConnection.commit()
        cursor.close()
        self.accept()


class Main(object):
    """
  Main Method that sets up the main window for the entire application, and takes
  the user to the actual program.
  """
    def setup_window(self, main_window):
        main_window.setWindowTitle("Spirit Quest")
        main_window.setObjectName("main_window")
        icon = QIcon("Application Pictures and Icons/gold-medal.png")
        main_window.setWindowIcon(icon)
        main_window.setFixedSize(800, 500)
        self.setup_login_screen(main_window)

    # Sets up the initial login screen
    """
    This method sets up the login screen of the program, and all physical 
    characteristics of the frame are made here.
    """

    def setup_login_screen(self, main_window):
        self.login_central_widget = QtWidgets.QWidget(main_window)
        self.login_central_widget.resize(800, 500)
        self.login_screen_background = QtWidgets.QLabel(self.login_central_widget)
        self.login_screen_background.setFixedSize(810, 500)
        self.login_screen_background.setPixmap(QtGui.QPixmap(r"Application Pictures and Icons/Login Screen Background.png"))

        self.login_screen_background.setScaledContents(True)
        self.login_screen_background.show()
        self.login_widget_container = QtWidgets.QGroupBox(self.login_central_widget)
        self.login_widget_container.resize(800, 500)

        # Application Logo
        self.login_screen_logo = QtWidgets.QLabel(self.login_widget_container)
        self.login_screen_logo.setFixedSize(200, 200)
        self.login_screen_logo.move(-20, -75)
        self.login_screen_logo.setScaledContents(True)
        self.login_screen_logo.show()

        # Student Login
        self.student_login_title = self.create_QLabel("login_widget_container", "login_titles", "Student Login", 105,
                                                      80, 300, 50)
        self.student_login_title.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.student_username_label = self.create_QLabel("login_widget_container", "login_screen_labels", "Email ID",
                                                         80, 122, 200, 50)
        self.student_username = self.create_QLineEdit("login_widget_container", "login_screen_text_fields", False, 80,
                                                      160, 240, 30)
        self.student_password_label = self.create_QLabel("login_widget_container", "login_screen_labels", "Password",
                                                         80, 187, 200, 50)
        # Student Password
        self.student_password = PasswordLineEdit(self.login_widget_container)
        self.student_password.setObjectName("login_screen_text_fields")
        self.student_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.student_password.setGeometry(QtCore.QRect(80, 225, 240, 30))
        student_password = self.student_password.text()  # Get the student password
        hashed_student_password = hashlib.sha256(student_password.encode()).hexdigest()  # Hash the password

        # end eye try
        self.student_forgot_password = self.create_QPushButton("login_widget_container", "login_screen_forgot_password",
                                                               "Forgot password?", "None", 65, 255, 140, 30)
        self.student_forgot_password.clicked.connect(self.setup_forgot_password)
        self.student_incorrect_login = self.create_QLabel("login_widget_container", "incorrect_login",
                                                          "Email ID and/or Password Icorrect. Please enter correct credentials.",
                                                          82, 275, 240, 50)
        self.student_incorrect_login.setWordWrap(True)
        self.student_incorrect_login.hide()
        self.student_login_button = self.create_QPushButton("login_widget_container", "student_login_button", "Login",
                                                            "None", 80, 290, 240, 30)
        self.student_login_button.clicked.connect(self.setup_portal)
        self.student_login_button.setStyleSheet("QPushButton {border-radius: 15px;}")
        self.student_or_label = self.create_QLabel("login_widget_container", "login_screen_labels", "or", 190, 310, 40,
                                                   50)
        self.student_create_account = self.create_QPushButton("login_widget_container", "student_login_button",
                                                              "Create a Student Account", "None", 80, 350, 240, 30)

        self.student_create_account.clicked.connect(self.setup_student_account_creation)
        self.student_create_account.setStyleSheet("QPushButton {border-radius: 15px;}")
        # Line divider between logins
        self.login_divider_line = self.create_QFrame("login_widget_container", "login_screen_elements", "VLine", 399,
                                                     40, 1, 410)

        # Administrator Login
        self.administrator_login_title = self.create_QLabel("login_widget_container", "login_titles",
                                                            "Administrator Login", 460, 80, 350, 50)
        self.administrator_login_title.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.administrator_username_label = self.create_QLabel("login_widget_container", "login_screen_labels",
                                                               "Email ID", 480, 122, 200, 50)
        self.administrator_username = self.create_QLineEdit("login_widget_container", "login_screen_text_fields", False,
                                                            480, 160, 240, 30)
        self.administrator_password_label = self.create_QLabel("login_widget_container", "login_screen_labels",
                                                               "Password", 480, 187, 200, 50)
        # Administrator Password eye stuff
        self.administrator_password = PasswordLineEdit(self.login_widget_container)
        self.administrator_password.setObjectName("login_screen_text_fields")
        self.administrator_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.administrator_password.setGeometry(QtCore.QRect(480, 225, 240, 30))
        admin_password = self.administrator_password.text()  # Get the admin password
        hashed_admin_password = hashlib.sha256(admin_password.encode()).hexdigest()

        self.administrator_forgot_password = self.create_QPushButton("login_widget_container",
                                                                     "login_screen_forgot_password", "Forgot password?",
                                                                     "None", 465, 255, 140, 30)
        self.administrator_forgot_password.clicked.connect(self.admin_forgot_password_page)
        self.administrator_incorrect_login = self.create_QLabel("login_widget_container", "incorrect_login",
                                                                "Email ID and/or Password Icorrect. Please enter correct credentials.",
                                                                482, 275, 240, 50)
        self.administrator_incorrect_login.setWordWrap(True)
        self.administrator_incorrect_login.hide()
        self.administrator_login_button = self.create_QPushButton("login_widget_container",
                                                                  "administrator_login_button", "Login", "None", 480,
                                                                  290, 240, 30)
        self.administrator_login_button.clicked.connect(self.setup_portal)
        self.administrator_login_button.setStyleSheet("QPushButton {border-radius: 15px;}")
        self.administrator_or_label = self.create_QLabel("login_widget_container", "login_screen_labels", "or", 590,
                                                         310, 40, 50)
        self.administrator_create_account = self.create_QPushButton("login_widget_container",
                                                                    "administrator_login_button",
                                                                    "Create an Administrator Account", "None", 480, 350,
                                                                    240, 30)
        self.administrator_create_account.clicked.connect(self.setup_administrator_account_creation)
        self.administrator_create_account.setStyleSheet("QPushButton {border-radius: 15px;}")
        main_window.setStatusBar(None)

    def setup_student_account_creation(self):
        self.student_account_frame = QtWidgets.QLabel()
        self.student_account_frame.setWindowTitle("Create Student Account")
        self.student_account_frame.setFixedSize(1200, 500)
        self.student_account_frame.move(100, 20)
        self.student_account_frame.setPixmap(QtGui.QPixmap(r"Application Pictures and Icons/Login Screen Background.png").scaledToWidth(1200))

        self.student_account_label = self.create_QLabel("student_account_frame", "student_account_label",
                                                        "Create Student Account", 20, 20, 600, 50)
        self.student_account_line = self.create_QFrame("student_account_frame", "student_account_line", "HLine", 10, 65,
                                                       600, 0)

        self.first_name_label = self.create_QLabel("student_account_frame", "first_name_label",
                                                   "First Name", 50, 120, 300, 30)

        self.first_name_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.first_name_entry.setGeometry(QtCore.QRect(150, 120, 200, 30))
        self.first_name_entry.setPlaceholderText("First Name")

        self.last_name_label = self.create_QLabel("student_account_frame", "last_name_label",
                                                  "Last Name", 55, 200, 300, 30)

        self.username_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.username_entry.setGeometry(QtCore.QRect(150, 200, 200, 30))
        self.username_entry.setPlaceholderText("Last Name")

        self.create_email_label = self.create_QLabel("student_account_frame", "create_email_label",
                                                     "Email Address", 40, 280, 300, 30)

        self.create_email_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.create_email_entry.setGeometry(QtCore.QRect(150, 280, 200, 30))
        self.create_email_entry.setPlaceholderText("Email Address")

        self.create_password_label = self.create_QLabel("student_account_frame", "create_password_label",
                                                        "Password", 55, 360, 300, 30)

        self.create_password_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.create_password_entry.setGeometry(QtCore.QRect(150, 360, 200, 30))
        self.create_password_entry.setPlaceholderText("Password")

        self.birthday_label = self.create_QLabel("student_account_frame", "birthday_label",
                                                 "Birthday (MM/DD/YY)", 370, 120, 300, 30)

        self.birthday_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.birthday_entry.setGeometry(QtCore.QRect(550, 120, 200, 30))
        self.birthday_entry.setPlaceholderText("Birthday (MM/DD/YY)")

        self.school_label = self.create_QLabel("student_account_frame", "school_label",
                                               "School", 370, 200, 300, 30)

        self.school_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.school_entry.setGeometry(QtCore.QRect(430, 200, 200, 30))
        self.school_entry.setPlaceholderText("School")

        self.grade_combobox = QComboBox(self.student_account_frame)
        self.grade_combobox.setGeometry(640, 200, 110, 30)
        self.grade_combobox.addItem("Choose Grade")
        self.grade_combobox.addItem("9")
        self.grade_combobox.addItem("10")
        self.grade_combobox.addItem("11")
        self.grade_combobox.addItem("12")
        self.grade_combobox.setCurrentIndex(0)

        self.security_combobox_label = self.create_QLabel("student_account_frame", "security_combobox_label",
                                                          "Security Question", 370, 280, 300, 30)

        self.security_combobox = QComboBox(self.student_account_frame)
        self.security_combobox.setGeometry(550, 280, 200, 30)
        self.security_combobox.addItem("Choose Security Question")
        self.security_combobox.addItem("What is your favorite color?")
        self.security_combobox.addItem("What is your favorite sports team?")
        self.security_combobox.addItem("What year was your first rock climbing nationals?")
        self.security_combobox.addItem("What is your mother's maiden name?")
        self.security_combobox.setCurrentIndex(0)

        self.create_answer_label = self.create_QLabel("student_account_frame", "create_answer_label",
                                                      "Answer", 370, 360, 300, 30)

        self.create_answer_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.create_answer_entry.setGeometry(QtCore.QRect(550, 360, 200, 30))
        self.create_answer_entry.setPlaceholderText("Answer")

        self.emergency_name_label = self.create_QLabel("student_account_frame", "emergency_name_label",
                                                       "Emergency Name", 800, 120, 300, 30)

        self.emergency_name_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.emergency_name_entry.setGeometry(QtCore.QRect(960, 120, 200, 30))
        self.emergency_name_entry.setPlaceholderText("Emergency Name")

        self.emergency_phone_label = self.create_QLabel("student_account_frame", "emergency_phone_label",
                                                        "Emergency Phone", 800, 200, 300, 30)

        self.emergency_phone_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.emergency_phone_entry.setGeometry(QtCore.QRect(960, 200, 200, 30))
        self.emergency_phone_entry.setPlaceholderText("Emergency Phone")

        self.emergency_email_label = self.create_QLabel("student_account_frame", "emergency_email_label",
                                                        "Emergency Email", 800, 280, 300, 30)

        self.emergency_email_entry = QtWidgets.QLineEdit(self.student_account_frame)
        self.emergency_email_entry.setGeometry(QtCore.QRect(960, 280, 200, 30))
        self.emergency_email_entry.setPlaceholderText("Emergency Email")

        self.gender_label = self.create_QLabel("student_account_frame", "gender_label",
                                               "Gender", 800, 360, 300, 30)

        self.gender_combobox = QComboBox(self.student_account_frame)
        self.gender_combobox.setGeometry(960, 360, 200, 30)
        self.gender_combobox.addItem("Select Gender")
        self.gender_combobox.addItem("Male")
        self.gender_combobox.addItem("Female")
        self.gender_combobox.addItem("Prefer not to say")
        self.gender_combobox.addItem("Other")
        self.gender_combobox.setCurrentIndex(0)

        self.create_account_button = QtWidgets.QPushButton("Create Account", self.student_account_frame)
        self.create_account_button.setGeometry(QtCore.QRect(460, 430, 260, 30))
        self.create_account_button.clicked.connect(self.create_student_account)
        #self.create_account_button.setStyleSheet(SEND_BUTTON_STYLESHEET)
        self.create_account_button.setObjectName("student_login_button")

        self.student_account_frame.show()

    def create_student_account(self):
        first_name = self.first_name_entry.text()
        last_name = self.username_entry.text()
        email = self.create_email_entry.text()
        password = self.create_password_entry.text()
        birthday = self.birthday_entry.text()
        school = self.school_entry.text()
        grade = self.grade_combobox.currentText()
        security_question = self.security_combobox.currentText()
        answer = self.create_answer_entry.text()
        emergency_name = self.emergency_name_entry.text()
        emergency_phone = self.emergency_phone_entry.text()
        emergency_email = self.emergency_email_entry.text()
        gender = self.gender_combobox.currentText()

        try:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            query = "INSERT INTO students (FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PASSWORD, BIRTHDAY, SCHOOL, GRADE, SECURITY_QUESTION, SECURITY_ANSWER, EMERGENCY_CONTACT_NAME, EMERCENCY_CONTACT_PHONE_NUMBER, EMERGENCY_CONTACT_EMAIL, GENDER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query,
                           (first_name, last_name, email, password, birthday, school, grade, security_question, answer,
                            emergency_name, emergency_phone, emergency_email, gender))
            sqliteConnection.commit()

            self.student_account_frame.close()

            registration = QMessageBox()
            registration.setText("Thanks for registration")
            registration.setIcon(QMessageBox.Information)
            registration.exec_()

        except sqlite3.Error as error:
            print("Error while connecting to SQLite database:", error)

        finally:
            if sqliteConnection:
                sqliteConnection.close()

    def setup_forgot_password(self):
        self.forgot_password_frame = QtWidgets.QLabel()
        self.forgot_password_frame.setWindowTitle("Forgot Password")
        self.forgot_password_frame.setFixedSize(800, 500)
        self.forgot_password_frame.move(108, 24)
        self.forgot_password_frame.setPixmap(QPixmap(r"Application Pictures and Icons/Login Screen Background.png").scaledToWidth(800))

        self.forgot_password_label = self.create_QLabel("forgot_password_frame", "forgot_password_label",
                                                        "Forgot Password", 20, 70, 600, 50)
        # self.forgot_password_line = self.create_QFrame("forgot_password_frame", "forgot_password_line", "HLine", 10, 65,
        #                                                600, 6)

        self.email_label = self.create_QLabel("forgot_password_frame", "email_label", "Email", 20, 150, 80, 30)

        self.email_entry = QtWidgets.QLineEdit(self.forgot_password_frame)
        self.email_entry.setGeometry(QtCore.QRect(200, 150, 170, 30))

        self.email_search_button = QtWidgets.QPushButton("  Search", self.forgot_password_frame)
        self.email_search_button.setGeometry(QtCore.QRect(400, 150, 150, 30))
        self.email_search_button.clicked.connect(self.search_security_question)
        self.email_search_button.setIcon(QIcon(r"Application Pictures and Icons/search-12-filled.svg"))

        self.security_question_label = self.create_QLabel("forgot_password_frame", "security_question_label",
                                                          "Security Question", 20, 220, 200, 30)

        self.security_question_entry = QtWidgets.QLineEdit(self.forgot_password_frame)
        self.security_question_entry.setGeometry(QtCore.QRect(200, 220, 350, 30))

        self.answer_label = self.create_QLabel("forgot_password_frame", "answer_label", "Answer", 20, 290, 90, 30)

        self.security_answer_entry = QtWidgets.QLineEdit(self.forgot_password_frame)
        self.security_answer_entry.setGeometry(QtCore.QRect(200, 290, 350, 30))

        self.new_password_label = self.create_QLabel("forgot_password_frame", "new_password_label", "New Password", 20,
                                                     360, 150, 30)

        self.new_password_entry = QtWidgets.QLineEdit(self.forgot_password_frame)
        self.new_password_entry.setGeometry(QtCore.QRect(200, 360, 350, 30))

        self.change_password_button = QtWidgets.QPushButton("Change Password", self.forgot_password_frame)
        self.change_password_button.setGeometry(QtCore.QRect(300, 420, 200, 30))
        self.change_password_button.clicked.connect(self.change_password)
        self.change_password_button.setObjectName("student_login_button")

        self.forgot_password_frame.show()

    def search_security_question(self):
        email_string = self.email_entry.text()

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute("SELECT SECURITY_QUESTION FROM students WHERE EMAIL_ADDRESS = ?", (email_string,))
        data = cursor.fetchone()

        if data:
            security_question = data[0]
            self.security_question_entry.setText(security_question)
        else:
            no_security_question = QMessageBox()
            no_security_question.setText("Email not found")
            no_security_question.setIcon(QMessageBox.Warning)
            no_security_question.exec_()

            self.email_entry.clear()

    def change_password(self):
        email_string = self.email_entry.text()
        new_password_string = self.new_password_entry.text()
        answer_string = self.security_answer_entry.text()

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute("SELECT SECURITY_ANSWER FROM students WHERE EMAIL_ADDRESS = ?", (email_string,))
        answer = cursor.fetchone()

        if answer:
            if (answer[0] == answer_string):
                cursor.execute("UPDATE students SET PASSWORD = ? WHERE EMAIL_ADDRESS = ? AND SECURITY_ANSWER = ?",
                               (new_password_string, email_string, answer_string))
                sqliteConnection.commit()

                updated_password = QMessageBox()
                updated_password.setText("Your Password has been updated!")
                updated_password.setIcon(QMessageBox.Information)
                updated_password.exec_()
            else:
                wrong_answer = QMessageBox()
                wrong_answer.setText("Incorrect information provided")
                wrong_answer.setIcon(QMessageBox.Warning)
                wrong_answer.exec_()

    def setup_administrator_account_creation(self):
        self.admin_account_frame = QtWidgets.QLabel()
        self.admin_account_frame.setWindowTitle("Create Administrator Account")
        self.admin_account_frame.setFixedSize(800, 500)
        self.admin_account_frame.setPixmap(QPixmap(r"Application Pictures and Icons/Login Screen Background.png").scaledToWidth(800))
        self.admin_account_frame.move(100, 20)

        self.student_account_label = self.create_QLabel("admin_account_frame", "student_account_label",
                                                        "Create Administrator Account", 160, 20, 600, 50)
        self.student_account_line = self.create_QFrame("admin_account_frame", "student_account_line", "HLine", 10, 65,
                                                       600, 0)
        #self.student_account_label.setStyleSheet("font-family:Roboto; color: white")

        self.first_name_label = self.create_QLabel("admin_account_frame", "first_name_label",
                                                   "First Name", 50, 120, 300, 30)

        self.login_screen_logo = QtWidgets.QLabel(self.admin_account_frame)
        self.login_screen_logo.setFixedSize(200, 200)
        self.login_screen_logo.move(-20, -75)
        self.login_screen_logo.setScaledContents(True)
        self.login_screen_logo.show()

        self.first_name_entry = QtWidgets.QLineEdit(self.admin_account_frame)
        self.first_name_entry.setGeometry(QtCore.QRect(150, 120, 200, 30))
        self.first_name_entry.setPlaceholderText("First Name")

        self.last_name_label = self.create_QLabel("admin_account_frame", "last_name_label",
                                                  "Last Name", 55, 200, 300, 30)

        self.username_entry = QtWidgets.QLineEdit(self.admin_account_frame)
        self.username_entry.setGeometry(QtCore.QRect(150, 200, 200, 30))
        self.username_entry.setPlaceholderText("Last Name")

        self.create_email_label = self.create_QLabel("admin_account_frame", "create_email_label",
                                                     "Email Address", 40, 280, 300, 30)

        self.create_email_entry = QtWidgets.QLineEdit(self.admin_account_frame)
        self.create_email_entry.setGeometry(QtCore.QRect(150, 280, 200, 30))
        self.create_email_entry.setPlaceholderText("Email Address")

        self.create_password_label = self.create_QLabel("admin_account_frame", "create_password_label",
                                                        "Password", 55, 360, 300, 30)

        self.create_password_entry = QtWidgets.QLineEdit(self.admin_account_frame)
        self.create_password_entry.setGeometry(QtCore.QRect(150, 360, 200, 30))
        self.create_password_entry.setPlaceholderText("Password")

        self.birthday_label = self.create_QLabel("admin_account_frame", "birthday_label",
                                                 "Birthday (MM/DD/YY)", 370, 120, 300, 30)

        self.birthday_entry = QtWidgets.QLineEdit(self.admin_account_frame)
        self.birthday_entry.setGeometry(QtCore.QRect(550, 120, 200, 30))
        self.birthday_entry.setPlaceholderText("Birthday (MM/DD/YY)")

        self.school_label = self.create_QLabel("admin_account_frame", "school_label",
                                               "School", 470, 200, 300, 30)

        self.school_entry = QtWidgets.QLineEdit(self.admin_account_frame)
        self.school_entry.setGeometry(QtCore.QRect(550, 200, 200, 30))
        self.school_entry.setPlaceholderText("School")

        self.security_combobox_label = self.create_QLabel("admin_account_frame", "security_combobox_label",
                                                          "Security Question", 400, 280, 300, 30)

        self.security_combobox = QComboBox(self.admin_account_frame)
        self.security_combobox.setGeometry(550, 280, 200, 30)
        self.security_combobox.addItem("Choose Security Question")
        self.security_combobox.addItem("What is your favorite color?")
        self.security_combobox.addItem("What is your favorite sports team?")
        self.security_combobox.addItem("What year was your first rock climbing nationals?")
        self.security_combobox.addItem("What is your mother's maiden name?")
        self.security_combobox.setCurrentIndex(0)

        self.create_answer_label = self.create_QLabel("admin_account_frame", "create_answer_label",
                                                      "Answer", 450, 360, 300, 30)

        self.create_answer_entry = QtWidgets.QLineEdit(self.admin_account_frame)
        self.create_answer_entry.setGeometry(QtCore.QRect(550, 360, 200, 30))
        self.create_answer_entry.setPlaceholderText("Answer")

        self.create_account_button = QtWidgets.QPushButton("Create Account", self.admin_account_frame)
        self.create_account_button.setGeometry(QtCore.QRect(320, 430, 260, 30))
        self.create_account_button.clicked.connect(self.create_admin_account)
        #self.create_account_button.setStyleSheet(SEND_BUTTON_STYLESHEET)
        self.create_account_button.setObjectName("student_login_button")

        self.admin_account_frame.show()

    def create_admin_account(self):
        first_name = self.first_name_entry.text()
        last_name = self.username_entry.text()
        email = self.create_email_entry.text()
        password = self.create_password_entry.text()
        birthday = self.birthday_entry.text()
        school = self.school_entry.text()
        security_question = self.security_combobox.currentText()
        answer = self.create_answer_entry.text()
        print("hello")

        try:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            query = "INSERT INTO administrators (FIRST_NAME, LAST_NAME, EMAIL_ADDRESS, PASSWORD, BIRTHDAY, SCHOOL, SECURITY_QUESTION, SECURITY_ANSWER) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query,
                           (first_name, last_name, email, password, birthday, school, security_question, answer))
            sqliteConnection.commit()
            print("hello")

            self.admin_account_frame.close()

            registration = QMessageBox()
            registration.setText("Thanks for registration")
            registration.setIcon(QMessageBox.Information)
            registration.exec_()

        except sqlite3.Error as error:
            print("Error while connecting to SQLite database:", error)

        finally:
            if sqliteConnection:
                sqliteConnection.close()

    def admin_forgot_password_page(self):
        self.forgot_password_frame = QtWidgets.QLabel()
        self.forgot_password_frame.setWindowTitle("Forgot Password")
        self.forgot_password_frame.setFixedSize(800, 500)
        self.forgot_password_frame.move(108, 24)
        self.forgot_password_frame.setPixmap(QPixmap(r"Application Pictures and Icons/Login Screen Background.png").scaledToWidth(800))

        self.forgot_password_label = self.create_QLabel("forgot_password_frame", "forgot_password_label",
                                                        "Forgot Password", 20, 70, 600, 50)
        # self.forgot_password_line = self.create_QFrame("forgot_password_frame", "forgot_password_line", "HLine", 10, 65,
        #                                                600, 6)

        self.email_label = self.create_QLabel("forgot_password_frame", "email_label", "Email", 20, 150, 80, 30)

        self.email_entry = QtWidgets.QLineEdit(self.forgot_password_frame)
        self.email_entry.setGeometry(QtCore.QRect(200, 150, 170, 30))

        self.email_search_button = QtWidgets.QPushButton("  Search", self.forgot_password_frame)
        self.email_search_button.setGeometry(QtCore.QRect(400, 150, 150, 30))
        self.email_search_button.clicked.connect(self.admin_security_question)
        self.email_search_button.setIcon(QIcon(r"Application Pictures and Icons/search-12-filled.svg"))

        self.security_question_label = self.create_QLabel("forgot_password_frame", "security_question_label",
                                                          "Security Question", 20, 220, 200, 30)

        self.security_question_entry = QtWidgets.QLineEdit(self.forgot_password_frame)
        self.security_question_entry.setGeometry(QtCore.QRect(200, 220, 350, 30))

        self.answer_label = self.create_QLabel("forgot_password_frame", "answer_label", "Answer", 20, 290, 90, 30)

        self.security_answer_entry = QtWidgets.QLineEdit(self.forgot_password_frame)
        self.security_answer_entry.setGeometry(QtCore.QRect(200, 290, 350, 30))

        self.new_password_label = self.create_QLabel("forgot_password_frame", "new_password_label", "New Password", 20,
                                                     360, 150, 30)

        self.new_password_entry = QtWidgets.QLineEdit(self.forgot_password_frame)
        self.new_password_entry.setGeometry(QtCore.QRect(200, 360, 350, 30))

        self.change_password_button = QtWidgets.QPushButton("Change Password", self.forgot_password_frame)
        self.change_password_button.setGeometry(QtCore.QRect(300, 420, 200, 30))
        self.change_password_button.clicked.connect(self.change_admin_password)
        self.change_password_button.setObjectName("student_login_button")

        self.forgot_password_frame.show()

    """
    Gets the security question if the user ID is enter properly (Administrator side)
    """
    def admin_security_question(self):
        # Gets the email string
        email_string = self.admin_email_entry.text()

        # Connects to the database
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        # Executes the cursor
        cursor.execute("SELECT SECURITY_QUESTION FROM administrators WHERE EMAIL_ADDRESS = ?", (email_string,))
        data = cursor.fetchone()

        # If data is there, then add the security question and set the text
        if data:
            security_question = data[0]
            self.admin_security_question_entry.setText(security_question)
        # If it is not there, then we know they entered the wrong info
        else:
            no_security_question = QMessageBox()
            no_security_question.setText("Email not found")
            no_security_question.setIcon(QMessageBox.Warning)
            no_security_question.exec_()

            self.email_entry.clear()


    """
     Method that changes the admin password (similar to the student side)
    """
    def change_admin_password(self):
        # Retrieve the email, new password, and security answer entered by the user
        email_string = self.admin_email_entry.text()
        new_password_string = self.new_password_entry.text()
        answer_string = self.security_answer_entry.text()

        # Connect to the 'identifier.sqlite' database
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        # Execute a SELECT query to retrieve the security answer from the administrators table for the given email address
        cursor.execute("SELECT SECURITY_ANSWER FROM administrators WHERE EMAIL_ADDRESS = ?", (email_string,))
        answer = cursor.fetchone()

        # Check if a valid security answer was retrieved
        if answer:
            # Compare the retrieved security answer with the answer provided by the user
            if answer[0] == answer_string:
                # Update the password in the administrators table for the given email address and security answer
                cursor.execute("UPDATE administrators SET PASSWORD = ? WHERE EMAIL_ADDRESS = ? AND SECURITY_ANSWER = ?",
                               (new_password_string, email_string, answer_string))
                sqliteConnection.commit()

                # Show a message box indicating that the password has been updated successfully
                updated_password = QMessageBox()
                updated_password.setText("Your Password has been updated!")
                updated_password.setIcon(QMessageBox.Information)
                updated_password.exec_()
            else:
                # Show a message box indicating that the provided information is incorrect
                wrong_answer = QMessageBox()
                wrong_answer.setText("Incorrect information provided")
                wrong_answer.setIcon(QMessageBox.Warning)
                wrong_answer.exec_()
    """
    This method sets up the main frame of the system once the login verification has been passed
    """
    def setup_portal(self):
        global username  # Global variable to store the username
        global password  # Global variable to store the password
        global user  # Global variable to store user information

        sending_button = self.login_widget_container.sender().objectName()
        # Get the object name of the sender from the login_widget_container

        if sending_button == "student_login_button":
            # Check if the sending_button is the student login button
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            # Connect to the 'identifier.sqlite' database
            cursor = sqliteConnection.cursor()
 
            cursor.execute("SELECT EMAIL_ADDRESS, PASSWORD, FIRST_NAME, LAST_NAME FROM students")
            # Execute a SELECT query to retrieve data from the 'students' table
            student_rows = cursor.fetchall()
            # Fetch all the rows returned by the query
            cursor.close()

            for user in student_rows:
                # Iterate through the student rows
                if self.student_username.text() == user[0] and self.student_password.text() == user[1]:
                    # Check if the entered username and password match the current student row
                    self.initialize_student_page()
                    # Call the initialize_student_page method to set up the student page
                    break

            self.student_login_button.move(80, 320)
            # Adjust the position of the student login button
            self.student_or_label.move(190, 340)
            # Adjust the position of the student "or" label
            self.student_create_account.move(80, 380)
            # Adjust the position of the student create account button
            self.student_incorrect_login.show()
            # Show the student incorrect login message


        elif sending_button == "administrator_login_button":
            # Check if the sending_button is the administrator login button
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            # Connect to the 'identifier.sqlite' database
            cursor = sqliteConnection.cursor()

            cursor.execute("SELECT EMAIL_ADDRESS, PASSWORD FROM administrators")
            # Execute a SELECT query to retrieve data from the 'administrators' table
            admin_rows = cursor.fetchall()
            # Fetch all the rows returned by the query
            cursor.close()

            for user in admin_rows:
                # Iterate through the administrator rows
                if self.administrator_username.text() == user[0] and self.administrator_password.text() == user[1]:
                    # Check if the entered username and password match the current administrator row
                    self.initialize_administrator_page()
                    # Call the initialize_administrator_page method to set up the administrator page
                    break

            self.administrator_login_button.move(480, 320)
            # Adjust the position of the administrator login button
            self.administrator_or_label.move(590, 340)
            # Adjust the position of the administrator "or" label
            self.administrator_create_account.move(480, 380)
            # Adjust the position of the administrator create account button
            self.administrator_incorrect_login.show()
            # Show the administrator incorrect login message


    """
    Initializes the student page when users log in properly
    """
    def initialize_student_page(self):
        # Delete the login_central_widget
        self.login_central_widget.deleteLater()

        # Set the fixed size of the main_window
        main_window.setFixedSize(1150, 650)

        # Center the main_window on the screen
        qtRectangle = main_window.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        main_window.move(qtRectangle.topLeft())

        # Create and set up the central_widget with a background image
        self.central_widget = QtWidgets.QLabel(main_window)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.resize(1150, 650)
        self.central_widget.setPixmap(QtGui.QPixmap("Application Pictures and Icons/589.jpg"))

        # Create and position the tab_widget_panel
        self.tab_widget_panel = QtWidgets.QLabel(self.central_widget)
        self.tab_widget_panel.resize(178, 650)
        self.tab_widget_panel.move(0, 0)
        self.tab_widget_panel.setStyleSheet("background-color:#202020")

        # Create and position the app_logo
        self.app_logo = QtWidgets.QLabel(self.central_widget)
        self.app_logo.setFixedSize(140, 140)
        self.app_logo.move(20, 10)
        self.app_logo.setPixmap(QtGui.QPixmap("Application Pictures and Icons/Time_Track_Icon-removebg-preview.png"))
        self.app_logo.setScaledContents(True)
        self.app_logo.show()

        # Create and position the log_out_button
        self.log_out_button = self.create_QPushButton("central_widget", "log_out", "None",
                                                      "Application Pictures and Icons/Log Out.png", 980, -50, 160, 160)
        self.log_out_button.setIconSize(QtCore.QSize(150, 150))
        self.log_out_button.setFlat(True)
        self.log_out_button.clicked.connect(self.return_to_login_screen)

        # Connect to the 'identifier.sqlite' database and retrieve user details
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        # Setting the values to the database values
        username = user[0]
        password = user[1]
        first_name = user[2]
        last_name = user[3]
        # Execute the cursor
        cursor.execute(
            "SELECT * FROM students WHERE EMAIL_ADDRESS = ? AND PASSWORD = ? AND FIRST_NAME = ? AND LAST_NAME = ?",
            (username, password, first_name, last_name))
        self.logged_in_user_details = cursor.fetchall()
        cursor.close()

        # Set up the student page with the retrieved user details
        self.setup_student_page(first_name, last_name)
        main_window.setCentralWidget(self.central_widget)
        # self.status_bar = QtWidgets.QStatusBar(main_window)
        # main_window.setStatusBar(self.status_bar)

    """
    Initializes the administrator page when users log in properly
    """
    def initialize_administrator_page(self):
        # Delete the login central widget
        self.login_central_widget.deleteLater()

        # Set the size of the main window
        main_window.setFixedSize(1150, 650)

        # Create and set up the central widget
        self.central_widget = QtWidgets.QLabel(main_window)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.resize(1150, 650)
        self.central_widget.setPixmap(QtGui.QPixmap("Application Pictures and Icons/589.jpg"))

        # Create and set up the tab widget panel
        self.tab_widget_panel = QtWidgets.QLabel(self.central_widget)
        self.tab_widget_panel.resize(178, 650)
        self.tab_widget_panel.move(0, 0)
        self.tab_widget_panel.setStyleSheet("background-color:#202020")

        # Create and set up the application logo
        self.app_logo = QtWidgets.QLabel(self.central_widget)
        self.app_logo.setFixedSize(140, 140)
        self.app_logo.move(20, 10)
        self.app_logo.setPixmap(QtGui.QPixmap("Application Pictures and Icons/Time_Track_Icon-removebg-preview.png"))
        self.app_logo.setScaledContents(True)
        self.app_logo.show()

        # Create and set up the log out button
        self.log_out_button = self.create_QPushButton("central_widget", "log_out", "None",
                                                      "Application Pictures and Icons/Log Out.png", 980, -50, 160, 160)
        self.log_out_button.setIconSize(QtCore.QSize(150, 150))
        self.log_out_button.setFlat(True)
        self.log_out_button.clicked.connect(self.return_to_login_screen)

        # Set up the admin page
        self.setup_admin_page()

        # Set the central widget for the main window
        main_window.setCentralWidget(self.central_widget)

        # Uncomment the following lines if you want to create a status bar
        # Create and set up the status bar
        # self.status_bar = QtWidgets.QStatusBar(main_window)
        # main_window.setStatusBar(self.status_bar)

    def setup_student_page(self, first_name, last_name):
        global dashboard_slideshow
        global slideshow_title
        global slideshow_description
        global kill_thread_boolean
        global threadpool
        global map

        user_details.get_user_details.__init__(self)

        self.tab_widget = VerticalTabWidget(self.central_widget)
        self.tab_widget.setObjectName("tab_widget")
        self.tab_widget.resize(1150, 650)
        self.tab_widget.move(0, 55)

        self.dashboard_tab = QtWidgets.QLabel()
        self.upcoming_events_tab = QtWidgets.QWidget()
        self.maps_tab = QtWidgets.QWidget()
        self.points_tab = QtWidgets.QWidget()
        self.rewards_tab = QtWidgets.QWidget()
        self.community_tab = QtWidgets.QWidget()
        self.student_profile_tab = QtWidgets.QWidget()
        self.chatbot_tab = QtWidgets.QWidget()
        self.faq_tab = QtWidgets.QWidget()

        # panel = QtWidgets.QLabel(self.dashboard_tab)
        # panel.resize(1000,1000)
        # #panel.setStyleSheet("background-color:rgb(20,20,20)")
        # panel.setPixmap(QPixmap(r"C:\Users\lesli\OneDrive\Documents\GitHub\Test_time\Application Pictures and Icons\591.jpg").scaledToWidth(1000))

        self.tab_widget.addTab(self.dashboard_tab, QIcon(r"Application Pictures and Icons/dashboard-solid-badged.svg"), "Dashboard          ")
        self.tab_widget.addTab(self.upcoming_events_tab, QIcon(r"Application Pictures and Icons/calendar-fill.svg"), "Upcoming Events")
        self.tab_widget.addTab(self.maps_tab, QIcon(r"Application Pictures and Icons/map.svg"), "Maps              ")
        self.tab_widget.addTab(self.points_tab, QIcon(r"Application Pictures and Icons/crown-24-filled.svg"), "Points             ")
        self.tab_widget.addTab(self.rewards_tab, QIcon(r"Application Pictures and Icons/reward-12-filled.svg"), "Rewards            ")
        self.tab_widget.addTab(self.student_profile_tab, QIcon(r"Application Pictures and Icons/profile-fill.svg"), "My Student Profile")
        self.tab_widget.addTab(self.faq_tab, QIcon(r"Application Pictures and Icons/question.svg"), "FAQs               ")
        self.tab_widget.addTab(self.chatbot_tab, QIcon(r"Application Pictures and Icons/robot.svg"), "Spirit Assistant   ")

        # pixmap = QPixmap("Application Pictures and Icons/user (3).png")
        # self.user_icon_label = self.create_QLabel("central_widget", "user_icon_label",
        #                                       "", 200, 0, 50, 50)
        # self.user_icon_label.setPixmap(pixmap)

        # Dashboard Tab
        self.intro_label = self.create_QLabel("central_widget", "intro_label",
                                              "Signed in as " + first_name + " " + last_name, 200, 0, 600, 50)
        self.dashboard_label = self.create_QLabel("dashboard_tab", "dashboard_label", "Dashboard", 20, 20, 600, 50)
        self.dashboard_title_line = self.create_QFrame("dashboard_tab", "dashboard_title_line", "HLine", 10, 65, 580, 6)

        pixmap = QPixmap("Application Pictures and Icons/bell_icon_transparent.png")
        icon = QIcon(pixmap)
        notification_button = QPushButton(self.dashboard_tab)
        notification_button.setIcon(icon)
        notification_button.setIconSize(pixmap.size())
        notification_button.setGeometry(550, 20, 35, 38)
        notification_button.setStyleSheet("background-color: transparent; border: none;")
        notification_button.clicked.connect(self.show_notifications)

        dashboard_slideshow = self.create_QLabel("dashboard_tab", "dashboard_slider_label", "filler", 20, 90, 550,
                                                 320)  # changed
        dashboard_slideshow.setScaledContents(True)
        self.slideshow_description_groupbox = QtWidgets.QGroupBox(self.dashboard_tab)
        self.slideshow_description_groupbox.setGeometry(20, 420, 550, 110)  # 20, 580, 840, 100
        self.slideshow_description_groupbox.setStyleSheet("QGroupBox { border-radius: 3px; }")
        slideshow_title = self.create_QLabel("slideshow_description_groupbox", "slideshow_title", "", 10, 10, 530,
                                             30)  # 10, 10, 830, 20
        slideshow_title.setWordWrap(True)
        #slideshow_title.setStyleSheet("QLabel { background-color: rgba(255, 255, 255, 200); }")
        slideshow_description = self.create_QLabel("slideshow_description_groupbox", "slideshow_description", "", 10,
                                                   40, 530, 150)  # 10, 40, 830, 60
        #slideshow_description.setStyleSheet("QLabel { background-color: rgba(255, 255, 255, 200); }")
        slideshow_description.setWordWrap(True)
        slideshow_description.setAlignment(QtCore.Qt.AlignTop)
        kill_thread_boolean = False
        threadpool = QThreadPool()
        slideshow = Slideshow()
        threadpool.start(slideshow)

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()
        cursor.execute("SELECT * FROM Announcement")
        announcements = cursor.fetchall()

        self.scroll_area = QScrollArea(self.dashboard_tab)
        self.scroll_area.setGeometry(630, 10, 320, 540)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #F0F0F0; border-radius: 10px; }")

        self.side_announcements_widget = QWidget(self.scroll_area)
        self.side_announcements_layout = QVBoxLayout(self.side_announcements_widget)
        self.side_announcements_layout.setContentsMargins(0, 0, 0, 0)
        self.side_announcements_layout.setAlignment(Qt.AlignTop)
        index = 0

        def open_link(link):
            QDesktopServices.openUrl(QUrl(link))

        for announcement in announcements:
            side_announcement = QGroupBox()
            side_announcement.setFixedSize(300, 270)
            side_announcement.setStyleSheet("QGroupBox { border-radius: 10px; }")
            sa_layout = QVBoxLayout(side_announcement)
            sa_layout.setContentsMargins(10, 15, 10, 10)
            sa_picture = QLabel()
            sa_picture.setScaledContents(True)
            sa_picture.setPixmap(QPixmap(announcement[6]).scaledToHeight(240))
            sa_picture.setStyleSheet("QLabel { border-radius: 10px; }")
            sa_link = announcement[7]
            sa_title = QLabel()
            sa_title.setWordWrap(True)
            sa_title.setText(announcement[1] + announcement[2])
            sa_layout.addWidget(sa_picture)
            sa_layout.addWidget(sa_title)
            self.side_announcements_layout.addWidget(side_announcement)

            sa_picture.mousePressEvent = lambda event, link=sa_link: open_link(link)

        self.scroll_area.setWidget(self.side_announcements_widget)
        # Upcoming Events Tab
        self.upcoming_events_label = self.create_QLabel("upcoming_events_tab", "upcoming_events_label",
                                                        "Upcoming Events", 20, 20, 600, 50)
        self.upcoming_events_title_line = self.create_QFrame("upcoming_events_tab", "upcoming_events_title_line",
                                                             "HLine", 10, 65, 580, 6)

        self.student_calendar = QCalendarWidget(self.upcoming_events_tab)
        self.student_calendar.setGeometry(20, 80, 450, 450)

        self.student_calendar.setStyleSheet("QCalendarWidget { border-radius: 10px;}")

        self.student_calendar.selectionChanged.connect(self.student_upcoming_events_calendar)

        self.day_events_label = self.create_QLabel("upcoming_events_tab", "day_events_label", "Selected Event", 560,
                                                   80, 365, 30)
        self.day_events_label.setStyleSheet("QLabel { font-weight: bold; }")

        self.day_events = QTextEdit(self.upcoming_events_tab)
        self.day_events.setGeometry(560, 110, 365, 430)
        self.day_events.setStyleSheet("QTextEdit { border-radius: 15px; background-color: #FFFFFF; }")
        self.day_events.setAlignment(Qt.AlignTop)
        self.day_events.setReadOnly(True)
        self.day_events.setWordWrapMode(QTextOption.WordWrap)

        self.current_day = self.student_calendar.selectedDate().toString()
        self.day_events_label.setText("Events on: " + self.current_day[4:] + ":")
        self.day_events_label.setStyleSheet("QLabel { border-radius: 15px; }")

        # Maps Tab
        self.maps_label = self.create_QLabel("maps_tab", "maps_label", "Maps", 20, 20, 600, 50)
        self.maps_line = self.create_QFrame("maps_tab", "maps_line", "HLine", 10, 65, 600, 6)

        self.map_container = QGroupBox(self.maps_tab)
        self.map_container.setGeometry(20, 80, 550, 470)
        self.map_container.setStyleSheet("QGroupBox { border-radius: 20px }")

        self.maps_objects = self.create_QScrollArea("maps_tab", "maps_QScrollArea", "vertical_layout", 620, 80, 335, 480)
        self.maps = self.maps_objects[0]
        self.maps_layout = self.maps_objects[1]
        self.maps_scrollArea = self.maps_objects[2]
        self.maps_scrollArea.setStyleSheet(
            "QScrollArea { background-color: #f2f2f2; border-radius: 10px; border: 1px solid #d4d4d4; }"
            "QScrollBar:vertical { background-color: #d4d4d4; width: 10px; margin: 0px; }"
            "QScrollBar::handle:vertical { background-color: #888888; border-radius: 5px; }"
            "QScrollBar::handle:vertical:hover { background-color: #666666; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background-color: none; }"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background-color: none; }"
        )

        self.blue_label = self.create_QLabel("maps_tab", "blue_label", "", 655, 30, 20, 20)
        self.blue_label.setStyleSheet("background-color: #90caf9;")

        blue_text_label = self.create_QLabel("maps_tab", "blue_text_label", "Sports", 685, 28, 100, 30)

        self.green_label = self.create_QLabel("maps_tab", "blue_label", "", 740, 30, 20, 20)
        self.green_label.setStyleSheet("background-color: #81c784;")

        green_text_label = self.create_QLabel("maps_tab", "green_text_label", "Club", 770, 28, 100, 30)

        self.yellow_label = self.create_QLabel("maps_tab", "blue_label", "", 815, 30, 20, 20)
        self.yellow_label.setStyleSheet("background-color: #fff176;")

        yellow_text_label = self.create_QLabel("maps_tab", "yellow_text_label", "Entertainment", 845, 28, 100, 30)




        self.map_frame = QVBoxLayout(self.map_container)
        coordinate = (40.617847198627, -111.86923371648)
        map = folium.Map(zoom_start=12, location=coordinate, control_scale=True)
        folium.Marker(location=coordinate, icon=folium.Icon(color="darkgreen", icon='user')).add_to(map)
        self.show_event_locations("student")
        data = io.BytesIO()
        map.save(data, close_file=False)
        webView = QWebEngineView()
        webView.setHtml(data.getvalue().decode())

        self.map_frame.addWidget(webView)
        webView.setStyleSheet("QWebEngineView { border-radius: 10px; }")

        self.maps_scrollArea.setWidget(self.maps)
        self.maps_scrollArea.verticalScrollBar().setSliderPosition(0)

        # Points Tab
        self.points_label = self.create_QLabel("points_tab", "points_label", "Points", 20, 20, 600, 50)
        self.points_title_line = self.create_QFrame("points_tab", "points_title_line", "HLine", 10, 65, 580, 6)

        # combo boxes and stars

        self.event_combobox = QComboBox(self.points_tab)
        self.event_combobox.setGeometry(QtCore.QRect(30, 100, 170, 30))
        # Connect to the database
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        # Retrieve the events from the "events" table
        cursor.execute("SELECT ID, NAME FROM events")
        events = cursor.fetchall()

        # Clear the existing items in the combo box
        self.event_combobox.clear()

        # Add the events to the combo box
        self.event_combobox.addItem("Select Event")  # Add a default option
        for event in events:
            self.event_combobox.addItem(event[1])  # Assuming the event name is in the second column of the event data

        # Close the database connection
        cursor.close()
        sqliteConnection.close()

        # stars/ rating

        self.rating_combobox = QComboBox(self.points_tab)
        self.rating_combobox.setGeometry(QtCore.QRect(300, 100, 170, 30))
        self.rating_combobox.addItem("Rate Event")
        self.rating_combobox.addItem("⭐⭐⭐⭐⭐" + " --> Amazing")
        self.rating_combobox.addItem("⭐⭐⭐⭐" + " --> Good")
        self.rating_combobox.addItem("⭐⭐⭐" + " --> Average")
        self.rating_combobox.addItem("⭐⭐" + " -->Bad")
        self.rating_combobox.addItem("⭐" + " -->Horrible")

        # describe field
        self.info = QTextEdit(self.points_tab)
        self.info.setGeometry(30, 200, 460, 250)
        self.info.setAlignment(Qt.AlignTop)
        self.info.setWordWrapMode(True)

        # send button
        self.QPushButton = QtWidgets.QPushButton(self.points_tab)
        self.QPushButton.setText("Send For Approval")
        self.QPushButton.setAccessibleName("push_button")
        self.QPushButton.setIcon(QIcon(r"Application Pictures and Icons/send.svg"))
        self.QPushButton.clicked.connect(self.update_points)
        self.QPushButton.clicked.connect(self.send_approval)
        self.QPushButton.setGeometry(75, 470, 350, 50)
        self.QPushButton.setStyleSheet(PROFILE_BUTTON_STYLESHEET)

        self.points_leaderboard_objects = self.create_QScrollArea("points_tab", "points_leaderboard_QScrollArea",
                                                                  "vertical_layout", 600, 130, 350, 350)
        self.points_leaderboard = self.points_leaderboard_objects[0]
        self.points_leaderboard_layout = self.points_leaderboard_objects[1]
        self.points_leaderboard_scrollArea = self.points_leaderboard_objects[2]
        self.points_leaderboard_label = self.create_QLabel("points_tab", "points_leaderboard_label", "  Leaderboard: ",
                                                           600, 100, 350, 30)
        self.points_leaderboard_label = self.create_QLabel("points_tab", " ",
                                                           "Personal Points : " + str(self.user_points), 780, 100, 300,
                                                           30)

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute(
            "SELECT email_address, first_name, last_name, points, birthday, school, grade, RANK() OVER(ORDER BY points DESC) 'Rank' from students")
        students_leaderboard = cursor.fetchall()

        # Leaderboard
        for index, student in enumerate(students_leaderboard):
            self.event_object = QtWidgets.QGroupBox(self.points_leaderboard)
            self.event_object.setFixedSize(400, 50)
            self.event_object.setLayout(QtWidgets.QVBoxLayout())

            # Set QSS style based on the ranking position
            if index == 0:
                self.event_object.setStyleSheet("background-color: #d4af37;")  # gold
            elif index == 1:
                self.event_object.setStyleSheet("background-color: #C0C0C0;")  # silver
            elif index == 2:
                self.event_object.setStyleSheet("background-color: #CD7F32;")  # bronze

            self.label = self.create_QLabel("event", "test", "   " + str(student[1]) + ", " + str(student[2]) +
                                            " Points: " + str(student[3]), 0, 0, 400, 30)
            self.points_leaderboard_layout.addWidget(self.event_object)

        self.points_leaderboard_scrollArea.setWidget(self.points_leaderboard)
        self.points_leaderboard_scrollArea.verticalScrollBar().setSliderPosition(0)

        # Rewards Tab
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        self.picture_list = []
        self.name_list = []
        self.description_list = []
        self.points_list = []
        self.int_points_list = []
        index = 0

        cursor.execute("SELECT IMAGE_LINK_SRC FROM rewards")
        pictures = cursor.fetchall()
        cursor.execute("SELECT NAME FROM rewards")
        names = cursor.fetchall()
        cursor.execute("SELECT DESCRIPTION  FROM rewards")
        descriptions = cursor.fetchall()
        cursor.execute("SELECT POINTS  FROM rewards")
        points = cursor.fetchall()
        cursor.execute("SELECT EMAIL_ADDRESS, PASSWORD, POINTS FROM students")
        student_rows = cursor.fetchall()
        cursor.execute("SELECT intpoints  FROM rewards")
        intpoints = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM main.rewards")
        row_count = cursor.fetchone()[0]  # Fetch the result

        cursor.close()

        for picture in pictures:
            self.picture_list.append(picture)
        for name in names:
            self.name_list.append(name)
        for description in descriptions:
            self.description_list.append(description)
        for point in points:
            self.points_list.append(point)
        for points in intpoints:
            self.int_points_list.append(points)

        self.rewards_label = self.create_QLabel("rewards_tab", "rewards_label", "Rewards", 20, 20, 600, 50)
        self.rewards_title_line = self.create_QFrame("rewards_tab", "rewards_title_line", "HLine", 10, 65, 580, 6)
        self.rewards_my_points_label = self.create_QLabel("rewards_tab", "rewards_my_points_label",
                                                          "  Your Points: " + str(self.user_points), 680, 40, 300, 30)

        self.rewards_tab_objects = self.create_QScrollArea("rewards_tab", "rewards_QScrollArea", "grid_layout", 20, 120,
                                                           950, 425)
        self.rewards = self.rewards_tab_objects[0]
        self.rewards_layout = self.rewards_tab_objects[1]
        self.rewards_events_scrollArea = self.rewards_tab_objects[2]

        iterations = math.ceil(row_count / 3)
        reward_count = len(self.picture_list)
        index = 0

        for i in range(iterations):
            for j in range(3):
                if index < reward_count:
                    self.event_object = QtWidgets.QGroupBox(self.rewards)
                    self.event_object.setFixedSize(300, 300)
                    self.event_object.setLayout(QtWidgets.QGridLayout())
                    self.label = self.create_QLabel("event", "test", "  " + self.name_list[index][0], 10, 10, 100, 30)
                    self.cost_label = self.create_QLabel("event", "point_cost",
                                                         "Cost: " + self.points_list[index][0] + " points", 205, 10, 80,
                                                         30)
                    self.text = QTextEdit(self.event_object)
                    self.text.setReadOnly(True)
                    self.text.setGeometry(190, 40, 100, 200)
                    self.text.setText(self.description_list[index][0])
                    self.text.setAlignment(Qt.AlignTop)
                    self.text.setWordWrapMode(True)
                    self.picture = QLabel(self.event_object)
                    self.picture.setGeometry(10, 40, 170, 200)
                    self.picture.setPixmap(QPixmap(self.picture_list[index][0]))
                    self.button = QPushButton(self.event_object)
                    self.button.setText("   Redeem " + self.name_list[index][0])
                    #self.button.setStyleSheet()
                    size = QSize(25,25)
                    self.button.setIconSize(size)
                    self.button.setGeometry(10, 250, 280, 40)
                    self.button.clicked.connect(lambda index=index: self.deduct_points(index))
                    self.button.setIcon(QIcon(r"Application Pictures and Icons/baseline-redeem.svg"))
                    self.button.setStyleSheet(REDEEM_BUTTON_STYLESHEET)

                    self.rewards_layout.addWidget(self.event_object, i, j)
                    index += 1
                else:
                    break

        self.rewards_events_scrollArea.setWidget(self.rewards)
        self.rewards_events_scrollArea.verticalScrollBar().setSliderPosition(0)

        # Student Profile Tab
        self.student_profile_label = self.create_QLabel("student_profile_tab", "student_profile_label", "My Profile",
                                                        20, 20, 600, 50)
        self.student_profile_title_line = self.create_QFrame("student_profile_tab", "student_profile_title_line",
                                                             "HLine", 10, 65, 580, 6)
        self.student_profile_data = self.create_QTextEdit("student_profile_tab", "student_profile_data", True, 645, 80,
                                                          300, 250)
        self.student_profile_data_label = self.create_QLabel("student_profile_tab", "student_profile_data_label",
                                                             "  User Data", 645, 50, 300, 30)
        self.student_profile_data.setText(" Name: " + first_name + " " + last_name + '\n\n Grade: ' + str(
            self.grade) + '\n\n Gender: ' + self.user_gender + '\n\n Date of Birth: ' + self.date_of_birth + '\n\n Events Attended: ' + str(
            self.events_attended) + '\n\n Points: ' + str(self.user_points))

        self.student_report_button = QtWidgets.QPushButton(self.student_profile_tab)
        self.student_report_button.setText("    Generate Student Report")
        self.student_report_button.setGeometry(645, 350, 300, 50)
        self.student_report_button.setIcon(QIcon(r"Application Pictures and Icons/file-pdf.svg"))
        self.student_report_button.clicked.connect(self.generate_report)
        self.student_report_button.setStyleSheet(PROFILE_BUTTON_STYLESHEET)

        # User documentation
        self.pdf_button = QtWidgets.QPushButton(self.student_profile_tab)
        self.pdf_button.setText("    User Documentation")
        self.pdf_button.setGeometry(645, 420, 300, 50)
        self.pdf_button.setIcon(QIcon(r"Application Pictures and Icons/document-bold.svg"))
        self.pdf_button.clicked.connect(self.open_google_link)
        self.pdf_button.setStyleSheet(PROFILE_BUTTON_STYLESHEET)

        self.sources_button = QtWidgets.QPushButton(self.student_profile_tab)
        self.sources_button.setText("  Sources, Licenses, and References")
        self.sources_button.setGeometry(645, 490, 300, 50)
        self.sources_button.setIcon(QIcon(r"Application Pictures and Icons/book-reference.svg"))
        self.sources_button.clicked.connect(self.open_sources_link)
        self.sources_button.setStyleSheet(PROFILE_BUTTON_STYLESHEET)

        self.message_box = QTextBrowser(self.student_profile_tab)
        self.message_box.setGeometry(10, 100, 480, 400)
        self.input_box = QLineEdit(self.student_profile_tab)
        self.input_box.setGeometry(10, 510, 380, 30)
        self.send_button = QPushButton(" Send", self.student_profile_tab)
        self.send_button.setGeometry(400, 510, 80, 30)
        self.send_button.setIcon(QIcon(r"Application Pictures and Icons/send.svg"))
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet(SEND_BUTTON_STYLESHEET)

        # Load chat history
        self.load_chat_history()

        # FAQ Tab
        self.faq_label = QtWidgets.QLabel(self.faq_tab)
        self.faq_label.setGeometry(QtCore.QRect(20, 20, 560, 40))
        self.faq_label.setText("<h1>Frequently Asked Questions</h1>")
        self.faq_title_line = QtWidgets.QFrame(self.faq_tab)
        self.faq_title_line.setGeometry(QtCore.QRect(20, 60, 560, 6))
        self.faq_title_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.faq_title_line.setStyleSheet("background-color: black")

        self.faq_question1 = QtWidgets.QLabel(self.faq_tab)
        self.faq_question1.setGeometry(QtCore.QRect(20, 80, 560, 30))
        self.faq_question1.setText("<b>Q: How can I earn points? </b>")

        self.faq_answer1 = QtWidgets.QLabel(self.faq_tab)
        self.faq_answer1.setGeometry(QtCore.QRect(20, 120, 1000, 100))
        self.faq_answer1.setText("A: To earn points,  you can participate in spirit activities and visit the Points "
                                 "page.  On the Points page, choose the event you attended from the \n\n dropdown "
                                 "menu, rate it on a scale of 1 to 5 stars, provide a description of your "
                                 "experience in approximately 100 words, and submit the form.   After \n\n you "
                                 "submit, the administrator will review your submission and award you points.  These "
                                 "points can later be redeemed for exciting prizes at the prize shop.")

        self.faq_question2 = QtWidgets.QLabel(self.faq_tab)
        self.faq_question2.setGeometry(QtCore.QRect(20, 250, 560, 30))
        self.faq_question2.setText("<b>Q: How can I find the location of events?</b>")

        self.faq_answer2 = QtWidgets.QLabel(self.faq_tab)
        self.faq_answer2.setGeometry(QtCore.QRect(20, 290, 1000, 100))
        self.faq_answer2.setText("A: Finding the location of events is easy!  Our program offers a convenient "
                                 "calendar feature that showcases all the upcoming events and their\n\n specific "
                                 "locations.  Additionally, you can utilize the maps tab, where you'll find "
                                 "detailed information such as the event's date, time, and an interactive \n\n map "
                                 "displaying its location.  This way, you'll have all the necessary details to "
                                 "ensure you don't miss out on any of our exciting events!")

        self.faq_question3 = QtWidgets.QLabel(self.faq_tab)
        self.faq_question3.setGeometry(QtCore.QRect(20, 420, 560, 30))
        self.faq_question3.setText("<b>Q: How can I redeem my points?</b>")
        self.faq_answer3 = QtWidgets.QLabel(self.faq_tab)
        self.faq_answer3.setGeometry(QtCore.QRect(20, 460, 1000, 100))
        self.faq_answer3.setText("A: To redeem your points,  visit the Rewards page.  On the Rewards page,  "
                                 "you'll find a list of all the prizes you can potentially redeem.  Simply click \n\n on "
                                 "the prize you'd like to redeem.  After you click Redeem,  your points will be"
                                 "deducted and you'll be able to pick up your prize at the next event.")

        self.other_questions_button = QtWidgets.QPushButton(self.faq_tab)
        self.other_questions_button.setText("Other questions?")
        self.other_questions_button.setStyleSheet(SEND_BUTTON_STYLESHEET)
        self.other_questions_button.setGeometry(720, 20, 200, 30)
        self.other_questions_button.clicked.connect(self.show_question_popup)
        # end faq

        self.chatbot_label = QtWidgets.QLabel(self.chatbot_tab)
        self.chatbot_label.setGeometry(QtCore.QRect(20, 20, 560, 40))

        self.chatbot_layout = QtWidgets.QVBoxLayout()
        self.chatbot_widget = ChatGPTWindowWidget()

        h_spacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.chatbot_layout.addWidget(self.chatbot_widget)
        self.chatbot_layout.addItem(h_spacer)
        self.chatbot_tab.setLayout(self.chatbot_layout)

        self.tab_widget.show()

    def show_notifications(self):
        self.show_notifications_frame = QtWidgets.QFrame()
        self.show_notifications_frame.setWindowTitle("Notifications")
        self.show_notifications_frame.setFixedSize(300, 400)
        self.show_notifications_frame.move(700, 200)

        scroll_area = QtWidgets.QScrollArea(self.show_notifications_frame)
        scroll_area.setGeometry(0, 0, 300, 400)
        scroll_area.setWidgetResizable(True)

        # Create a widget to contain the items
        widget = QtWidgets.QWidget()
        scroll_area.setWidget(widget)

        # Set a layout for the widget
        layout = QtWidgets.QVBoxLayout(widget)

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute("SELECT * FROM NOTIFICATIONS")
        notifications = cursor.fetchall()

        for notification in notifications:
            id_, points, description, first_name, last_name, status = notification

            label = QtWidgets.QLabel(f"ID: {id_}\nPoints: {points}\nDescription: {description}\n"
                                     f"Name: {first_name} {last_name}\nStatus: {status}")
            layout.addWidget(label)

        self.show_notifications_frame.show()

    def load_chat_history(self):
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute("SELECT message, timestamp, user_id FROM chat")
        rows = cursor.fetchall()

        for row in rows:
            user_id, message, timestamp = row
            self.display_message(f" {timestamp}: {user_id} [{message}]\n")

    def send_message(self):
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        message = self.input_box.text()
        if message:
            # Insert the new message into the database
            cursor.execute("INSERT INTO chat (user_id, message) VALUES (?, ?)", (self.first_name, message))
            sqliteConnection.commit()

            # Display the message in the message box
            self.display_message(f"[{self.first_name}] {message}\n")

            # Clear the input box
            self.input_box.clear()

    def send_message_admin(self):
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        message = self.input_box.text()
        if message:
            # Insert the new message into the database
            cursor.execute("INSERT INTO chat (user_id, message) VALUES (?, ?)", ("Admin", message))
            sqliteConnection.commit()

            # Display the message in the message box
            self.display_message(f"[Admin] {message}\n")

            # Clear the input box
            self.input_box.clear()

    def display_message(self, message):
        self.message_box.append(message)
        self.message_box.verticalScrollBar().setValue(self.message_box.verticalScrollBar().maximum())

    def generate_report(self):
        self.report_frame = QtWidgets.QFrame()
        self.report_frame.setWindowTitle("Student Output Report")
        self.report_frame.setFixedSize(800, 500)

        self.student_report_label = self.create_QLabel("report_frame", "student_report_label", "Student Report", 20, 20,
                                                       600, 50)
        self.student_report_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.student_report_line = self.create_QFrame("report_frame", "student_report_line", "HLine", 10, 75, 600, 6)

        self.item_name_list = []
        self.item_points_list = []
        self.item_picture_list = []

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute("SELECT ITEM_NAME FROM purchased_items WHERE FIRST_NAME = ?", (self.first_name,))
        item_name = cursor.fetchall()

        cursor.execute("SELECT ITEM_POINTS FROM purchased_items WHERE FIRST_NAME = ?", (self.first_name,))
        item_points = cursor.fetchall()

        cursor.execute("SELECT IMAGE_LINK_SRC FROM purchased_items WHERE FIRST_NAME = ?", (self.first_name,))
        item_picture = cursor.fetchall()

        for item in item_name:
            self.item_name_list.append(item[0])
        for point in item_points:
            self.item_points_list.append(point[0])
        for picture in item_picture:
            self.item_picture_list.append(picture[0])

        self.report_frame_objects = self.create_QScrollArea("report_frame", "rewards_QScrollArea", "grid_layout", 20,
                                                            150, 450, 335)
        self.report = self.report_frame_objects[0]
        self.report_layout = self.report_frame_objects[1]
        self.report_scrollArea = self.report_frame_objects[2]

        self.past_purchases_label = self.create_QLabel("report_frame", "past_purchases_label", "Past Purchases", 20,
                                                       100, 300, 50)
        self.past_purchases_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        # Set vertical scroll policy to always on
        self.report_scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.report_scrollArea.setWidgetResizable(True)

        scroll_content = QtWidgets.QWidget()
        scroll_content_layout = QtWidgets.QGridLayout()
        scroll_content_layout.setSpacing(0)
        scroll_content.setLayout(scroll_content_layout)

        for index, item_name in enumerate(self.item_name_list):
            item_points = self.item_points_list[index]
            item_picture = self.item_picture_list[index]

            # Create a container widget for each item
            item_widget = QtWidgets.QWidget()
            item_layout = QtWidgets.QVBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_widget.setLayout(item_layout)

            item_name_label = self.create_QLabel("report_frame", f"item_name_label_{index}", item_name, 0, 0, 200, 50)
            item_name_label.setStyleSheet("font-size: 16px;")

            item_points_label = self.create_QLabel("report_frame", f"item_points_label_{index}",
                                                   f"Points: {item_points}", 0, 0, 200, 50)
            item_points_label.setStyleSheet("font-size: 16px;")

            item_picture_label = self.create_QLabel("report_frame", f"item_picture_label_{index}", "", 0, 0, 120, 120)
            item_picture_label.setPixmap(QtGui.QPixmap(item_picture).scaled(120, 120))

            # Add the item labels to the item layout
            item_layout.addWidget(item_name_label)
            item_layout.addWidget(item_points_label)
            item_layout.addWidget(item_picture_label)

            # Add the item widget to the report layout at the specified row and column positions
            scroll_content_layout.addWidget(item_widget, index // 3, index % 3)

        # Add the container widget to the scroll area
        self.report_scrollArea.setWidget(scroll_content)

        self.attended_events_label = self.create_QLabel("report_frame", "attended_events_label", "Attended Events", 510,
                                                        100, 300, 50)
        scroll_area = QScrollArea(self.report_frame)
        scroll_area.setGeometry(510, 150, 275, 335)

        labels_widget = QWidget()
        labels_layout = QVBoxLayout()
        labels_widget.setLayout(labels_layout)

        cursor.execute("SELECT FIRST_NAME, LAST_NAME, POINTS, EVENT, RATING FROM approval WHERE FIRST_NAME = ?",
                       (self.first_name,))
        data = cursor.fetchall()

        for row_data in data:
            for col_data in row_data:
                label = QLabel(str(col_data))
                labels_layout.addWidget(label)
            spacer = QLabel("<br>")  # Add a QLabel spacer with a line break
            labels_layout.addWidget(spacer)

        scroll_area.setWidget(labels_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        download_button = QtWidgets.QPushButton("Download Report", self.report_frame)
        download_button.setGeometry(615, 20, 150, 50)
        download_button.clicked.connect(self.download_report)

        self.report_frame.show()

    def download_report(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        printer.setOutputFileName("student-report.pdf")

        painter = QtGui.QPainter()
        painter.begin(printer)

        self.draw_report(painter)

        painter.end()

        file_path = os.path.abspath(
            "student-report.pdf")
        if os.path.exists(file_path):
            self.pdf_viewer = QtWidgets.QWidget()
            self.pdf_viewer.setWindowTitle("PDF Viewer")
            self.pdf_viewer.setGeometry(100, 100, 800, 600)

            layout = QtWidgets.QVBoxLayout(self.pdf_viewer)

            viewer = QtWebEngineWidgets.QWebEngineView()
            settings = viewer.settings()
            settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
            url = QtCore.QUrl.fromLocalFile(file_path)
            viewer.load(url)

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(self.pdf_viewer.close)

            layout.addWidget(viewer)
            layout.addWidget(close_button)

            self.pdf_viewer.show()
        else:
            print("PDF file not found.")

    def draw_report(self, painter):
        document = QtGui.QTextDocument()
        document.setDefaultFont(QtGui.QFont("Arial", 150))

        cursor = QtGui.QTextCursor(document)

        self.draw_report_title(cursor)

        self.draw_columns(cursor)

        cursor.movePosition(QtGui.QTextCursor.End)

        document.drawContents(painter)

    def draw_report_title(self, cursor):
        title_format = QtGui.QTextCharFormat()
        title_format.setFont(QtGui.QFont("Arial", 500, QtGui.QFont.Bold))

        cursor.insertText("Student Output Report\n", title_format)
        cursor.insertBlock()

    def draw_columns(self, cursor):
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        db_cursor = sqliteConnection.cursor()

        # Draw the column for past purchases
        db_cursor.execute("SELECT ITEM_NAME, ITEM_POINTS FROM purchased_items WHERE FIRST_NAME = ?", (self.first_name,))
        past_purchases = db_cursor.fetchall()

        item_format = QtGui.QTextCharFormat()
        item_format.setFont(QtGui.QFont("Arial", 250))

        cursor.insertText("Past Purchases:\n", item_format)
        cursor.insertBlock()

        for purchase in past_purchases:
            item_name = purchase[0]
            item_points = purchase[1]
            cursor.insertText(f"- {item_name} (Points: {item_points})\n", item_format)
            cursor.insertBlock()

        # Add a column break
        cursor.insertBlock()

        # Draw the column for attended events
        db_cursor.execute("SELECT EVENT, RATING FROM approval WHERE FIRST_NAME = ?", (self.first_name,))
        attended_events = db_cursor.fetchall()

        event_format = QtGui.QTextCharFormat()
        event_format.setFont(QtGui.QFont("Arial", 250))

        cursor.insertText("Attended Events:\n", event_format)
        cursor.insertBlock()

        for event in attended_events:
            event_name = event[0]
            event_rating = event[1]
            cursor.insertText(f"- {event_name} (Rating: {event_rating})\n", event_format)
            cursor.insertBlock()

    # admin output report
    def admin_output_reports(self):

        self.admin_output_report_frame = QtWidgets.QFrame()
        self.admin_output_report_frame.setWindowTitle("Administrator Output Report")
        self.admin_output_report_frame.setFixedSize(800, 500)

        self.admin_report_label = self.create_QLabel("admin_output_report_frame", "admin_report_label",
                                                     "Administrator Report", 20, 20,
                                                     600, 50)
        self.admin_report_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.admin_report_line = self.create_QFrame("admin_output_report_frame", "admin_report_line", "HLine", 10, 75,
                                                    600, 6)

        self.select_combobox_label = self.create_QLabel("admin_output_report_frame", "select_combobox_label",
                                                        "Choose Filter Option", 25, 120,
                                                        600, 50)

        self.filter_graph_combobox = QtWidgets.QComboBox(self.admin_output_report_frame)
        self.filter_graph_combobox.addItem("Choose Filter Option")
        self.filter_graph_combobox.addItem("Points by Grade")
        self.filter_graph_combobox.addItem("Events attended by Grade")
        self.filter_graph_combobox.addItem("Points by School")
        self.filter_graph_combobox.setGeometry(30, 170, 150, 40)

        self.graph_canvas = FigureCanvas(plt.figure())
        self.graph_canvas.setParent(self.admin_output_report_frame)
        self.graph_canvas.setGeometry(200, 90, 580, 400)

        self.filter_graph_combobox.currentIndexChanged.connect(self.generate_graph)

        self.download_button = QPushButton("Download Report", self.admin_output_report_frame)
        self.download_button.setGeometry(10, 350, 180, 50)
        self.download_button.clicked.connect(self.download_admin_report)

        self.download_leaderboard_button = QPushButton("Download Student Statistics", self.admin_output_report_frame)
        self.download_leaderboard_button.setGeometry(10, 420, 180, 50)
        self.download_leaderboard_button.clicked.connect(self.download_leaderboard_report)


        self.admin_output_report_frame.show()

    def generate_graph(self, index):
        selected_option = self.filter_graph_combobox.itemText(index)

        self.graph_canvas.figure.clear()
        ax = self.graph_canvas.figure.add_subplot(111)

        if selected_option == "Points by Grade":
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            cursor.execute("SELECT grade, SUM(points) FROM main.students GROUP BY grade;")
            result = cursor.fetchall()

            grades = [row[0] for row in result]
            points = [row[1] for row in result]

            plt.xlabel("Grade")
            plt.ylabel("Points")
            plt.title("Points by Grade")

            colors = plt.cm.get_cmap('tab10')
            color_values = colors(np.linspace(0, 1, len(grades)))
            ax.bar(grades, points, color=color_values)

        elif selected_option == "Events attended by Grade":
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            cursor.execute("SELECT grade, SUM(total_events_attended) FROM main.students GROUP BY grade;")
            result = cursor.fetchall()

            grades = [row[0] for row in result]
            events_attended = [row[1] for row in result]

            ax.bar(grades, events_attended)
            ax.set_xlabel("Grade")
            ax.set_ylabel("Events Attended")
            ax.set_title("Events Attended by Grade")

            colors = plt.cm.get_cmap('tab10')
            color_values = colors(np.linspace(0, 1, len(grades)))
            ax.bar(grades, events_attended, color=color_values)

        elif selected_option == "Points by School":
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            cursor.execute("SELECT SCHOOL, SUM(points) FROM main.students GROUP BY SCHOOL;")
            result = cursor.fetchall()

            schools = [row[0] for row in result]
            points = [row[1] for row in result]

            plt.xlabel("School")
            plt.ylabel("Points")
            plt.title("Points by School")

            colors = plt.cm.get_cmap('tab10')
            color_values = colors(np.linspace(0, 1, len(schools)))
            ax.bar(schools, points, color=color_values)
            # plt.xticks(rotation=45)  # Rotates x-axis labels for better readability
            plt.show()

        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

        self.graph_canvas.draw()

    def download_leaderboard_report(self):
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        # Retrieve the student data from the database, ordered by points in descending order
        cursor.execute("SELECT * FROM main.students ORDER BY POINTS DESC")
        students = cursor.fetchall()

        # Create a new PDF
        pdf = canvas.Canvas("leaderboard.pdf", pagesize=letter)

        # Set up the PDF layout
        pdf.setFont("Helvetica", 12)
        x_offset = 50
        y_offset = 700
        line_height = 20

        # Add the leaderboard header
        pdf.drawString(x_offset, y_offset, "Leaderboard")
        y_offset -= line_height

        # Add the column headers
        pdf.drawString(x_offset, y_offset, "Rank")
        pdf.drawString(x_offset + 50, y_offset, "First Name")
        pdf.drawString(x_offset + 150, y_offset, "Last Name")
        pdf.drawString(x_offset + 250, y_offset, "Points")
        y_offset -= line_height

        # Add the student data to the PDF
        rank = 1
        for student in students:
            first_name = student[1]
            last_name = student[2]
            points = student[11]

            pdf.drawString(x_offset, y_offset, str(rank))
            pdf.drawString(x_offset + 50, y_offset, first_name)
            pdf.drawString(x_offset + 150, y_offset, last_name)
            pdf.drawString(x_offset + 250, y_offset, str(points))

            y_offset -= line_height
            rank += 1

        # Save the PDF file
        pdf.save()

        file_path = os.path.abspath(
            "leaderboard.pdf")
        if os.path.exists(file_path):
            self.pdf_viewer = QtWidgets.QWidget()
            self.pdf_viewer.setWindowTitle("PDF Viewer")
            self.pdf_viewer.setGeometry(100, 100, 800, 600)

            layout = QtWidgets.QVBoxLayout(self.pdf_viewer)

            viewer = QtWebEngineWidgets.QWebEngineView()
            settings = viewer.settings()
            settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
            url = QtCore.QUrl.fromLocalFile(file_path)
            viewer.load(url)

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(self.pdf_viewer.close)

            layout.addWidget(viewer)
            layout.addWidget(close_button)

            self.pdf_viewer.show()
        else:
            print("PDF file not found.")


    def download_admin_report(self):

        pdf = pdf_backend.PdfPages("admin_report.pdf")

        options = ["Choose graph", "Points by Grade", "Events attended by Grade", "Gender Distribution",
                   "Points by Gender"]
        for index, option in enumerate(options[1:], start=1):
            self.generate_graph(index)
            pdf.savefig(self.graph_canvas.figure)

            self.graph_canvas.figure.clear()

        pdf.close()

        file_path = os.path.abspath(
            "admin_report.pdf")
        if os.path.exists(file_path):
            self.pdf_viewer = QtWidgets.QWidget()
            self.pdf_viewer.setWindowTitle("PDF Viewer")
            self.pdf_viewer.setGeometry(100, 100, 800, 600)

            layout = QtWidgets.QVBoxLayout(self.pdf_viewer)

            viewer = QtWebEngineWidgets.QWebEngineView()
            settings = viewer.settings()
            settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
            url = QtCore.QUrl.fromLocalFile(file_path)
            viewer.load(url)

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(self.pdf_viewer.close)

            layout.addWidget(viewer)
            layout.addWidget(close_button)

            self.pdf_viewer.show()
        else:
            print("PDF file not found.")

    #  User Documentation
    def open_google_link(self):
        file_path = os.path.abspath(
            "Application Data and Documentation Files/Spirit Quest User Documentation.pdf")
        if os.path.exists(file_path):
            self.pdf_viewer = QtWidgets.QWidget()
            self.pdf_viewer.setWindowTitle("PDF Viewer")
            self.pdf_viewer.setGeometry(100, 100, 800, 600)

            layout = QtWidgets.QVBoxLayout(self.pdf_viewer)

            viewer = QtWebEngineWidgets.QWebEngineView()
            settings = viewer.settings()
            settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
            url = QtCore.QUrl.fromLocalFile(file_path)
            viewer.load(url)

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(self.pdf_viewer.close)

            layout.addWidget(viewer)
            layout.addWidget(close_button)

            self.pdf_viewer.show()
        else:
            print("PDF file not found.")

    # admin user documentation
    def admin_user_documentation(self):
        file_path = os.path.abspath(
            "Application Data and Documentation Files/Spirit Quest Admin Documentation.pdf")
        if os.path.exists(file_path):
            self.pdf_viewer = QtWidgets.QWidget()
            self.pdf_viewer.setWindowTitle("PDF Viewer")
            self.pdf_viewer.setGeometry(100, 100, 800, 600)

            layout = QtWidgets.QVBoxLayout(self.pdf_viewer)

            viewer = QtWebEngineWidgets.QWebEngineView()
            settings = viewer.settings()
            settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
            url = QtCore.QUrl.fromLocalFile(file_path)
            viewer.load(url)

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(self.pdf_viewer.close)

            layout.addWidget(viewer)
            layout.addWidget(close_button)

            self.pdf_viewer.show()
        else:
            print("PDF file not found.")

    #  Sources Function
    def open_sources_link(self):
        file_path = os.path.abspath(
            "Application Data and Documentation Files/Sources, Licenses, and references .pdf")
        if os.path.exists(file_path):
            self.pdf_viewer = QtWidgets.QWidget()
            self.pdf_viewer.setWindowTitle("PDF Viewer")
            self.pdf_viewer.setGeometry(100, 100, 800, 600)

            layout = QtWidgets.QVBoxLayout(self.pdf_viewer)

            viewer = QtWebEngineWidgets.QWebEngineView()
            settings = viewer.settings()
            settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
            url = QtCore.QUrl.fromLocalFile(file_path)
            viewer.load(url)

            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(self.pdf_viewer.close)

            layout.addWidget(viewer)
            layout.addWidget(close_button)

            self.pdf_viewer.show()
        else:
            print("PDF file not found.")

    # 2 methods below are for the FAQ tab seperate questions
    def show_question_popup(self):
        dialog = QDialog(self.faq_tab)
        dialog.setWindowTitle("Ask a Question")
        dialog.setFixedSize(600, 500)

        layout = QGridLayout(dialog)

        name_label = QLabel("Name:", dialog)
        name_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(name_label, 0, 0)

        name_textbox = QLineEdit(dialog)
        layout.addWidget(name_textbox, 0, 1, 1, 2)

        grade_label = QLabel("Grade:", dialog)
        grade_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(grade_label, 1, 0)

        grade_textbox = QLineEdit(dialog)
        layout.addWidget(grade_textbox, 1, 1, 1, 2)

        email_label = QLabel("Email:", dialog)
        email_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(email_label, 2, 0)

        email_textbox = QLineEdit(dialog)
        layout.addWidget(email_textbox, 2, 1, 1, 2)

        title_label = QLabel("Title:", dialog)
        title_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(title_label, 3, 0)

        title_textbox = QLineEdit(dialog)
        layout.addWidget(title_textbox, 3, 1, 1, 2)

        message_label = QLabel("Message:", dialog)
        message_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(message_label, 4, 0)

        message_textbox = QTextEdit(dialog)
        layout.addWidget(message_textbox, 4, 1, 2, 2)
        message_textbox.setMinimumHeight(150)

        send_button = QPushButton("Send", dialog)
        layout.addWidget(send_button, 6, 1, 1, 2)
        send_button.clicked.connect(
            lambda: self.process_question(dialog, name_textbox.text(), grade_textbox.text(),
                                          email_textbox.text(), title_textbox.text(), message_textbox.toPlainText()))

        # Adjust widget positions and sizes
        name_label.setGeometry(20, 20, 100, 40)
        name_textbox.setGeometry(130, 20, 200, 30)
        grade_label.setGeometry(340, 20, 100, 30)
        grade_textbox.setGeometry(450, 20, 100, 30)
        email_label.setGeometry(20, 70, 100, 30)
        email_textbox.setGeometry(130, 70, 200, 30)
        title_label.setGeometry(340, 70, 100, 40)
        title_textbox.setGeometry(450, 70, 200, 30)
        message_label.setGeometry(20, 120, 100, 30)
        message_textbox.setGeometry(130, 120, 450, 150)
        send_button.setGeometry(240, 400, 120, 40)

        dialog.exec_()

    def process_question(self, dialog, name, grade, email, title, message):
        dialog.close()

        # Connect to the database
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        # Insert the question and message into the database
        insert_query = "INSERT INTO faq_questions (faq_name, faq_grade, faq_email, title, message) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (name, grade, email, title, message))
        sqliteConnection.commit()

        # Close the database connection
        cursor.close()
        sqliteConnection.close()

    def send_approval(self):
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        first_name = user[2]
        last_name = user[3]

        event_combobox_selection = self.event_combobox.currentText()
        rating_combobox_selection = self.rating_combobox.currentText()
        description_box = self.info.toPlainText()

        cursor.execute(
            "INSERT INTO approval (FIRST_NAME, LAST_NAME, POINTS, EVENT, RATING, DESCRIPTION) VALUES (?, ?, ?, ?, ?, ?)",
            (first_name, last_name, str(self.user_points), event_combobox_selection, rating_combobox_selection,
             description_box))
        sqliteConnection.commit()
        cursor.close()
        self.update_leaderboard()

        # Clear the text field
        self.info.clear()

        # Reset the event combo box to the default position
        self.event_combobox.setCurrentIndex(0)

        # Reset the rating combo box to the default position
        self.rating_combobox.setCurrentIndex(0)

    # updating the leadeboard
    def update_leaderboard(self):
        # Clear the existing leaderboard
        while self.points_leaderboard_layout.count():
            child = self.points_leaderboard_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Retrieve the updated leaderboard data from the database
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()
        cursor.execute(
            "SELECT email_address, first_name, last_name, points, birthday, school, grade, RANK() OVER(ORDER BY points DESC) 'Rank' FROM students")
        students_leaderboard = cursor.fetchall()
        cursor.close()
        sqliteConnection.close()

        # Repopulate the leaderboard
        for index, student in enumerate(students_leaderboard):
            self.event_object = QtWidgets.QGroupBox(self.points_leaderboard)
            self.event_object.setFixedSize(400, 50)
            self.event_object.setLayout(QtWidgets.QVBoxLayout())

            # Set QSS style based on the ranking position
            if index == 0:
                self.event_object.setStyleSheet("background-color: #d4af37;")  # gold
            elif index == 1:
                self.event_object.setStyleSheet("background-color: #C0C0C0;")  # silver
            elif index == 2:
                self.event_object.setStyleSheet("background-color: #CD7F32;")  # bronze

            self.label = self.create_QLabel("event", "test", "   " + str(student[1]) + ", " + str(student[2]) +
                                            " Points: " + str(student[3]), 0, 0, 400, 30)
            self.points_leaderboard_layout.addWidget(self.event_object)

        # Scroll to the top of the leaderboard
        self.points_leaderboard_scrollArea.verticalScrollBar().setValue(0)

    def approved_points(self):
        approved_message = QMessageBox()
        approved_message.setText("Approved hours")
        approved_message.setIcon(QMessageBox.Information)
        approved_message.exec_()

    def approved_hours(self):
        approved_message = QMessageBox()
        approved_message.setText("Sent Announcement")
        approved_message.setIcon(QMessageBox.Information)
        approved_message.exec_()

    def update_points(self):
        message = QMessageBox()
        message.setText("Sent to Administrator")
        message.setIcon(QMessageBox.Information)
        message.exec_()

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()
        # updated_user_points = self.logged_in_user_details[0][11] + 20
        updated_events_attended = self.logged_in_user_details[0][10] + 1
        # cursor.execute("UPDATE students SET POINTS = ?, TOTAL_EVENTS_ATTENDED = ? WHERE FIRST_NAME = ?",
        #                (updated_user_points, updated_events_attended, self.first_name))
        # sqliteConnection.commit()
        #
        # self.user_points = updated_user_points

        username = user[0]
        password = user[1]
        first_name = user[2]
        last_name = user[3]

        cursor.execute(
            "SELECT * FROM students WHERE EMAIL_ADDRESS = ? AND PASSWORD = ? AND FIRST_NAME = ? AND LAST_NAME = ?",
            (username, password, first_name, last_name))
        self.logged_in_user_details = cursor.fetchall()

        cursor.close()

        self.rewards_my_points_label.setText("  Your Points: " + str(self.user_points))
        self.points_leaderboard_label.setText("Personal Points : " + str(self.user_points))
        self.student_profile_data.setText("Name: " + first_name + " " + last_name + '\n\n Grade: ' + str(
            self.grade) + '\n\n Gender: ' + self.user_gender + '\n\n Date of Birth: ' + self.date_of_birth + '\n\n Events Attended: ' + str(
            self.events_attended) + '\n\n Points: ' + str(self.user_points))

        user_details.get_user_details.__init__(self)

    def setup_admin_page(self):
        self.intro_label = self.create_QLabel("central_widget", "intro_label", "Signed in as Vivaan Rajesh", 200,
                                              10, 600, 50)

        self.tab_widget = VerticalTabWidget(self.central_widget)
        self.tab_widget.setObjectName("tab_widget")
        self.tab_widget.resize(1405, 750)
        self.tab_widget.move(0, 55)

        # Administrator Login
        self.admin_dashboard_tab = QtWidgets.QWidget()
        self.admin_events_tab = QtWidgets.QWidget()
        self.admin_statistics_tab = QtWidgets.QWidget()
        self.admin_student_view_tab = QtWidgets.QWidget()
        self.admin_student_support_tab = QtWidgets.QWidget()

        self.tab_widget.addTab(self.admin_dashboard_tab, QIcon(r"Application Pictures and Icons/dashboard-solid-badged.svg"), "Dashboard           ")
        self.tab_widget.addTab(self.admin_events_tab, QIcon(r"Application Pictures and Icons/calendar-fill.svg"), "Events             ")
        self.tab_widget.addTab(self.admin_statistics_tab, QIcon(r"Application Pictures and Icons/statistics.svg"), "Statistics         ")
        self.tab_widget.addTab(self.admin_student_view_tab, QIcon(r"Application Pictures and Icons/profile-fill.svg"), "Student View       ")
        self.tab_widget.addTab(self.admin_student_support_tab, QIcon(r"Application Pictures and Icons/support.svg"), "Student Support    ")

        self.count = 0

        self.admin_dashboard_label = self.create_QLabel("admin_dashboard_tab", "admin_dashboard_label", "Dashboard", 20,
                                                        20, 600, 50)
        self.admin_dashboard_line = self.create_QFrame("admin_dashboard_tab", "admin_dashboard_line", "HLine", 10, 65,
                                                       600, 6)

        self.admin_events_label = self.create_QLabel("admin_events_tab", "admin_events_label", "Events", 20, 20, 600,
                                                     50)
        self.admin_events_line = self.create_QFrame("admin_events_tab", "admin_events_line", "HLine", 10, 65, 500, 6)
        self.admin_calendar = self.create_QCalendar("admin_events_tab", 20, 80, 450, 450)
        self.admin_calendar.selectionChanged.connect(self.admin_upcoming_events_calendar)

        # setting selected date
        # self.admin_events_title = self.create_QLabel("admin_events_tab", "admin_events_text", "Current Events", 680, 50,
        #                                              400, 30)
        # self.admin_events_title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.admin_current_events = self.create_QTextEdit("admin_events_tab", "admin_current_events", True, 560, 90,
                                                          365, 360)
        self.admin_day_events_label = self.create_QLabel("admin_events_tab", "admin_day_events_label", "  Selected Event", 560,
                                                   60, 365, 30)
        self.admin_current_day = self.admin_calendar.selectedDate().toString()
        self.admin_day_events_label.setText("Events on: " + self.admin_current_day[4:] + ":")
        self.admin_current_events.setAlignment(Qt.AlignTop)

        self.add_event_button = QtWidgets.QPushButton("    Add Event", self.admin_events_tab)
        self.add_event_button.setGeometry(QtCore.QRect(560, 460, 365, 40))
        self.add_event_button.setIcon(QIcon(r"Application Pictures and Icons/event-add.svg"))
        self.add_event_button.clicked.connect(self.add_event_button_clicked)
        self.add_event_button.setStyleSheet(SEND_BUTTON_STYLESHEET)

        self.add_rewards_button = QtWidgets.QPushButton("  Add Rewards", self.admin_events_tab)
        self.add_rewards_button.setGeometry(QtCore.QRect(560, 510, 365, 40))
        self.add_rewards_button.setIcon(QIcon(r"Application Pictures and Icons/reward-13-filled.svg"))
        self.add_rewards_button.clicked.connect(self.add_rewards_button_clicked)
        self.add_rewards_button.setStyleSheet(SEND_BUTTON_STYLESHEET)

        # ADMIN STATISTICS TAB
        self.admin_statistics_label = self.create_QLabel("admin_statistics_tab", "admin_statistics_label", "Statistics",
                                                         20, 20, 600, 50)
        self.admin_statistics_line = self.create_QFrame("admin_statistics_tab", "admin_statistics_line", "HLine", 10,
                                                        65, 600, 6)
        self.admin_leaderboard_title_label = self.create_QLabel("admin_statistics_tab", "leaderboard_admin",
                                                                "Student Leaderboard", 20, 5, 400, 200)
        self.admin_leaderboard_title_label.setFont(QFont('Arial', 20))
        self.admin_leaderboard_title_label.setAlignment(Qt.AlignCenter)
        self.admin_leaderboard_title_label.setStyleSheet("color: black")

        self.admin_leaderboard_objects = self.create_QScrollArea("admin_statistics_tab",
                                                                 "points_leaderboard_QScrollArea", "vertical_layout",
                                                                 20, 120, 450, 400)
        self.admin_leaderboard = self.admin_leaderboard_objects[0]
        self.admin_leaderboard_layout = self.admin_leaderboard_objects[1]
        self.admin_leaderboard_scrollArea = self.admin_leaderboard_objects[2]

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute(
            "SELECT email_address, first_name, last_name, points, birthday, school, grade, RANK() OVER(ORDER BY points DESC) 'Rank' from students")
        students_leaderboard = cursor.fetchall()

        self.rank = 1
        index = 0
        for student in students_leaderboard:
            self.event_object = QtWidgets.QGroupBox(self.admin_leaderboard)
            self.event_object.setFixedSize(400, 100)
            self.event_object.setLayout(QtWidgets.QVBoxLayout())
            self.label = self.create_QLabel("event", "test", "   " + "Name: " + str(student[1]) + " " + str(student[2]),
                                            0, 5, 400, 25)

            self.label2 = self.create_QLabel("event", "test", "   " + "Student Birthday: " + str(students[index][8]), 0,
                                             25,
                                             400, 30)

            self.label3 = self.create_QLabel("event", "test", "   " + "Attending School: " + str(students[index][9]), 0,

                                             45, 400, 30)
            self.label4 = self.create_QLabel("event", "test", "   " + "Grade: " + str(students[index][7]), 0, 65, 400,
                                             30)
            self.label5 = self.create_QLabel("event", "test", "   " + "Rank: " + str(self.rank), 300, 5, 400, 30)

            if index == 0:
                self.event_object.setStyleSheet("background-color: #d4af37;")  # gold
            elif index == 1:
                self.event_object.setStyleSheet("background-color: #C0C0C0;")  # silver
            elif index == 2:
                self.event_object.setStyleSheet("background-color: #CD7F32;")  # bronze
            self.rank += 1
            index += 1
            self.label6 = self.create_QLabel("event", "test", "   " + "Points: " + str(student[3]), 300, 25, 400, 30)
            self.admin_leaderboard_layout.addWidget(self.event_object)
        self.admin_leaderboard_scrollArea.setWidget(self.admin_leaderboard)
        self.admin_leaderboard_scrollArea.verticalScrollBar().setSliderPosition(0)

        self.choose_rand_winner = QtWidgets.QPushButton(self.admin_statistics_tab)
        self.choose_rand_winner.setText("  Select a Random Winner")
        self.choose_rand_winner.setGeometry(500, 100, 300, 30)
        self.choose_rand_winner.setIcon(QIcon(r"Application Pictures and Icons/trophy.svg"))
        self.choose_rand_winner.setStyleSheet(SEND_BUTTON_STYLESHEET)
        self.choose_rand_winner.clicked.connect(self.rand_win_nine)
        self.choose_rand_winner.clicked.connect(self.rand_win_ten)
        self.choose_rand_winner.clicked.connect(self.rand_win_eleven)
        self.choose_rand_winner.clicked.connect(self.rand_win_twelve)


        self.rand_win_gb = QtWidgets.QGroupBox(self.admin_statistics_tab)
        self.rand_win_gb.setFixedSize(400, 240)
        self.rand_win_gb.move(500, 140)
        self.rand_win_gb.setLayout(QtWidgets.QVBoxLayout())
        self.rand_label_nine = self.create_QLabel("rand", "test", "", 0, 5, 400, 30)
        self.rand_label4_nine = self.create_QLabel("rand", "test", "", 0, 25, 400, 30)
        self.rand_label6_nine = self.create_QLabel("rand", "test", "", 300, 5, 400, 30)

        self.rand_label_ten = self.create_QLabel("rand", "test", "", 0, 65, 400, 30)
        self.rand_label4_ten = self.create_QLabel("rand", "test", "", 0, 85, 400, 30)
        self.rand_label6_ten = self.create_QLabel("rand", "test", "", 300, 65, 400, 30)

        self.rand_label_eleven = self.create_QLabel("rand", "test", "", 0, 125, 400, 30)
        self.rand_label4_eleven = self.create_QLabel("rand", "test", "", 0, 145, 400, 30)
        self.rand_label6_eleven = self.create_QLabel("rand", "test", "", 300, 125, 400, 30)

        self.rand_label_twelve = self.create_QLabel("rand", "test", "", 0, 185, 400, 30)
        self.rand_label4_twelve = self.create_QLabel("rand", "test", "", 0, 205, 400, 30)
        self.rand_label6_twelve = self.create_QLabel("rand", "test", "", 300, 185, 400, 30)

        self.choose_top_winner = QtWidgets.QPushButton(self.admin_statistics_tab)
        self.choose_top_winner.setText("Select Winner with Most Points")
        self.choose_top_winner.setGeometry(500, 400, 300, 30)
        self.choose_top_winner.setIcon(QIcon(r"Application Pictures and Icons/trophy.svg"))
        self.choose_top_winner.setStyleSheet(SEND_BUTTON_STYLESHEET)
        self.choose_top_winner.clicked.connect(self.top_win)

        self.top_win_gb = QtWidgets.QGroupBox(self.admin_statistics_tab)
        self.top_win_gb.setFixedSize(400, 75)
        self.top_win_gb.move(500, 440)
        self.top_win_gb.setLayout(QtWidgets.QVBoxLayout())
        self.top_label = self.create_QLabel("top", "test", "", 0, 5, 400, 30)
        self.top_label4 = self.create_QLabel("top", "test", "", 0, 25, 400, 30)
        self.top_label6 = self.create_QLabel("top", "test", "", 300, 10, 400, 30)

        # ADMIN STUDENT VIEW
        self.admin_student_view_label = self.create_QLabel("admin_student_view_tab", "admin_student_view_label",
                                                           "Student View", 20, 20, 600, 50)
        self.admin_student_view_label.setStyleSheet("font-weight: bold; font-size: 30px;")
        self.admin_student_view_line = self.create_QFrame("admin_student_view_tab", "admin_student_view_line", "HLine",
                                                          10, 65, 600, 6)
        self.add_student_button = QPushButton(self.admin_student_view_tab)
        self.add_student_button.setGeometry(600, 20, 30, 30)
        add_icon = QIcon("Application Pictures and Icons/Add Button.png")
        self.add_student_button.setIcon(add_icon)
        self.add_student_button.clicked.connect(self.setup_student_account_creation)

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute("SELECT FIRST_NAME, LAST_NAME, GRADE, TOTAL_EVENTS_ATTENDED, POINTS, GENDER FROM main.students")
        rows = cursor.fetchall()

        scroll_area = QtWidgets.QScrollArea(self.admin_student_view_tab)
        scroll_area.setGeometry(20, 80, 660, 500)
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QGridLayout(scroll_content)

        admin_students = []
        for row in rows:
            first_name, last_name, grade, events_attended, points, gender = row
            student_info = f"<b>Name:</b> {first_name} {last_name}<br><br><b>Grade:</b> {grade}<br><br><b>Events Attended:</b> {events_attended}<br><br><b>Points:</b> {points}<br><br><b>Gender:</b> {gender}"
            admin_students.append(student_info)

        for i, student in enumerate(admin_students):
            text_edit = QtWidgets.QTextEdit(scroll_content)
            text_edit.setFixedSize(200, 200)
            text_edit.setReadOnly(True)
            text_edit.setHtml(student)
            scroll_layout.addWidget(text_edit, i // 3, i % 3)

        scroll_area.setWidget(scroll_content)

        # Admin information
        admin_info_label = QtWidgets.QLabel(self.admin_student_view_tab)
        admin_info_label.setGeometry(700, 20, 250, 30)
        admin_info_label.setStyleSheet("background-color: lightblue; font-weight: bold; font-size: 16px;")
        admin_info_label.setAlignment(QtCore.Qt.AlignCenter)
        admin_info_label.setText("Your Information")

        admin_info_text_edit = QtWidgets.QTextEdit(self.admin_student_view_tab)
        admin_info_text_edit.setGeometry(700, 50, 250, 250)
        admin_info_text_edit.setStyleSheet("font-size: 14px;")

        admin_name = "Vivaan Rajesh"
        admin_info = "Age: 34 \n\nDate of Birth: 11/5/1989\n\nGender: Male \n\nPosition: Primary Administrator \n\nEmail: vivaan.rajesh2006@gmail.com"

        # Set the admin's name with a larger font size
        admin_info_text_edit.append("<span style='font-size: 20px; font-weight: bold;'>{}</span>".format(admin_name))

        admin_info_text_edit.append("<br>")
        admin_info_text_edit.append(admin_info)
        admin_info_text_edit.setReadOnly(True)
        # Create buttons
        admin_report = QtWidgets.QPushButton("  Admin Output reports", self.admin_student_view_tab)
        admin_documentation = QtWidgets.QPushButton("  Admin User Documentation", self.admin_student_view_tab)
        admin_sources = QtWidgets.QPushButton("  Sources, Licenses and References", self.admin_student_view_tab)

        # Set button positions
        admin_report.setGeometry(700, 350, 250, 50)
        admin_documentation.setGeometry(700, 420, 250, 50)
        admin_sources.setGeometry(700, 490, 250, 50)

        # Connect buttons to functions
        admin_report.clicked.connect(self.admin_output_reports)
        admin_documentation.clicked.connect(self.admin_user_documentation)
        admin_sources.clicked.connect(self.open_sources_link)

        admin_report.setIcon(QIcon(r"Application Pictures and Icons/file-pdf.svg"))
        admin_documentation.setIcon(QIcon(r"Application Pictures and Icons/document-bold.svg"))
        admin_sources.setIcon(QIcon(r"Application Pictures and Icons/book-reference.svg"))

        admin_report.setStyleSheet(PROFILE_BUTTON_STYLESHEET)
        admin_documentation.setStyleSheet(PROFILE_BUTTON_STYLESHEET)
        admin_sources.setStyleSheet(PROFILE_BUTTON_STYLESHEET)

        # End of Admin Student View
        self.send_annoucements_label = self.create_QLabel("admin_dashboard_tab", "adminApprovalBlue",
                                                          " Send Announcements", 10, 65, 500, 55)
        self.send_annoucements_label.setFont(QFont('Open Sans', 19, QFont.Bold))

        self.name_of_annoucement_label = self.create_QLabel("admin_dashboard_tab", "adminApprovalBlue",
                                                            " Name of Announcement", 10, 110, 500, 55)
        self.name_of_annoucement_label.setFont(QFont('Calibri', 12))

        self.name_annoucement_text = QTextEdit(self.admin_dashboard_tab)
        self.name_annoucement_text.setGeometry(10, 150, 300, 30)
        self.name_annoucement_text.setAlignment(Qt.AlignTop)
        self.name_annoucement_text.setWordWrapMode(True)

        self.link_label = self.create_QLabel("admin_dashboard_tab", "adminApprovalBlue",
                                                            " Announcement Link", 10, 180, 500, 55)
        self.link_label.setFont(QFont('Calibri', 12))

        self.link_text = QTextEdit(self.admin_dashboard_tab)
        self.link_text.setGeometry(10, 225, 300, 30)
        self.link_text.setAlignment(Qt.AlignTop)
        self.link_text.setWordWrapMode(True)


        self.name_of_annoucement_label = self.create_QLabel("admin_dashboard_tab", "adminApprovalBlue",
                                                            " Announcement Details", 10, 250, 500, 55)
        self.name_of_annoucement_label.setFont(QFont('Calibri', 12))

        self.annoucement_detail = QTextEdit(self.admin_dashboard_tab)
        self.annoucement_detail.setGeometry(10, 300, 450, 170)
        self.annoucement_detail.setAlignment(Qt.AlignTop)
        self.annoucement_detail.setWordWrapMode(True)

        self.send_annnouncement_button = QtWidgets.QPushButton(self.admin_dashboard_tab)
        self.send_annnouncement_button.setText("  Send Announcement")
        self.send_annnouncement_button.setGeometry(10, 500, 450, 50)
        self.send_annnouncement_button.setIcon(QIcon(r"Application Pictures and Icons/announcement.svg"))
        self.send_annnouncement_button.clicked.connect(self.send_annoucement)
        self.send_annnouncement_button.setStyleSheet(PROFILE_BUTTON_STYLESHEET)

        # file upload
        self.upload_image_button = QtWidgets.QPushButton(self.admin_dashboard_tab)
        self.upload_image_button.setText("  Upload Image")
        self.upload_image_button.setGeometry(350, 150, 150, 30)
        self.upload_image_button.setIcon(QIcon(r"Application Pictures and Icons/upload.svg"))
        self.upload_image_button.clicked.connect(self.upload_image)
        self.upload_image_button.setStyleSheet(SEND_BUTTON_STYLESHEET)

        self.adminApprovalLine = self.create_QFrame("admin_dashboard_tab", "adminApprovalLine", "HLine", 10, 65, 600, 6)

        scroll_area = QtWidgets.QScrollArea(self.admin_dashboard_tab)
        scroll_area.setGeometry(570, 80, 390, 470)
        scroll_area.setWidgetResizable(True)

        scroll_content = QtWidgets.QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.adminApprovalBlue = self.create_QLabel("admin_dashboard_tab", "adminApprovalBlue",
                                                    " Requests Pending Approval", 650, 50, 300, 30)
        self.adminApprovalBlue.setStyleSheet("font-weight: bold; font-size: 20px;")

        self.tab_widget.show()

        layout = QVBoxLayout()  # create a vertical layout for the new widgets

        cursor.execute("SELECT FIRST_NAME, LAST_NAME, POINTS, EVENT, RATING, DESCRIPTION FROM approval")
        admin_approval_rows = cursor.fetchall()

        for approval in admin_approval_rows:
            widget = QWidget()  # create a new widget for each row
            hbox = QHBoxLayout(widget)  # Use widget as the parent layout for the label and button

            info_layout = QVBoxLayout()  # create a vertical layout for the information
            info_label = QLabel()  # create a label to display the information
            info_text = "Name: " + str(approval[0]) + " " + str(approval[1]) + "\nPoints: " + str(
                approval[2]) + "\nEvent: " + str(approval[3]) + "\nRating: " + str(approval[4])
            info_label.setText(info_text)
            info_layout.addWidget(info_label)  # add the info label to the info layout

            description_label = QLabel()  # create a label for the description
            description_label.setText("Description: " + str(approval[5]))
            description_label.setWordWrap(True)  # enable word wrapping for the description label

            button_layout = QVBoxLayout()  # create a vertical layout for the buttons
            approve_button = QPushButton("  Approve")  # create an "Approve" button for the row
            approve_button.setFixedSize(100, 30)  # set the size of the button
            approve_button.setIcon(QIcon(r"Application Pictures and Icons/thumb-up-green.svg"))
            approve_button.setProperty("row",
                                       approval)  # set the "row" property of the button to the current approval row
            approve_button.clicked.connect(lambda _, btn=approve_button: self.approved_points(btn))
            button_layout.addWidget(approve_button)  # add the approve button to the button layout

            deny_button = QPushButton("  Deny     ")  # create a "Deny" button for the row
            deny_button.setFixedSize(100, 30)  # set the size of the button
            deny_button.setIcon(QIcon(r"Application Pictures and Icons/thumb-up-red.svg"))
            deny_button.setProperty("row", approval)  # set the "row" property of the button to the current approval row
            deny_button.clicked.connect(lambda _, btn=deny_button: self.denied_points(btn))
            button_layout.addWidget(deny_button)  # add the deny button to the button layout

            hbox.addLayout(info_layout)  # add the info layout to the horizontal layout
            hbox.addWidget(description_label)  # add the description label to the horizontal layout
            hbox.addLayout(button_layout)  # add the button layout to the horizontal layout

            widget.setLayout(hbox)  # set the horizontal layout as the widget's layout
            layout.addWidget(widget)  # add the widget to the vertical layout

        scroll_layout.addLayout(layout)
        scroll_area.setWidget(scroll_content)

        # ADMIN STUDENT SUPPORT
        self.admin_student_support_label = self.create_QLabel("admin_student_support_tab",
                                                              "admin_student_support_label",
                                                              "Student Support", 20, 20, 600, 50)
        self.admin_student_support_label.setStyleSheet("font-weight: bold; font-size: 30px;")
        self.admin_student_support_line = self.create_QFrame("admin_student_support_tab", "admin_student_support_line",
                                                             "HLine", 10, 65, 600, 6)

        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute("SELECT faq_name, faq_grade, faq_email, title, message FROM faq_questions")
        faq_questions = cursor.fetchall()

        questions_label = QLabel("Student's Questions", self.admin_student_support_tab)
        questions_label.setStyleSheet("font-weight: bold; font-size: 20pt;")
        questions_label.setGeometry(680, 30, 280, 50)

        scroll_area = QScrollArea(self.admin_student_support_tab)
        scroll_area.setGeometry(680, 80, 260, 470)
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for question in faq_questions:
            faq_name = question[0]
            faq_grade = question[1]
            faq_email = question[2]
            title_text = question[3]
            message_text = question[4]

            text_edit = QTextEdit(scroll_content)
            text_edit.setFixedSize(220, 200)
            text_edit.setReadOnly(True)
            text_edit.setPlainText(
                f"Name: {faq_name}\n\nGrade: {faq_grade}\n\nEmail: {faq_email}\n\nTitle: {title_text}\n\nMessage: {message_text}")
            scroll_layout.addWidget(text_edit)

            resolved_button = QPushButton("  Resolved")
            resolved_button.setObjectName("resolved_button")
            resolved_button.setFixedWidth(text_edit.width())
            resolved_button.setFixedHeight(30)
            resolved_button.setIcon(QIcon(r"Application Pictures and Icons/check-fat-fill.svg"))
            resolved_button.setStyleSheet(RESOLVED_BUTTON_STYLESHEET)
            resolved_button.clicked.connect(lambda _, te=text_edit: self.resolve_question(te))
            scroll_layout.addWidget(resolved_button)

        scroll_area.setWidget(scroll_content)

        # Group Chat
        self.message_box = QTextBrowser(self.admin_student_support_tab)
        self.message_box.setGeometry(20, 90, 600, 400)

        self.input_box = QLineEdit(self.admin_student_support_tab)
        self.input_box.setGeometry(20, 500, 500, 30)

        send_button = QPushButton("Send", self.admin_student_support_tab)
        send_button.setGeometry(530, 500, 90, 30)
        send_button.setIcon(QIcon("Application Pictures and Icons/send.svg"))
        send_button.clicked.connect(self.send_message_admin)
        send_button.setStyleSheet(SEND_BUTTON_STYLESHEET)

        self.load_chat_history()

    def admin_upcoming_events_calendar(self):
        selected_date = self.admin_events_tab.sender().selectedDate().toString()
        new_date = selected_date.split()
        self.admin_check_events_on_day()

    def add_rewards_button_clicked(self):
        self.create_rewards_frame = QtWidgets.QFrame()
        self.create_rewards_frame.setWindowTitle("Create Rewards")
        self.create_rewards_frame.setFixedSize(800, 500)

        self.create_rewards_label = self.create_QLabel("create_rewards_frame", "create_rewards_label", "Create Rewards",
                                                       20, 20,
                                                       600, 50)
        self.create_rewards_label.setStyleSheet("font-size: 30px; font-weight: bold;")

        self.create_rewards_line = self.create_QFrame("create_rewards_frame", "create_rewards_line", "HLine", 10, 75,
                                                      600, 6)

        self.name_field_label = self.create_QLabel("create_rewards_frame", "name_field_label",
                                                   "Reward Name", 45, 120, 300, 30)

        self.name_field = QtWidgets.QLineEdit(self.create_rewards_frame)
        self.name_field.setGeometry(QtCore.QRect(200, 120, 200, 30))

        self.reward_description_label = self.create_QLabel("create_rewards_frame", "reward_description_label",
                                                           "Reward Description", 45, 170, 300, 30)
        self.reward_description = QPlainTextEdit(self.create_rewards_frame)
        self.reward_description.setGeometry(200, 170, 300, 150)

        self.upload_rewards_image_button = QtWidgets.QPushButton(self.create_rewards_frame)
        self.upload_rewards_image_button.setText("  Upload Image")
        self.upload_rewards_image_button.setGeometry(450, 120, 150, 30)
        self.upload_rewards_image_button.setIcon(QIcon(r"Application Pictures and Icons/image-add.svg"))
        self.upload_rewards_image_button.setStyleSheet(SEND_BUTTON_STYLESHEET)
        self.upload_rewards_image_button.clicked.connect(self.upload_rewards_photo)


        self.points_value_label = self.create_QLabel("create_rewards_frame", "points_value_label",
                                                     "Reward Points", 45, 340, 300, 30)
        self.points_value = QLineEdit(self.create_rewards_frame)
        self.points_value.setGeometry(200, 340, 200, 30)

        self.upload_rewards_button = QtWidgets.QPushButton(self.create_rewards_frame)
        self.upload_rewards_button.setText("  Upload Reward")
        self.upload_rewards_button.setGeometry(300, 410, 200, 50)
        self.upload_rewards_button.setIcon(QIcon(r"Application Pictures and Icons/reward-13-filled.svg"))
        self.upload_rewards_button.clicked.connect(self.upload_reward)
        self.upload_rewards_button.setStyleSheet(PROFILE_BUTTON_STYLESHEET)

        self.create_rewards_frame.show()

    def upload_rewards_photo(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self.create_rewards_frame, "Upload Image", "",
                                                    "Image Files (*.png *.jpg *.jpeg)")
        if image_path:
            destination_folder = "Rewards Pictures"
            current_directory = os.getcwd()
            destination_path = os.path.join(current_directory, destination_folder)
            destination_last_word = destination_path.split("\\")[-1]
            image_last_word = image_path.split("/")[-1]
            self.final_rewards_path = destination_last_word + "/" + image_last_word
            print(self.final_rewards_path)

            try:
                if os.path.isdir(destination_path):
                    shutil.copy(image_path, destination_path)
                    print("Image uploaded successfully!")
                else:
                    print("Destination directory not found.")
            except Exception as e:
                print("An error occurred:", str(e))

    def upload_reward(self):
        import sqlite3

        reward_name = self.name_field.text()
        reward_description = self.reward_description.toPlainText()
        reward_points = self.points_value.text()

        if self.final_rewards_path == "":
            print("Please upload an image")
        else:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            insert_query = "INSERT INTO rewards (NAME, DESCRIPTION, IMAGE_LINK_SRC, POINTS, intpoints) VALUES (?, ?, ?, ?, ?)"
            reward_data = (reward_name, reward_description, self.final_rewards_path, reward_points, reward_points)
            cursor.execute(insert_query, reward_data)
            sqliteConnection.commit()
            cursor.close()
            sqliteConnection.close()

            popup = QMessageBox()
            popup.setText("Uploaded Reward")
            popup.setIcon(QMessageBox.Information)
            popup.exec_()

    def add_reward_to_student_side(self, name, description, points, image_link):
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()
        cursor.execute("INSERT INTO rewards (NAME, DESCRIPTION, POINTS, IMG_LINK_SRC) VALUES (?, ?, ?, ?)",
                       (name, description, points, image_link))
        sqliteConnection.commit()

        cursor.execute("SELECT NAME, DESCRIPTION, POINTS, IMG_LINK_SRC FROM rewards WHERE NAME = ?", (name,))
        reward_info = cursor.fetchone()
        cursor.close()
        if reward_info:
            reward_name = reward_info[0]
            reward_description = reward_info[1]
            reward_points = reward_info[2]
            reward_image_link = reward_info[3]

            self.event_object = QtWidgets.QGroupBox(self.rewards)
            self.event_object.setFixedSize(300, 300)
            self.event_object.setLayout(QtWidgets.QGridLayout())
            self.label = self.create_QLabel("event", "test", "  " + reward_name, 10, 10, 100, 30)
            self.cost_label = self.create_QLabel("event", "point_cost", "Cost: " + str(reward_points) + " points",
                                                 205, 10, 80, 30)
            self.text = QTextEdit(self.event_object)
            self.text.setReadOnly(True)
            self.text.setGeometry(190, 40, 100, 200)
            self.text.setText(reward_description)
            self.text.setAlignment(Qt.AlignTop)
            self.text.setWordWrapMode(True)
            self.picture = QLabel(self.event_object)
            self.picture.setGeometry(10, 40, 170, 200)
            self.picture.setPixmap(QPixmap(reward_image_link))
            self.button = QPushButton(self.event_object)
            self.button.setText("Redeem " + reward_name)
            self.button.setGeometry(10, 250, 280, 40)
            self.button.clicked.connect(lambda: self.deduct_points(reward_name))
            self.rewards_layout.addWidget(self.event_object)

            self.rewards_events_scrollArea.verticalScrollBar().setSliderPosition(
                self.rewards_events_scrollArea.verticalScrollBar().maximum())

    def resolve_question(self, text_edit):
        popup = ResolvePopup()
        if popup.exec_() == QDialog.Accepted:
            resolution = popup.text_field.text()
            print("Resolution:", resolution)

    def add_event_button_clicked(self):
        popup = AddEventPopup()
        if popup.exec_() == QDialog.Accepted:
            print("Event added")

    def upload_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self.admin_dashboard_tab, "Upload Image", "",
                                                    "Image Files (*.png *.jpg *.jpeg)")
        if image_path:
            destination_folder = "Dashboard Sidebar Pictures"
            current_directory = os.getcwd()
            destination_path = os.path.join(current_directory, destination_folder)
            destination_last_word = destination_path.split("\\")[-1]
            image_last_word = image_path.split("/")[-1]
            self.final_path_announcement = destination_last_word + "/" + image_last_word
            print(self.final_path_announcement)

            try:
                if os.path.isdir(destination_path):
                    shutil.copy(image_path, destination_path)
                    print("Image uploaded successfully!")
                else:
                    print("Destination directory not found.")
            except Exception as e:
                print("An error occurred:", str(e))

    def denied_points(self, button):
        parent_widget = button.parentWidget()
        label = parent_widget.findChild(QLabel, "")
        if label is not None:
            item_text = label.text()
            lines = item_text.split('\n')
            if len(lines) >= 2:
                second_line = lines[1]
                prefix = "Points: "
                if second_line.startswith(prefix):
                    number = second_line[len(prefix):]

            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            status = "Denied"

            insert_query = "INSERT INTO main.notifications (points, description, first_name, last_name, status) " \
                           "SELECT points, description, first_name, last_name, ? " \
                           "FROM main.approval " \
                           f"WHERE POINTS = '{number}'"
            cursor.execute(insert_query, (status,))

            delete_query = f"DELETE FROM main.approval WHERE POINTS = '{number}'"
            cursor.execute(delete_query)

            sqliteConnection.commit()

            popup = QMessageBox()
            popup.setText("Denied request")
            popup.setIcon(QMessageBox.Information)
            popup.exec_()

            layout = parent_widget.layout()
            layout.removeWidget(label)
            layout.removeWidget(button)
            label.deleteLater()
            button.deleteLater()
            parent_widget.deleteLater()

    def approved_points(self, button):
        updated_user_points = self.logged_in_user_details[0][11] + 20
        print(updated_user_points)

        parent_widget = button.parentWidget()
        label = parent_widget.findChild(QLabel, "")
        if label is not None:

            item_text = label.text()
            lines = item_text.split('\n')
            if len(lines) >= 2:
                second_line = lines[1]
                prefix = "Points: "
                if second_line.startswith(prefix):
                    number = second_line[len(prefix):]

            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            status = "Approved"

            insert_query = "INSERT INTO main.notifications (points, description, first_name, last_name, status) " \
                           "SELECT points, description, first_name, last_name, ? " \
                           "FROM main.approval " \
                           f"WHERE POINTS = '{number}'"
            cursor.execute(insert_query, (status,))

            delete_query = f"DELETE FROM main.approval WHERE POINTS = '{number}'"
            cursor.execute(delete_query)

            query = "UPDATE students SET POINTS = ? WHERE FIRST_NAME = ?"
            cursor.execute(query, (updated_user_points, self.first_name))

            sqliteConnection.commit()

            popup = QMessageBox()
            popup.setText("Approved request")
            popup.setIcon(QMessageBox.Information)
            popup.exec_()

            layout = parent_widget.layout()
            layout.removeWidget(label)
            layout.removeWidget(button)
            label.deleteLater()
            button.deleteLater()
            parent_widget.deleteLater()

    def rand_win_nine(self):
        import random

        try:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()
            cursor.execute(
                "SELECT email_address, first_name, last_name, points, birthday, school, grade FROM main.students WHERE grade = 9")
            grade_9_students = cursor.fetchall()
        except Exception as e:
            print("An error occurred:", str(e))

        if grade_9_students:
            random_winner = random.choice(grade_9_students)
            self.rand_label_nine.setText("   " + "Name: " + str(random_winner[1]) + " " + str(random_winner[2]))
            self.rand_label4_nine.setText("   " + "Grade: " + str(random_winner[6]))
            self.rand_label6_nine.setText("   " + "Points: " + str(random_winner[3]))
        else:
            # Handle the case when there are no students in grade 9
            self.rand_label_nine.setText("No students in grade 9")
            self.rand_label4_nine.setText("")
            self.rand_label6_nine.setText("")

    def rand_win_ten(self):
        import random

        try:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()
            cursor.execute(
                "SELECT email_address, first_name, last_name, points, birthday, school, grade FROM main.students WHERE grade = 10")
            grade_10_students = cursor.fetchall()
        except Exception as e:
            print("An error occurred:", str(e))

        if grade_10_students:
            random_winner = random.choice(grade_10_students)
            self.rand_label_ten.setText("   " + "Name: " + str(random_winner[1]) + " " + str(random_winner[2]))
            self.rand_label4_ten.setText("   " + "Grade: " + str(random_winner[6]))
            self.rand_label6_ten.setText("   " + "Points: " + str(random_winner[3]))
        else:
            # Handle the case when there are no students in grade 10
            self.rand_label_ten.setText("No students in grade 10")
            self.rand_label4_ten.setText("")
            self.rand_label6_ten.setText("")

    def rand_win_eleven(self):
        import random

        try:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()
            cursor.execute(
                "SELECT email_address, first_name, last_name, points, birthday, school, grade FROM main.students WHERE grade = 11")
            grade_11_students = cursor.fetchall()
        except Exception as e:
            print("An error occurred:", str(e))

        if grade_11_students:
            random_winner = random.choice(grade_11_students)
            self.rand_label_eleven.setText("   " + "Name: " + str(random_winner[1]) + " " + str(random_winner[2]))
            self.rand_label4_eleven.setText("   " + "Grade: " + str(random_winner[6]))
            self.rand_label6_eleven.setText("   " + "Points: " + str(random_winner[3]))
        else:
            # Handle the case when there are no students in grade 11
            self.rand_label_eleven.setText("No students in grade 11")
            self.rand_label4_eleven.setText("")
            self.rand_label6_eleven.setText("")

    def rand_win_twelve(self):
        import random

        try:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()
            cursor.execute(
                "SELECT email_address, first_name, last_name, points, birthday, school, grade FROM main.students WHERE grade = 12")
            grade_12_students = cursor.fetchall()
        except Exception as e:
            print("An error occurred:", str(e))

        if grade_12_students:
            random_winner = random.choice(grade_12_students)
            self.rand_label_twelve.setText("   " + "Name: " + str(random_winner[1]) + " " + str(random_winner[2]))
            self.rand_label4_twelve.setText("   " + "Grade: " + str(random_winner[6]))
            self.rand_label6_twelve.setText("   " + "Points: " + str(random_winner[3]))
        else:
            # Handle the case when there are no students in grade 12
            self.rand_label_twelve.setText("No students in grade 12")
            self.rand_label4_twelve.setText("")
            self.rand_label6_twelve.setText("")

    def top_win(self):
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        cursor.execute(
            "SELECT email_address, first_name, last_name, points, birthday, school, grade, RANK() OVER(ORDER BY points DESC) 'Rank' from students")
        students_leaderboard = cursor.fetchall()

        if students_leaderboard:
            sorted_students = sorted(students_leaderboard, key=lambda x: x[3], reverse=True)
            top_winner = sorted_students[0]
            self.top_label.setText("   " + "Name: " + str(top_winner[1]) + " " + str(top_winner[2]))
            self.top_label4.setText("   " + "Grade: " + str(top_winner[6]))
            self.top_label6.setText("   " + "Points: " + str(top_winner[3]))
        else:
            # Handle the case when there are no students in the leaderboard
            self.top_label.setText("No students in the leaderboard")
            self.top_label4.setText("")
            self.top_label6.setText("")

    def send_annoucement(self):
        try:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()

            name_annoucement_text_stuff = self.name_annoucement_text.toPlainText()
            details_annoucement_text_stuff = self.annoucement_detail.toPlainText()
            link_text_stuff = self.link_text.toPlainText()

            query = "INSERT INTO ANNOUNCEMENT (NAME, DETAILS, IMAGE_LINK_SOURCE, LINK) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (name_annoucement_text_stuff, details_annoucement_text_stuff, self.final_path_announcement, link_text_stuff))
            sqliteConnection.commit()
            cursor.close()

            popup = QMessageBox()
            popup.setText("Sent Announcement")
            popup.setIcon(QMessageBox.Information)
            popup.exec_()

            self.name_annoucement_text.clear()
            self.annoucement_detail.clear()
            self.link_text.clear()

        except Exception as e:
            print(e)

    def create_QTextEdit2(self, container, object_name, read_only, x_coordinate, y_coordinate, width, length):
        widget = QTextEdit(container)
        widget.setObjectName(object_name)
        widget.setReadOnly(read_only)
        widget.setGeometry(x_coordinate, y_coordinate, width, length)
        return widget

    def student_upcoming_events_calendar(self):
        selected_date = self.upcoming_events_tab.sender().selectedDate().toString()
        new_date = selected_date.split()
        self.check_events_on_day()

    def admin_events_calendar(self):
        selected_date = self.admin_events_tab.sender().selectedDate().toString()
        new_date = selected_date.split()
        self.admin_current_events.setText("Events on " + selected_date[4:] + ":")
        self.admin_current_events.setAlignment(Qt.AlignTop)
        event_year = new_date[3]
        event_month = new_date[1]
        event_day = new_date[2]
        new_month = 1
        month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9,
                      "Oct": 10, "Nov": 11, "Dec": 12}
        new_month = month_dict[event_month]
        for event in events:
            events_day = event[8]
            events_month = event[7]
            events_year = event[6]
            if str(event_year) == str(events_year):
                if str(new_month) == str(events_month):
                    if str(event_day) == str(events_day):
                        self.admin_current_events.setText("Events on " + selected_date[4:] + ": " + event[2])

    # Deduct points from the user that purchases the merchandise
    def deduct_points(self, index):
        global username
        global password
        global user
        point_cost = int(self.rewards_tab.sender().parent().findChild(QtWidgets.QLabel, "point_cost").text()[6:9])

        # Validates that the user has enough points to purchase the item
        if self.user_points >= point_cost:
            sqliteConnection = sqlite3.connect('identifier.sqlite')
            cursor = sqliteConnection.cursor()
            new_user_points = self.logged_in_user_details[0][11] - point_cost
            cursor.execute("UPDATE students SET POINTS = ? WHERE FIRST_NAME = ?", (new_user_points, self.first_name))

            cursor.execute("SELECT NAME, DESCRIPTION, IMAGE_LINK_SRC FROM rewards WHERE POINTS = ?", (point_cost,))
            result = cursor.fetchone()

            if result:
                item_name = result[0]
                item_description = result[1]
                item_image = result[2]

                popup = QMessageBox()
                popup.setText("Purchased: " + item_name)
                popup.setIcon(QMessageBox.Information)
                popup.exec_()

                cursor.execute(
                    "INSERT INTO purchased_items (FIRST_NAME, LAST_NAME, ITEM_NAME, ITEM_DESCRIPTION, ITEM_POINTS, IMAGE_LINK_SRC) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (self.first_name, self.last_name, item_name, item_description,
                     point_cost,
                     item_image)
                )

            sqliteConnection.commit()

            self.user_points = new_user_points
            username = user[0]
            password = user[1]
            cursor.execute("SELECT * FROM students WHERE EMAIL_ADDRESS = ? AND PASSWORD = ?", (username, password))

            self.logged_in_user_details = cursor.fetchall()
            cursor.close()
            self.rewards_my_points_label.setText("  Your Points: " + str(self.user_points))

            user_details.get_user_details.__init__(self)

    def return_to_login_screen(self):
        global kill_thread_boolean
        kill_thread_boolean = True
        self.central_widget.deleteLater()
        main_window.setFixedSize(800, 500)
        self.setup_login_screen(main_window)
        main_window.setCentralWidget(self.login_central_widget)

    def show_event_locations(self, user):
        if user == "student":

            for i, event in enumerate(events):
                event_coordinate = (event[9], event[10])
                marker_cluster = MarkerCluster().add_to(map)
                folium.Marker(
                    location=event_coordinate,
                    icon=folium.Icon(color="red", icon='circle', prefix='fa'),
                    popup=(folium.Popup(f'<h6><b>{event[1]}</b></h6>' + "\n" + f'<h6><b>{event[2]}</b></h6>', show=True,
                                        min_width=20))
                ).add_to(marker_cluster)

                self.event_object = QtWidgets.QGroupBox(self.maps)
                self.event_object.setFixedSize(325, 100)
                self.event_object.setLayout(QtWidgets.QVBoxLayout())

                # Color-coding based on event type
                event_type = event[4]
                if event_type == "Sports":
                    color = "#90caf9"
                elif event_type == "Club":
                    color = "#81c784"
                elif event_type == "Entertainment":
                    color = "#fff176"
                else:
                    color = "gray"

                self.event_object.setStyleSheet(
                    f"background-color: {color}; border-radius: 10px;")  # Set box background color and border radius
                # Set box background color

                self.title = self.create_QLabel("event", "title", (event[1] + "\n" + event[2]), 10, 10, 305, 60)
                self.title.setWordWrap(True)

                self.date = self.create_QLabel("event", "date",
                                               (str(event[7]) + "/" + str(event[8]) + "/" + str(event[6])), 240, 0, 80,
                                               60)
                self.description = self.create_QLabel("event", "description", (event[3]), 10, 60, 305, 40)
                self.description.setWordWrap(True)

                self.maps_layout.addWidget(self.event_object)

    def check_events_on_day(self):
        selected_date = self.upcoming_events_tab.sender().selectedDate().toString()
        numerical_data_list = selected_date.split()
        numerical_data_list[2] = int(numerical_data_list[2])
        numerical_data_list[3] = int(numerical_data_list[3])

        month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9,
                      "Oct": 10, "Nov": 11, "Dec": 12}
        numerical_data_list[1] = month_dict[numerical_data_list[1]]
        self.day_events.clear()
        current_text = '<html><body style="font-size: 10pt;">'  # Opening HTML tags and setting font size (reduced to 10pt)
        for event in events:
            if ((event[7] == numerical_data_list[1]) and (event[8] == numerical_data_list[2]) and (
                    event[6] == numerical_data_list[3])):
                # Insert the image into the QTextEdit widget using HTML and CSS
                picture = event[11]
                if picture:
                    current_text += '<div style="display: flex; align-items: center; flex-direction: column;">' \
                                    + '<img src="{}" style="width: 100px; height: auto; margin-bottom: 10px;">'.format(
                        picture) \
                                    + '<p><strong>Event:</strong> ' + event[2] + '</p>' \
                                    + '<p><strong>Address:</strong> ' + event[3] + '</p>' \
                                    + '<p><strong>Type:</strong> ' + event[4] + '</p>' \
                                    + '<p><strong>Points:</strong> ' + str(event[5]) + '</p>' \
                                    + '<p><strong>Coordinates:</strong> ' + str(event[9]) + ', ' + str(
                        event[10]) + '</p>' \
                                    + '</div>' \
                                    + '<br>'  # Add a line space between events

        current_text += '</body></html>'  # Closing HTML tags

        # Set the HTML content as the text of the QTextEdit widget
        self.day_events.setHtml(current_text)

        self.day_events_label.setText(
            "Events on: " + self.upcoming_events_tab.sender().selectedDate().toString("MMMM d, yyyy") + ":")

    def admin_check_events_on_day(self):
        selected_date = self.admin_events_tab.sender().selectedDate().toString()
        numerical_data_list = selected_date.split()
        numerical_data_list[2] = int(numerical_data_list[2])
        numerical_data_list[3] = int(numerical_data_list[3])

        month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9,
                      "Oct": 10, "Nov": 11, "Dec": 12}
        numerical_data_list[1] = month_dict[numerical_data_list[1]]
        self.admin_current_events.clear()
        current_text = '<html><body style="font-size: 10pt;">'  # Opening HTML tags and setting font size (reduced to 10pt)
        for event in events:
            if ((event[7] == numerical_data_list[1]) and (event[8] == numerical_data_list[2]) and (
                    event[6] == numerical_data_list[3])):
                # Insert the image into the QTextEdit widget using HTML and CSS
                picture = event[11]
                if picture:
                    current_text += '<div style="display: flex; align-items: center; flex-direction: column;">' \
                                    + '<img src="{}" style="width: 100px; height: auto; margin-bottom: 10px;">'.format(
                        picture) \
                                    + '<p><strong>Event:</strong> ' + event[2] + '</p>' \
                                    + '<p><strong>Address:</strong> ' + event[3] + '</p>' \
                                    + '<p><strong>Type:</strong> ' + event[4] + '</p>' \
                                    + '<p><strong>Points:</strong> ' + str(event[5]) + '</p>' \
                                    + '<p><strong>Coordinates:</strong> ' + str(event[9]) + ', ' + str(
                        event[10]) + '</p>' \
                                    + '</div>' \
                                    + '<br>'  # Add a line space between events

        current_text += '</body></html>'  # Closing HTML tags

        # Set the HTML content as the text of the QTextEdit widget
        self.admin_current_events.setHtml(current_text)

        self.admin_day_events_label.setText(
            "Events on: " + self.admin_events_tab.sender().selectedDate().toString("MMMM d, yyyy") + ":")
    # Widget Creation Functions
    def create_QCheckBox(self, container, x_coordinate, y_coordinate, width, length):
        return create_widget_functions.create_QCheckBox.__init__(self, container, x_coordinate, y_coordinate, width,
                                                                 length)

    def create_QCalendar(self, container, x_coordinate, y_coordinate, width, length):
        return create_widget_functions.create_QCalendar.__init__(self, container, x_coordinate, y_coordinate, width,
                                                                 length)

    def create_QLabel(self, container, object_name, text, x_coordinate, y_coordinate, width, length):
        return create_widget_functions.create_QLabel.__init__(self, container, object_name, text, x_coordinate,
                                                              y_coordinate, width, length)

    def create_QLineEdit(self, container, object_name, read_only, x_coordinate, y_coordinate, width, length):
        return create_widget_functions.create_QLineEdit.__init__(self, container, object_name, read_only, x_coordinate,
                                                                 y_coordinate, width, length)

    def create_QTextEdit(self, container, object_name, read_only, x_coordinate, y_coordinate, width, height):
        text_edit = create_widget_functions.create_QTextEdit.__init__(self, container, object_name, read_only,
                                                                      x_coordinate, y_coordinate, width, height)
        text_edit.setFixedWidth(width)
        text_edit.setFixedHeight(height)
        return text_edit

    def create_QTextEdit2(self, container, object_name, read_only, x_coordinate, y_coordinate, width, length):
        text_edit = QTextEdit(container)
        text_edit.setObjectName(object_name)
        text_edit.setReadOnly(read_only)
        text_edit.setGeometry(x_coordinate, y_coordinate, width, length)
        return text_edit

    def create_QScrollArea(self, container, object_name, layout, x_coordinate, y_coordinate, fixed_width, min_length):
        return create_widget_functions.create_QScrollArea.__init__(self, container, object_name, layout, x_coordinate,
                                                                   y_coordinate, fixed_width, min_length)

    def create_QFrame(self, container, object_name, orientation, x_coordinate, y_coordinate, width, length):
        return create_widget_functions.create_QFrame.__init__(self, container, object_name, orientation, x_coordinate,
                                                              y_coordinate, width, length)

    def create_QPushButton(self, container, object_name, text, icon, x_coordinate, y_coordinate, width, length):
        if container == "main_window":
            self.QPushButton = QtWidgets.QPushButton(main_window)
            if text != "None":
                self.QPushButton.setText(text)
            if icon != "None":
                self.QPushButton.setIcon(QIcon(icon))
            self.QPushButton.setFixedSize(width, length)
            self.QPushButton.move(x_coordinate, y_coordinate)

            return self.QPushButton
        else:
            return create_widget_functions.create_QPushButton.__init__(self, container, object_name, text, icon,
                                                                       x_coordinate, y_coordinate, width, length)

    def create_horizontal_QSlider(self, container, x_coordinate, y_coordinate, width, length):
        return create_widget_functions.create_horizontal_QSlider.__init__(self, container, x_coordinate, y_coordinate,
                                                                          width, length)


# A custom-built widget that creates a slideshow
import glob


class Slideshow(QRunnable):
    @pyqtSlot()
    def run(self) -> None:
        sqliteConnection = sqlite3.connect('identifier.sqlite')
        cursor = sqliteConnection.cursor()

        dir_path = r'Announcement Pictures'
        picture_list = glob.glob(os.path.join(dir_path, '*.jpeg')) + glob.glob(
            os.path.join(dir_path, '*.jpg')) + glob.glob(os.path.join(dir_path, '*.png'))

        title_list = [
            "Hillcrest High School was voted the school that had the best theatre program in the nation!\n\n",

            "Hillcrest High School has the highest graduation rate and most challenging curriculum!\n",

            "Canyons school district has an IB school in it's district, meaning better education\n",

            "Canyons School District filmed on the world's largest commercial news channel!\n",

            "Hillcrest High Library reintroduced the love for reading\n",
        ]

        description_list = [
            "\n US News just ranked Hillcrest High school as a school that had the best theatre program "
            "in the country. After this, Hillcrest went on to win 50 more theatre play awards."
            "This lead Hillcrest to recieve over $500,000 in funding!",

            "Hillcrest High School was awarded the most challenging curriculum in the district! Leading to a more "
            "prepared student body! Not only was the curriculum challenging, \n but the school had the highest "
            "graduation rate in the district",

            "Hillcrest High school, being the only IB school in the district is pulling up district \n test"
            "score averages drastically. Although the school has an extremely challenging \n curriculum, it is"
            "still bringing up the test score averages!",

            "Canyons district was recently interviewed on ABC News for having the best schools in the nation! Including Hillcrest and Alta High School"
            "",

            "Hillcrest High library renovations lead to 1000 students issuing books from the library \nalmost every month, which is almost half the school population, and a feat that very few \n High schools could accomplish!",
        ]

        index = 0

        while True:
            try:
                image_path = picture_list[index % len(picture_list)]
                title = title_list[index % len(title_list)]
                description = description_list[index % len(description_list)]
# round slideshow
                pixmap = QPixmap(image_path)
                rounded_pixmap = QPixmap(pixmap.size())
                rounded_pixmap.fill(QtCore.Qt.transparent)
                painter = QtGui.QPainter(rounded_pixmap)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                path = QtGui.QPainterPath()
                path.addRoundedRect(QtCore.QRectF(rounded_pixmap.rect()), 10.0, 10.0)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                dashboard_slideshow.setPixmap(rounded_pixmap)
# end roundy
                slideshow_title.setText(title)
                slideshow_description.setText(description)

                time.sleep(5)
                index += 1

            except Exception as e:
                print(f"Error occurred: {e}")

            if kill_thread_boolean:
                break

        cursor.close()


# eye class
class PasswordLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(PasswordLineEdit, self).__init__(parent)

        self.echoModeButton = QtWidgets.QToolButton(self)
        self.echoModeButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.echoModeButton.setFocusPolicy(Qt.NoFocus)
        self.echoModeButton.setStyleSheet("border: none;")
        self.echoModeButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.echoModeButton.setIcon(QtGui.QIcon("eye_icon.png"))
        self.echoModeButton.setIconSize(QtCore.QSize(24, 24))
        self.echoModeButton.setToolTip("Show/Hide Password")
        self.echoModeButton.setCheckable(True)
        self.echoModeButton.toggled.connect(self.onEchoModeButtonToggled)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.echoModeButton, 0, Qt.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)

    def onEchoModeButtonToggled(self, checked):
        if checked:
            self.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.setEchoMode(QtWidgets.QLineEdit.Password)


class AddEventPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Add Event")
        self.setParent(parent)
        self.setFixedSize(500,300)

        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setFixedHeight(30)

        self.description_label = QLabel("Description:")
        self.description_edit = QLineEdit()
        self.description_edit.setFixedHeight(30)

        self.address_label = QLabel("Address:")
        self.address_edit = QLineEdit()
        self.address_edit.setFixedHeight(30)

        self.type_label = QLabel("Type:")
        self.type_edit = QLineEdit()
        self.type_edit.setFixedHeight(30)

        self.points_label = QLabel("Points:")
        self.points_edit = QLineEdit()
        self.points_edit.setFixedHeight(30)

        self.year_label = QLabel("Year:")
        self.year_edit = QLineEdit()
        self.year_edit.setFixedHeight(30)

        self.month_label = QLabel("Month:")
        self.month_edit = QLineEdit()
        self.month_edit.setFixedHeight(30)

        self.day_label = QLabel("Day:")
        self.day_edit = QLineEdit()
        self.day_edit.setFixedHeight(30)

        self.latitude_label = QLabel("Latitude:")
        self.latitude_edit = QLineEdit()
        self.latitude_edit.setFixedHeight(30)

        self.longitude_label = QLabel("Longitude:")
        self.longitude_edit = QLineEdit()
        self.longitude_edit.setFixedHeight(30)

        self.image_label = QLabel("Image Link:")
        self.image_edit = QLineEdit()
        self.image_edit.setFixedHeight(30)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_event)
        self.submit_button.setFixedHeight(30)
        self.submit_button.setStyleSheet(SEND_BUTTON_STYLESHEET)

        grid_layout = QGridLayout(self)

        # Add widgets to the grid layout
        grid_layout.addWidget(self.name_label, 0, 0)
        grid_layout.addWidget(self.name_edit, 0, 1)

        grid_layout.addWidget(self.description_label, 0, 2)
        grid_layout.addWidget(self.description_edit, 0, 3)

        grid_layout.addWidget(self.address_label, 1, 0)
        grid_layout.addWidget(self.address_edit, 1, 1)

        grid_layout.addWidget(self.type_label, 1, 2)
        grid_layout.addWidget(self.type_edit, 1, 3)

        grid_layout.addWidget(self.points_label, 2, 0)
        grid_layout.addWidget(self.points_edit, 2, 1)

        grid_layout.addWidget(self.year_label, 2, 2)
        grid_layout.addWidget(self.year_edit, 2, 3)

        grid_layout.addWidget(self.month_label, 3, 0)
        grid_layout.addWidget(self.month_edit, 3, 1)

        grid_layout.addWidget(self.day_label, 3, 2)
        grid_layout.addWidget(self.day_edit, 3, 3)

        grid_layout.addWidget(self.latitude_label, 4, 0)
        grid_layout.addWidget(self.latitude_edit, 4, 1)

        grid_layout.addWidget(self.longitude_label, 4, 2)
        grid_layout.addWidget(self.longitude_edit, 4, 3)

        grid_layout.addWidget(self.image_label, 5, 0)
        grid_layout.addWidget(self.image_edit, 5, 1, 1, 3)  # Span three columns

        grid_layout.addWidget(self.submit_button, 6, 0, 1, 4)  # Span four columns

        self.setLayout(grid_layout)

    def submit_event(self):
        name = self.name_edit.text()
        description = self.description_edit.text()
        address = self.address_edit.text()
        event_type = self.type_edit.text()
        points = self.points_edit.text()
        year = self.year_edit.text()
        month = self.month_edit.text()
        day = self.day_edit.text()
        latitude = self.latitude_edit.text()
        longitude = self.longitude_edit.text()
        image_link = self.image_edit.text()

        conn = sqlite3.connect("identifier.sqlite")
        cursor = conn.cursor()

        query = "INSERT INTO events (NAME, DESCRIPTION, ADDRESS, TYPE, POINTS, YEAR, MONTH, DAY, LATITUDE, LONGITUDE, IMAGE_LINK_SRC) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (name, description, address, event_type, points, year, month, day, latitude, longitude, image_link)

        try:
            cursor.execute(query, values)
            conn.commit()

            print("Event added successfully!")
        except Exception as e:
            print("Error inserting event:", e)
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

        self.accept()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    with open("styling.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    main_window = QtWidgets.QMainWindow()
    ui = Main()
    ui.setup_window(main_window)
    main_window.show()
    sys.exit(app.exec_())
