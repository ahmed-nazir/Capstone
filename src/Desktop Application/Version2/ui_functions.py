from azure.storage.blob import BlobClient
import codecs
import hashlib
import os
import platform
import json
import pymysql
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
from webbrowser import open as webopen
import pandas as pd
import threading
import datetime
import serial.tools.list_ports
import serial
import subprocess

from main import *
from arduino_code_generator import *

''''
try :
    conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:capstonetest850.database.windows.net,1433;Database=Capstone850;Uid=capmaster;Pwd=capstone132!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    cursor = conn.cursor()
except pyodbc.Error as err:
    print(err)
    '''

#Blob storage info
connection_string = 'DefaultEndpointsProtocol=https;AccountName=capstonestorage1;AccountKey=J+U2eXzqIsAg6pP6qFnO9NazZERufddfOQVl4qI5qbFSgzOHuZq5Lc/qR15XO0bjn1SheNrmld+4+AStDPPLSw==;EndpointSuffix=core.windows.net'
container_name = 'testimages'
container_url = 'https://capstonestorage1.blob.core.windows.net/testimages/'

logged_in = False


class over_the_character_limit(Exception):
    "Raised when the user input exceeds the max limit"
    pass


class PandasModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001
    def __init__(self, df=pd.DataFrame(), parent=None):
        super(PandasModel, self).__init__(parent)
        self._dataframe = df
    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()
    def dataFrame(self):
        return self._dataframe
    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)
    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()
    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)
    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype
        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == PandasModel.ValueRole:
            return val
        if role == PandasModel.DtypeRole:
            return dt
        return QtCore.QVariant()
    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            PandasModel.DtypeRole: b'dtype',
            PandasModel.ValueRole: b'value'
        }
        return roles


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
        """
        Logs and authenticates user into the application
        """
        try:
            conn, cursor = connect_to_database()
            username = self.ui.username_field.text()
            password = self.ui.login_password_field.text()

            if len(username) == 0:
                self.ui.login_error_label.setText('Please enter a username')
                raise Exception
            elif len(password) == 0:
                self.ui.login_error_label.setText('Please enter a password')
            else:
                cursor.execute("SELECT * FROM Login WHERE UserName = '{}'".format(username))
                result = cursor.fetchone()

                #Checking if user exists
                if result:
                    salt_hex = result[1]
                    stored_hash = result[2]
                    if (is_correct_password(salt_hex, stored_hash, password)):
                        global logged_in
                        logged_in = True
                        self.ui.account_menu_button.setText(' Log out of ' + username)
                        self.ui.pages_widget.setCurrentWidget(self.ui.homepage)
                        self.ui.username_field.clear()
                        self.ui.login_password_field.clear()
                        self.ui.login_error_label.clear()
                        self.b = 0
                    else:
                        self.ui.login_error_label.setText('Incorrect password, try again')
                        self.ui.username_field.clear()
                        self.ui.login_password_field.clear()
                else:
                    self.ui.login_error_label.setText('User does not exist, try again')
                    self.ui.username_field.clear()
                    self.ui.login_password_field.clear()
        except pymysql.Error as err:
            print(err)
            err_popup = QMessageBox()
            err_popup.setText('Authentication failed, could not connect to server, please ensure you are connected to internet')
            err_popup.setIcon(QMessageBox.Critical)
            x = err_popup.exec_()

    def sign_out(self):
        global logged_in
        logged_in = False
        self.ui.account_menu_button.setText('')
        try:
            if self.isConnected == "Wired":
                UIFunctions.disconnect_wired(self)

            if self.isConnected == "Wireless":
                UIFunctions.disconnect_wireless(self)
        except:
            None
        
        self.pdData = pd.DataFrame(columns=[0])
        model = PandasModel(self.pdData)
        self.ui.data_table.setModel(model)
        self.ui.test_name.clear()
        self.ui.test_purpose.clear()
        self.ui.test_description.clear()
        self.ui.file_path_field.clear()
        self.ui.test_image.clear()
        self.ui.pages_widget.setCurrentWidget(self.ui.login_page)

    def continue_signup(self):
        try:
            conn, cursor = connect_to_database()
            username = self.ui.signup_username_field.text()
            password = self.ui.signup_password_field.text()
            confirm_password = self.ui.confirm_password_field.text()
            first_name = self.ui.firstname_field.text()
            last_name = self.ui.lastname_field.text()
            team_role= self.ui.team_role_dropdown.currentText()

            cursor.execute("SELECT * FROM Users where UserName = '{}'".format(username))
            result = cursor.fetchone()

            if(result):
                self.ui.error_label.setText('Username already taken')
            elif(len(first_name)==0 or len(last_name)==0):
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
                cursor.execute('INSERT INTO Users VALUES ("{}","{}","{}","{}",NULL)'.format(username, first_name, last_name, team_role))
                conn.commit()
                #Generate salt, hashed_password and save to database
                salt, hashed_pass = hash_new_password(password)
                cursor.execute('INSERT INTO Login VALUES ("{}","{}","{}")'.format(username, salt.hex(), hashed_pass.hex()))
                conn.commit()

                self.ui.pages_widget.setCurrentWidget(self.ui.login_page)
                self.ui.signup_username_field.clear()
                self.ui.signup_password_field.clear()
                self.ui.confirm_password_field.clear()
                self.ui.error_label.clear()
        except pymysql.Error as err:
            print(err)
            err_popup = QMessageBox()
            err_popup.setText('Sign up failed, could not connect to server, please ensure you are connected to internet')
            err_popup.setIcon(QMessageBox.Critical)
            x = err_popup.exec_()

    def move_to_submit_test(self):
        if logged_in:
            self.ui.pages_widget.setCurrentWidget(self.ui.submit_page)
        else:
            err_popup = QMessageBox()
            err_popup.setText("Please login to submit tests")
            err_popup.setIcon(QMessageBox.Critical)

            x = err_popup.exec_()

    def browse_and_display_pictures(self):
        fname = QFileDialog.getOpenFileName(None, 'Open File', 'C:\\')
        self.ui.file_path_field.setText(fname[0])
        qpixmap = QPixmap(fname[0])
        scaled_pixmap = qpixmap.scaled(540, 290, aspectRatioMode=QtCore.Qt.KeepAspectRatioByExpanding)
        self.ui.test_image.setPixmap(scaled_pixmap)

    def upload_test_info(self):
        """
        -- Submits test data to DB
        -- Submits user input related to test information to the DB
        -- Uploads test image to azure blob storage
        """
        try:
            err_message = "Oops something went wrong :("
   
            conn, cursor = connect_to_database()

            test_name = self.ui.test_name.text()
            test_purpose = self.ui.test_purpose.text()
            test_desc = self.ui.test_description.text()
            image_url = None
            username = self.ui.account_menu_button.text().split("of ")[1]

            if len(test_name) == 0 or len(test_desc) == 0 or len(test_purpose) == 0:
                err_message = ('Failed to submit test, missing field')
            elif len(test_name) > 100:
                err_message = ('Failed to submit test, name must be less than 100 characters')
                raise Exception
            elif len(test_desc) > 500:
                err_message = ('Failed to submit test, description must be less than 500 characters')
                raise Exception
            elif len(test_purpose) > 500:
                err_message = ('Failed to submit test, purpose must be less than 500 characters')
                raise Exception
                
            image_path = self.ui.file_path_field.text()
            if image_path:
                image_file = os.path.basename(image_path)
                current_time = datetime.datetime.now()
                blob_name = image_file.split(".")[0] + '-' + current_time.strftime("%d-%m-%Y-%H:%M:%S") + "." + image_file.split(".")[1]
                print(blob_name)
                blob__client = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=blob_name)
                with open(self.ui.file_path_field.text(), 'rb') as image:
                    blob__client.upload_blob(image)
                print("Successfully uploaded image!")
                image_url = container_url + blob_name


            cursor.execute("INSERT INTO Test (UserName, TestName, TestPurpose, TestDescription, ImageURL) VALUES ('{}','{}','{}','{}','{}')".format(username, test_name, test_purpose, test_desc, image_url))

            cursor.execute('SELECT MAX(ID) FROM Test')
            test_id = cursor.fetchone()[0]

            cursor.execute('SHOW TABLES')
            num_of_cols = len(self.pdData.axes[1])

            current_tables = []
            for x in cursor.fetchall():
                current_tables.append(x[0])

            for i in range(1, num_of_cols):
                if self.pdData.columns[i] not in current_tables:
                    create_table_sql = """ CREATE TABLE {} ( 
                                    TestID INT NOT NULL,
                                    TimePerformed DATETIME NOT NULL,
                                    Value FLOAT(8) NOT NULL,
                                    PRIMARY KEY (TestID, TimePerformed),
                                    FOREIGN KEY (TestID) REFERENCES Test(ID)
                                );""".format(self.pdData.columns[i])
                    cursor.execute(create_table_sql)
                    conn.commit()
                else:
                    print('nothing to add here')
                
                insert_data_sql = 'INSERT INTO {} (TestID, TimePerformed, Value) VALUES '.format(self.pdData.columns[i])
                for index, row in self.pdData.iterrows():
                    insert_data_sql = insert_data_sql + '({}, {}, {}), '.format(test_id, "'"+row[self.pdData.columns[0]]+"'", row[self.pdData.columns[i]])
                    #insert_data_sql = 'INSERT INTO {} VALUES ({}, {}, {})'.format(self.pdData.columns[i], test_id, "'"+row[self.pdData.columns[0]]+"'", row[self.pdData.columns[i]])
                
                insert_data_sql = insert_data_sql[:-2]
                cursor.execute(insert_data_sql)
                conn.commit()

            conn.close
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Test Successfully Submitted to the Database")
            x = msgBox.exec_()
            UIFunctions.declineData(self)
          
        except Exception as err:
            print(err)
            err_popup = QMessageBox()
            err_popup.setText(err_message)
            err_popup.setIcon(QMessageBox.Information)
            x = err_popup.exec_()

            """        except pymysql.Error() as err:
            print(err)
            err_popup = QMessageBox()
            err_popup.setText('Failed to submit test, could not connect to server, please ensure you are connected to internet')
            err_popup.setIcon(QMessageBox.Information)
            x = err_popup.exec_()"""


    def uploadCSV(self):
        """
        Reads the previous conducted test from the onboard SD card and displays it on the table view for the user
        """
        self.data = []
        try:
            if self.isConnected == "Wired":
                self.ser.write(b'R')
                line = 1
                now = datetime.datetime.now()
                while(line):
                    line = self.ser.readline()
                    if line:
                        string = line.decode()
                        if string[0] == "(" and string[len(string)-3] == ")":
                            filteredByteString = string[1:len(string)-3].split(",")
                            rowData =[now.strftime("%Y-%m-%d %H:%M:%S")]
                            now += datetime.timedelta(seconds=1) 
                            for i in filteredByteString: 
                                rowData.append(i[2:])
                            self.data.append(rowData)
                self.pdData = pd.DataFrame(self.data,columns=self.tableHeader)
                model = PandasModel(self.pdData)
                self.ui.data_table.setModel(model)
                self.ui.data_table.setColumnWidth(0,200)
            
            if self.isConnected == "Wireless":
                err_popup = QMessageBox()
                err_popup.setWindowTitle("Information")
                err_popup.setText("Retrieving Information is only available with a wired connection")
                err_popup.setIcon(QMessageBox.Information)
                x = err_popup.exec_()
        except Exception as e:
            print("Failed")
            print(e)
            return


    def testing_page(self):
        """
        Goes to the testing page only if the PC is connected to the Formulate device
        """
        try:
            if self.isConnected == "Wireless" or self.isConnected == "Wired":
                self.ui.pages_widget.setCurrentWidget(self.ui.view_test_page)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Error")
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("Connect to Formulate Device")
                x = msgBox.exec_()
                    
        except:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Error")
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Connect to Formulate Device")
            x = msgBox.exec_()


    def change_connectivity_page(self):
        if(self.ui.connection_type.currentText() == "Wireless"):
            self.ui.connectivity_page.setCurrentWidget(self.ui.wireless_page)
        elif(self.ui.connection_type.currentText() == "Wired"):
            self.ui.connectivity_page.setCurrentWidget(self.ui.wired_page)
    

    b = 0
    def connect_wireless(self):
        """
        Connect to the Formulate device via WiFi
        """
        try:
            UIFunctions.disconnect_wired(self)
        except:
            print("")

        try:
            subprocess.run(['netsh', 'wlan', 'connect', 'name={}'.format("Formulate")])
            sleep(5)
            ip = '192.168.4.1'
            port = 8080
            self.conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            if(UIFunctions.b == 0):
                self.conn.connect((ip,port))
                UIFunctions.b = 1
                self.ui.wifi_connect.setText("Disconnect")
                self.ui.connection_status_wireless_label.setText("Connected")
                self.ui.wifi_name_label.setText("Formulate")
                self.ui.ip_address_label.setText(ip)
                self.isConnected = "Wireless"
                UIFunctions.ping(self)
            else:
                UIFunctions.disconnect_wireless(self)

        except:
            err_popup = QMessageBox()
            err_popup.setWindowTitle("Connection Failed")
            err_popup.setText("Make sure the device is powered ON")
            err_popup.setIcon(QMessageBox.Critical)
            x = err_popup.exec_()

            


    def disconnect_wireless(self):
        try:
            try:
                self.conn.close()
            except:
                None
            self.isConnected = ""
            self.ui.connection_status_wireless_label.setText("Disconnected")
            self.ui.wifi_name_label.setText("---")
            self.ui.ip_address_label.setText("---")
            UIFunctions.b = 0
            self.ui.wifi_connect.setText("Connect")
            self.ui.detect_sensors_list.setText("")
            output = subprocess.check_output(['netsh', 'wlan', 'show', 'interface']).decode('utf-8')
            ssid_line = [line for line in output.split('\n') if 'SSID' in line][0].strip()
            current_ssid = ssid_line.split(':')[1].strip()
            if current_ssid == "Formulate":
                subprocess.run(['netsh', 'wlan', 'disconnect'])

        except:
            return
    
    def disconnect_wired(self):
        try:
            self.ser.close()
            self.isConnected = ""
            self.ui.connection_status_wired_label.setText("Disconnected")
            self.ui.board_name_label.setText("---")
            self.ui.com_port_label.setText("---")
            UIFunctions.a = 0
            self.ui.wired_connect.setText("Connect")
            self.ui.detect_sensors_list.setText("")
        except:
            return



    def view_dashboard(self):
        webopen("https://powerbi.microsoft.com/en-au/")


    def ping(self):
        self.tableHeader = ['Time']

        with open('src\Desktop Application\Version2\currentConfig.json','r') as f:
            dict = json.load(f)

        val = list(dict.values())
        print(val)


        for i in val:
            self.tableHeader.append(i)

        display_sensors = self.tableHeader[1]
        for i in range(2,len(self.tableHeader)):
            display_sensors =  display_sensors + " | " + self.tableHeader[i]
        
        self.ui.detect_sensors_list.setText(display_sensors)


    def startTest(self):
        #Start button function, starts the test
        self.ui.startButton.setEnabled(False)
        self.ui.startButton.setStyleSheet("background-color: rgb(69, 83, 100);")
        self.ui.stopButton.setEnabled(True)
        self.ui.stopButton.setStyleSheet("QPushButton {background-color: rgb(200, 0, 0);}QPushButton:hover {background-color:  rgb(220,0, 0);}QPushButton:pressed {background-color: rgb(180, 0, 0);}")
        self.run = 1
        self.data = []
        rowData = []

        if self.isConnected == "Wireless":
            self.conn.send('Q'.encode())
            while(self.run):
                try:
                    line = self.conn.recv(1024)
                    now = datetime.datetime.now()
                except:
                    print("Connection Failed")
                    self.run = 0
                    UIFunctions.disconnect_wireless(self)
                    UIFunctions.declineData(self)# read a byte
                    self.ui.startButton.setEnabled(True)
                    self.ui.startButton.setStyleSheet("QPushButton {background-color: rgb(0, 170, 0);} QPushButton:hover {background-color:  rgb(0,190, 0);} QPushButton:pressed {background-color: rgb(0, 150, 0);}")
                    self.ui.stopButton.setEnabled(False)
                    self.ui.stopButton.setStyleSheet("background-color: rgb(69, 83, 100);")

                if line:
                    string = line.decode()
                    print(string)
                    if string[0] == "(" and string[len(string)-3] == ")":
                        filteredByteString = string[1:len(string)-3].split(",")
                        rowData =[now.strftime("%Y-%m-%d %H:%M:%S")]
                        for i in filteredByteString: 
                            rowData.append(i[2:]) 
                        self.data.append(rowData)
                        #self.pdData = pd.DataFrame(self.data,columns=self.tableHeader)
                        #model = PandasModel(self.pdData)
                        #self.ui.data_table.setModel(model)
                        #self.ui.data_table.setColumnWidth(0,200)
                
        if self.isConnected == "Wired":
            self.ser.write(b'G')
            while(self.run):
                try:
                    line = self.ser.readline()
                    now = datetime.datetime.now()  
                except:
                    print("Connection Failed")
                    self.run = 0
                    UIFunctions.disconnect_wired(self)
                    UIFunctions.declineData(self)
                    self.ui.startButton.setEnabled(True)
                    self.ui.startButton.setStyleSheet("QPushButton {background-color: rgb(0, 170, 0);} QPushButton:hover {background-color:  rgb(0,190, 0);} QPushButton:pressed {background-color: rgb(0, 150, 0);}")
                    self.ui.stopButton.setEnabled(False)
                    self.ui.stopButton.setStyleSheet("background-color: rgb(69, 83, 100);")


                if line:
                    string = line.decode()
                    print(string)
                    if string[0] == "(" and string[len(string)-3] == ")":
                        filteredByteString = string[1:len(string)-3].split(",")
                        rowData =[now.strftime("%Y-%m-%d %H:%M:%S")]
                        for i in filteredByteString: 
                            rowData.append(i[2:]) 
                        self.data.append(rowData)
                        #self.pdData = pd.DataFrame(self.data,columns=self.tableHeader)
                        #model = PandasModel(self.pdData)
                        #self.ui.data_table.setModel(model)
                        #self.ui.data_table.setColumnWidth(0,200)
                


    def runProg(self):
        """
        Start another thread to start reading data from the Formulate device
        """
        t1 = threading.Thread(target=lambda: UIFunctions.startTest(self))
        t1.start()


    def stopTest(self):
        """
        Stop reading data from the Formulate device
        """
        self.ui.startButton.setEnabled(True)
        self.ui.startButton.setStyleSheet("QPushButton {background-color: rgb(0, 170, 0);} QPushButton:hover {background-color:  rgb(0,190, 0);} QPushButton:pressed {background-color: rgb(0, 150, 0);}")
        self.ui.stopButton.setEnabled(False)
        self.ui.stopButton.setStyleSheet("background-color: rgb(69, 83, 100);")

        if self.ui.connection_type.currentText() == "Wireless":
            try:
                self.run = 0
                self.conn.send('W'.encode())
                self.pdData = pd.DataFrame(self.data,columns=self.tableHeader)
                model = PandasModel(self.pdData)
                self.ui.data_table.setModel(model)
                self.ui.data_table.setColumnWidth(0,200)

            except Exception as e:
                print(e)

        if self.ui.connection_type.currentText() == "Wired":
            try:
                self.run = 0
                self.ser.write(b'P')
                self.pdData = pd.DataFrame(self.data,columns=self.tableHeader)
                model = PandasModel(self.pdData)
                self.ui.data_table.setModel(model)
                self.ui.data_table.setColumnWidth(0,200)

            except Exception as e:
                print(e)


    def declineData(self):
        self.pdData = pd.DataFrame(columns=[0])
        model = PandasModel(self.pdData)
        self.ui.data_table.setModel(model)
        self.ui.test_name.clear()
        self.ui.test_purpose.clear()
        self.ui.test_description.clear()
        self.ui.file_path_field.clear()
        self.ui.test_image.clear()
        self.ui.pages_widget.setCurrentWidget(self.ui.homepage)


    
    def select_com(self):
        if self.ui.com_port_select.currentText() == "Refresh":
            self.ui.com_port_select.clear()
            self.portData = serial.tools.list_ports.comports()
            i = 1
            self.a=0
            print(self.portData)
            if len(self.portData) != 0:
                for i in range(0,len(self.portData)):
                    print(i)
                    self.portData[i] = str(self.portData[i])
            self.ui.com_port_select.addItem("Refresh")
            self.ui.com_port_select.addItems(self.portData)
        else:
            self.comUserSelect = self.ui.com_port_select.currentText()
            self.comPort = self.comUserSelect[0:4]
            print(self.comPort)
    
    
    a = 0
    def connect_wired(self):
        try:
            UIFunctions.disconnect_wireless(self)
        except:
            print("")
        
        try:
            if(UIFunctions.a == 0):
                self.ser = serial.Serial(self.comPort, 9600, timeout=1)
                UIFunctions.a = 1
                self.ui.wired_connect.setText("Disconnect")
                self.isConnected = "Wired"
                self.ui.connection_status_wired_label.setText("Connected")
                self.ui.board_name_label.setText(self.comUserSelect[7:])
                self.ui.com_port_label.setText(self.comPort)
                sleep(2)
                UIFunctions.ping(self)

            else:
                UIFunctions.disconnect_wired(self)

        except:
            err_popup = QMessageBox()
            err_popup.setWindowTitle("Connection Failed")
            err_popup.setText("Make sure the device is connected and the COM port is not in use by another program")
            err_popup.setIcon(QMessageBox.Critical)
            x = err_popup.exec_()


    def make_config_page(self):
        self.ui.pages_widget.setCurrentWidget(self.ui.add_sensor_page)
        with open('src\Desktop Application\Version2\savedSensors.json','r') as f:
            self.dict = json.load(f)
            f.close()
            self.saved = list(self.dict.keys())
        self.ui.sensor1_header.clear()
        self.ui.sensor2_header.clear()
        self.ui.sensor3_header.clear()
        self.ui.sensor4_header.clear()
        for i in self.saved:
            self.ui.sensor1_header.addItem(i)
            self.ui.sensor2_header.addItem(i)
            self.ui.sensor3_header.addItem(i)
            self.ui.sensor4_header.addItem(i)
        


    def autofill_config(self):
        
        if self.ui.sensor1_header.currentText() in self.saved:
            self.ui.sensor1_readings.setText(self.dict[self.ui.sensor1_header.currentText()]['Readings'])
            self.ui.sensor1_pins.setText(self.dict[self.ui.sensor1_header.currentText()]['Pins'])
            self.ui.sensor1_units.setText(self.dict[self.ui.sensor1_header.currentText()]['Units'])
        
        if self.ui.sensor2_header.currentText() in self.saved:
            self.ui.sensor2_readings.setText(self.dict[self.ui.sensor2_header.currentText()]['Readings'])
            self.ui.sensor2_pins.setText(self.dict[self.ui.sensor2_header.currentText()]['Pins'])
            self.ui.sensor2_units.setText(self.dict[self.ui.sensor2_header.currentText()]['Units'])
        
        if self.ui.sensor3_header.currentText() in self.saved:
            self.ui.sensor3_readings.setText(self.dict[self.ui.sensor3_header.currentText()]['Readings'])
            self.ui.sensor3_pins.setText(self.dict[self.ui.sensor3_header.currentText()]['Pins'])
            self.ui.sensor3_units.setText(self.dict[self.ui.sensor3_header.currentText()]['Units'])
        
        if self.ui.sensor4_header.currentText() in self.saved:
            self.ui.sensor4_readings.setText(self.dict[self.ui.sensor4_header.currentText()]['Readings'])
            self.ui.sensor4_pins.setText(self.dict[self.ui.sensor4_header.currentText()]['Pins'])
            self.ui.sensor4_units.setText(self.dict[self.ui.sensor4_header.currentText()]['Units'])
    


        

    
    def get_config_sensors(self):
        sensors = []
        if (self.ui.sensor1_header.currentText() != "") and (self.ui.sensor1_readings.text() != ""):
            sensor1Header = self.ui.sensor1_header.currentText()
            sensor1Readings = self.ui.sensor1_readings.text().split(',')
            sensor1Pins = self.ui.sensor1_pins.text().split(',')
            sensors.append([sensor1Header,sensor1Readings,sensor1Pins])

        if (self.ui.sensor2_header.currentText() != "") and (self.ui.sensor2_readings.text() != ""):
            sensor2Header = self.ui.sensor2_header.currentText()
            sensor2Readings = self.ui.sensor2_readings.text().split(',')
            sensor2Pins = self.ui.sensor2_pins.text().split(',')
            sensors.append([sensor2Header,sensor2Readings,sensor2Pins])

        if (self.ui.sensor3_header.currentText() != "") and (self.ui.sensor3_readings.text() != ""):
            sensor3Header = self.ui.sensor3_header.currentText()
            sensor3Readings = self.ui.sensor3_readings.text().split(',')
            sensor3Pins = self.ui.sensor3_pins.text().split(',')
            sensors.append([sensor3Header,sensor3Readings,sensor3Pins])

        if (self.ui.sensor4_header.currentText() != "") and (self.ui.sensor4_readings.text() != ""):
            sensor4Header = self.ui.sensor4_header.currentText()
            sensor4Readings = self.ui.sensor4_readings.text().split(',')
            sensor4Pins = self.ui.sensor4_pins.text().split(',')
            sensors.append([sensor4Header,sensor4Readings,sensor4Pins])
        CodeGenerator.generate(sensors)
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Success")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Arduino Code Generated, MAKE SURE TO FLASH THE BOARD")
        x = msgBox.exec_()
        
    def saveConfiguration1(self):
        with open('src\Desktop Application\Version2\savedSensors.json','r') as f:
            dict = json.load(f)
        
        dict[self.ui.sensor1_header.currentText()] = {
            'Readings': self.ui.sensor1_readings.text(),
            'Pins':'',
            'Units':self.ui.sensor1_units.text()
        }

        with open('src\Desktop Application\Version2\savedSensors.json','w') as f:
            json.dump(dict,f,indent=4)
        f.close()
            





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


"""def connect_to_database():
    try :
        #conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:capstonetest850.database.windows.net,1433;Database=Capstone850;Uid=capmaster;Pwd=capstone132!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
        conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:capstonedb2.database.windows.net,1433;Database=CapstoneDB;Uid=capmaster;Pwd=capstone132!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
        cursor = conn.cursor()
        return conn, cursor
    except pyodbc.Error as err:
        print(err)"""

def connect_to_database():
    #try:
    conn = pymysql.connect(host = "mycapstonedb.ctlp2jqtpmzj.us-east-2.rds.amazonaws.com", user = 'capmaster', password = 'capstone132!', database = 'mycapstonedb')
    cursor = conn.cursor()
    return conn, cursor
    #except pymysql.Error as err:
    #    print(err)