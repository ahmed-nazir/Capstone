import codecs
import hashlib
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget, QFileDialog
from PyQt5.QtGui import QPixmap
import os
import regex as re
import time
import pyodbc

conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:capstonetest850.database.windows.net,1433;Database=Capstone850;Uid=capmaster;Pwd=capstone132!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
cursor = conn.cursor()

def hash_new_password(password):
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """
    salt = os.urandom(32)
    hashed_pass = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    return salt, hashed_pass

def is_correct_password(salt_hex, stored_hash, pass_to_check):
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    salt_bytes = codecs.decode(salt_hex, 'hex_codec')
    new_hash = hashlib.pbkdf2_hmac('sha256', pass_to_check.encode('utf-8'), salt_bytes, 100000)
    if(new_hash.hex() == stored_hash):
        return True
    else:
        return False

class Welcome_Screen(QDialog):
    def __init__(self):
        super(Welcome_Screen, self).__init__()
        loadUi("welcomeScreen.ui", self)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)

        #Button Connections
        self.sign_in.clicked.connect(self.login_into_app)
        self.sign_in_as_guest.clicked.connect(self.go_to_homepage)
        self.sign_up.clicked.connect(self.go_to_signup_screen)

    def go_to_homepage(self):
        widget.setCurrentIndex(1)
    
    def go_to_signup_screen(self):
        widget.setCurrentIndex(2)

    def login_into_app(self):
        username = self.username_field.text()
        password = self.password_field.text()

        if len(username) == 0:
            self.error_label.setText('Please enter a username')
        elif len(password) == 0:
            self.error_label.setText('Please enter a password')
        else:
            cursor.execute("SELECT * FROM Login WHERE UserName = ?", username)
            result = cursor.fetchone()

            if result:
                print('User exists, checking password')
                salt_hex = result[1]
                stored_hash = result[2]
                if (is_correct_password(salt_hex, stored_hash, password)):
                    #self.error_label.setText('Successful login!')
                    #time.sleep(2)
                    widget.setCurrentIndex(1)
                    self.username_field.clear()
                    self.password_field.clear()
                    self.error_label.clear()
                else:
                    self.error_label.setText('Incorrect password, try again')
                    self.username_field.clear()
                    self.password_field.clear()
            else:
                self.error_label.setText('User does not exist, try again')
                self.username_field.clear()
                self.password_field.clear()

class Homepage(QDialog):
    def __init__(self):
        super(Homepage, self).__init__()
        loadUi("leak_homepage.ui", self)

        #Button Connections
        self.sign_out.clicked.connect(self.sign_out_of_app)

    def sign_out_of_app(self):
        widget.setCurrentIndex(0)

class HomeScreen(QDialog):
    def __init__(self):
        super(HomeScreen, self).__init__()
        loadUi("home_screen.ui", self)

        #Altering user's test table
        self.user_test_table.setColumnWidth(0, 100)
        self.user_test_table.setColumnWidth(1, 275)
        self.user_test_table.setColumnWidth(2, 273)

        #Button Connections
        #self.sign_out.clicked.connect(self.sign_out_of_app)
        self.start_testing.clicked.connect(self.go_to_testing_screen)
        self.view_your_tests.clicked.connect(self.go_to_view_tests)
        self.sign_out.clicked.connect(self.sign_out_of_app)
        self.parameters_upload_image.clicked.connect(self.upload_test_image)


    def go_to_testing_screen(self):
        self.tabWidget.setCurrentIndex(1)

    def go_to_view_tests(self):
        self.tabWidget.setCurrentIndex(3)

    def sign_out_of_app(self):
        widget.setCurrentIndex(0)

    def upload_test_image(self):
        fname = QFileDialog.getOpenFileName(None, 'Open File', 'C:\\Users\Muhanad\Documents')
        self.file_path.setText(fname[0])
        qpixmap = QPixmap(fname[0])
        scaled_pixmap = qpixmap.scaled(720, 400, aspectRatioMode=QtCore.Qt.KeepAspectRatioByExpanding)
        self.parameters_image_label.setPixmap(scaled_pixmap)

class Signup_Screen(QDialog):
    def __init__(self):
        super(Signup_Screen, self).__init__()
        loadUi("signup_screen.ui",self)
        default_profile_image = QPixmap("profile_placeholder.png")
        self.profile_image_label.setPixmap(default_profile_image)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)

        #Button Connections
        self.continue_sign_up.clicked.connect(self.continue_signup)
        self.upload.clicked.connect(self.upload_pf_image)
        self.welcome_return.clicked.connect(self.return_to_welcome_screen)


    def return_to_welcome_screen(self):

        widget.setCurrentIndex(0)
        self.username_field.clear()
        self.password_field.clear()
        self.confirm_password_field.clear()
        self.error_label.clear()

    def continue_signup(self):
        username = self.username_field.text()
        password = self.password_field.text()
        confirm_password = self.confirm_password_field.text()
        first_name = self.first_name_field.text()
        last_name = self.last_name_field.text()
        team_role= self.team_role_dropdown.currentText()

        if(len(first_name)==0 or len(last_name)==0):
            self.error_label.setText('Please fill in missing fields')
        elif(len(username) < 4):
            self.error_label.setText('Username requires at least 4 characters')
        elif(len(password) < 8):
            self.error_label.setText('Password requires at least 8 characters')
        elif(re.search(r'[0-9]', password) is None):
            self.error_label.setText('Password requires at least one number')
        elif(re.search(r'[a-zA-Z]', password) is None):
            self.error_label.setText('Password requires at least one alphabet')
        elif(re.search(r'\W', password) is None):
            self.error_label.setText('Password requires at least one non-alphanumeric character')
        elif(password != confirm_password):
            self.error_label.setText('Password does not match')
        else:
            #Store User information first
            cursor.execute('INSERT INTO Users VALUES (?,?,?,?,NULL)', username, first_name, last_name, team_role)
            conn.commit()
            #Generate salt, hashed_password and save to database
            salt, hashed_pass = hash_new_password(password)
            cursor.execute('INSERT INTO Login VALUES (?,?,?)', username, salt.hex(), hashed_pass.hex())
            conn.commit()

            widget.setCurrentIndex(1)
            self.username_field.clear()
            self.password_field.clear()
            self.confirm_password_field.clear()
            self.error_label.clear()

    def upload_pf_image(self):
        fname = QFileDialog.getOpenFileName(None, 'Open File', 'C:\\Users\Muhanad\Documents')
        pf_image_qpixmap = QPixmap(fname[0])
        self.profile_image_label.setPixmap(pf_image_qpixmap)
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome=Welcome_Screen()
    widget = QStackedWidget()
    widget.addWidget(welcome)
    #homepage = Homepage()
    #widget.addWidget(homepage)
    homescreen = HomeScreen()
    widget.addWidget(homescreen)
    signup_screen = Signup_Screen()
    widget.addWidget(signup_screen)
    widget.setFixedHeight(930)
    widget.setFixedWidth(1300)
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")