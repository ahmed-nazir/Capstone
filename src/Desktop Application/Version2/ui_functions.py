import codecs
import hashlib
import os
import platform
import pyodbc
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PyQt5.QtWidgets import *
import regex as re
import sys

from main import *

conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:capstonetest850.database.windows.net,1433;Database=Capstone850;Uid=capmaster;Pwd=capstone132!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
cursor = conn.cursor()

class UIFunctions(MainWindow):

    def toggleMenu(self, maxWidth, enable):
        if enable:

            # GET WIDTH
            width = self.ui.menu_frame.width()
            maxExtend = maxWidth
            standard = 70

            # SET MAX WIDTH
            if width == 70:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMATION
            self.animation = QPropertyAnimation(self.ui.menu_frame, b"minimumWidth")
            self.animation.setDuration(700)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()
            self.animation.finished.connect(lambda: self.changeText())
    
    def login_into_app(self):
        username = self.ui.username_field.text()
        password = self.ui.password_field.text()

        if len(username) == 0:
            self.ui.error_label.setText('Please enter a username')
        elif len(password) == 0:
            self.ui.error_label.setText('Please enter a password')
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
                    self.ui.pages_widget.setCurrentWidget(self.ui.homepage)
                    self.ui.username_field.clear()
                    self.ui.password_field.clear()
                    self.ui.login_error_label.clear()
                else:
                    self.ui.login_error_label.setText('Incorrect password, try again')
                    self.ui.username_field.clear()
                    self.ui.password_field.clear()
            else:
                self.ui.login_error_label.setText('User does not exist, try again')
                self.ui.username_field.clear()
                self.ui.password_field.clear()

    def continue_signup(self):
        username = self.ui.signup_username_field.text()
        password = self.ui.signup_password_field.text()
        confirm_password = self.ui.confirm_password_field.text()
        first_name = self.ui.firstname_field.text()
        last_name = self.ui.lastname_field.text()
        team_role= self.ui.team_role_dropdown.currentText()

        if(len(first_name)==0 or len(last_name)==0):
            self.ui.error_label.setText('Please fill in missing fields')
        elif(len(username) < 4):
            self.ui.error_label.setText('Username requires at least 4 characters')
        elif(len(password) < 8):
            self.ui.error_label.setText('Password requires at least 8 characters')
        elif(re.search(r'[0-9]', password) is None):
            self.ui.error_label.setText('Password requires at least one number')
        elif(re.search(r'[a-zA-Z]', password) is None):
            self.ui.error_label.setText('Password requires at least one alphabet')
        elif(re.search(r'\W', password) is None):
            self.ui.error_label.setText('Password requires at least one non-alphanumeric character')
        elif(password != confirm_password):
            self.ui.error_label.setText('Password does not match')
        else:
            #Store User information first
            cursor.execute('INSERT INTO Users VALUES (?,?,?,?,NULL)', username, first_name, last_name, team_role)
            conn.commit()
            #Generate salt, hashed_password and save to database
            salt, hashed_pass = hash_new_password(password)
            cursor.execute('INSERT INTO Login VALUES (?,?,?)', username, salt.hex(), hashed_pass.hex())
            conn.commit()

            self.ui.pages_widget.setCurrentWidget(self.ui.homepage)
            self.ui.signup_username_field.clear()
            self.ui.signup_password_field.clear()
            self.ui.confirm_password_field.clear()
            self.ui.error_label.clear()

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


