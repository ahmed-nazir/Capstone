from azure.storage.blob import BlobClient
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
import socket
import os
from time import sleep
from webbrowser import open

from main import *

try :
    conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:capstonetest850.database.windows.net,1433;Database=Capstone850;Uid=capmaster;Pwd=capstone132!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor = conn.cursor()
except pyodbc.Error as err:
    print(err)

#Blob storage info
connection_string = 'DefaultEndpointsProtocol=https;AccountName=capstonestorage1;AccountKey=J+U2eXzqIsAg6pP6qFnO9NazZERufddfOQVl4qI5qbFSgzOHuZq5Lc/qR15XO0bjn1SheNrmld+4+AStDPPLSw==;EndpointSuffix=core.windows.net'
container_name = 'testimages'
container_url = 'https://capstonestorage1.blob.core.windows.net/testimages/'

logged_in = False

class UIFunctions(MainWindow):

    def setup_page(self, page_name):
        if page_name == 'homepage':
            self.ui.connection_type.addItem(['Wired','Wireless'])
        elif page_name == 'sign up page':
            self.ui.team_role_dropdown.addItems(['Admin', 'Team Lead', 'Member'])
            self.ui.signup_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
            self.ui.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        elif page_name == 'login page':
            self.ui.login_password_field.setEchoMode(QtWidgets.QLineEdit.Password)

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
        password = self.ui.login_password_field.text()

        if len(username) == 0:
            self.ui.login_error_label.setText('Please enter a username')
        elif len(password) == 0:
            self.ui.login_error_label.setText('Please enter a password')
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
                    global logged_in
                    logged_in = True
                    self.ui.pages_widget.setCurrentWidget(self.ui.homepage)
                    self.ui.username_field.clear()
                    self.ui.login_password_field.clear()
                    self.ui.login_error_label.clear()
                else:
                    self.ui.login_error_label.setText('Incorrect password, try again')
                    self.ui.username_field.clear()
                    self.ui.login_password_field.clear()
            else:
                self.ui.login_error_label.setText('User does not exist, try again')
                self.ui.username_field.clear()
                self.ui.login_password_field.clear()

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

    def submit_new_sensor(self):
        measurement_name = self.ui.measurement_name_field.text()
        units_of_measurement = self.ui.units_of_measurement_field.text()
        
        names_of_values = self.ui.names_of_values_field.text()
        name_of_sensor = self.ui.name_of_sensor_field.text()


        sql_columns = ''
        for value in names_of_values.split(', '):
            sql_columns = sql_columns + '{} FLOAT(8) NOT NULL, '.format(value)
            
        create_table_sql = """ CREATE TABLE {} ( 
                            TestID INT NOT NULL FOREIGN KEY REFERENCES Test(ID),
                            TimePerformed DATETIME NOT NULL,
                            {}
                            PRIMARY KEY (TestID, TimePerformed));""".format(measurement_name, sql_columns)

        cursor.execute(create_table_sql)
        conn.commit()

        #Adding new sensor measurement to measurements table
        cursor.execute('INSERT INTO Measurements VALUES (?,?,?)', measurement_name, units_of_measurement, name_of_sensor)
        conn.commit()

    def move_to_submit_test(self):
        if logged_in:
            self.ui.pages_widget.setCurrentWidget(self.ui.submit_page)
        else:
            err_popup = QMessageBox()
            err_popup.setText("Please login to submit tests")
            err_popup.setIcon(QMessageBox.Critical)

            x = err_popup.exec_()

    def browse_and_display_pictures(self):
        fname = QFileDialog.getOpenFileName(None, 'Open File', 'C:\\Users\Muhanad\Documents')
        self.ui.file_path_field.setText(fname[0])
        qpixmap = QPixmap(fname[0])
        scaled_pixmap = qpixmap.scaled(540, 290, aspectRatioMode=QtCore.Qt.KeepAspectRatioByExpanding)
        self.ui.test_image.setPixmap(scaled_pixmap)

    def upload_test_info(self):
        image_path = self.ui.file_path_field.text()
        image_file = os.path.basename(image_path)
        blob_name = image_file
        blob__client = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=blob_name)
        with open(self.ui.file_path_field.text(), 'rb') as image:
            blob__client.upload_blob(image)
        print("Successfully uploaded image!")

        blob_url = container_url + blob_name

        cursor.execute("SELECT MAX(ID) FROM Test")
        test_id = cursor.fetchone()[0]
        print(test_id)

        cursor.execute("INSERT INTO Test_Notes VALUES (?, ?, ?, ?)", test_id, self.ui.submit_first_name_field.text(), self.ui.submit_last_name_field.text(), blob_url)
        conn.commit()
        print('Successfully submitted notes to database!')

    def change_connectivity_page(self):
        if(self.ui.connection_type.currentText() == "Wireless"):
            self.ui.connectivity_page.setCurrentWidget(self.ui.wireless_page)
        elif(self.ui.connection_type.currentText() == "Wired"):
            self.ui.connectivity_page.setCurrentWidget(self.ui.wired_page)
    
    def connect_wireless(self):
        os.system(f'''cmd /c "netsh wlan connect name=Formulate"''')
        sleep(3)
        ip = '192.168.4.1'
        port = 8080
        self.conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.conn.connect((ip,port))
            self.ui.connection_status_label.setText("Connected")
            self.ui.wifi_name_label.setText("Formulate")
            self.ui.ip_address_label.setText(ip)
            self.ping()

        except:
            print("Connection Failed")
            self.ui.connection_status_label.setText("Disconnected")
            self.ui.wifi_name_label.setText("---")
            self.ui.ip_address_label.setText("---")

    def view_dashboard(self):
        open("https://powerbi.microsoft.com/en-au/")


    def ping(self):
        sensorList = []
        self.conn.send('Q'.encode())
        line = conn.recv(1024)   # read a byt
        print(line)  # read a byte
        if line:
            string = line.decode()
            if string[0] == "(" and string[len(string)-3] == ")":
                print(string)
        self.conn.send('W'.encode())
        self.conn.close()









# DATABASE AUTHENTICATION FUNCTIONS
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


