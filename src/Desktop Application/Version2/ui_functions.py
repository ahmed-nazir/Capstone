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
#from webbrowser import open
import pandas as pd
import threading
import datetime
import serial.tools.list_ports
import serial

import csv

from main import *

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
        conn, cursor = connect_to_database()
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
                    self.ui.account_menu_button.setText(username)
                    print(self.ui.account_menu_button.text())
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

    def continue_signup(self):
        conn, cursor = connect_to_database()
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
        conn, cursor = connect_to_database()
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
        fname = QFileDialog.getOpenFileName(None, 'Open File', 'C:\\')
        self.ui.file_path_field.setText(fname[0])
        qpixmap = QPixmap(fname[0])
        scaled_pixmap = qpixmap.scaled(540, 290, aspectRatioMode=QtCore.Qt.KeepAspectRatioByExpanding)
        self.ui.test_image.setPixmap(scaled_pixmap)

    def upload_test_info(self):
        try:
            conn, cursor = connect_to_database()
            
            image_path = self.ui.file_path_field.text()
            image_file = os.path.basename(image_path)
            blob_name = image_file
            blob__client = BlobClient.from_connection_string(conn_str=connection_string, container_name=container_name, blob_name=blob_name)
            with open(self.ui.file_path_field.text(), 'rb') as image:
                blob__client.upload_blob(image)
            print("Successfully uploaded image!")

            blob_url = container_url + blob_name

            test_name = self.ui.test_name.text()
            test_purpose = self.ui.test_purpose.text()
            test_desc = self.ui.test_description.text()
            image_url = None
            username = self.ui.account_menu_button.text()
            
            cursor.execute("INSERT INTO Test VALUES (?,?,?,?,?)", username, test_name, test_purpose, test_desc, image_url)

            cursor.execute('SELECT MAX(ID) FROM TEST')
            last_index = cursor.fetchone()[0]

            cursor.execute('SELECT name FROM sys.tables')
            num_of_cols = len(self.pdData.axes[1])

            current_tables = []
            for x in cursor.fetchall():
                current_tables.append(x[0])

            for i in range(1, num_of_cols):
                if self.pdData.columns[i] not in current_tables:
                    create_table_sql = """ CREATE TABLE {} ( 
                                TestID INT NOT NULL FOREIGN KEY REFERENCES Test(ID),
                                TimePerformed DATETIME NOT NULL,
                                Value FLOAT(8) NOT NULL,
                                PRIMARY KEY (TestID, TimePerformed));""".format(self.pdData.columns[i])
                    cursor.execute(create_table_sql)
                    conn.commit()
                else:
                    print('nothing to add here')
                
                for index, row in self.pdData.iterrows():
                    insert_data_sql = 'INSERT INTO {} VALUES ({}, {}, {})'.format(self.pdData.columns[i], last_index, "'"+row[self.pdData.columns[0]]+"'", row[self.pdData.columns[i]])
                    sql = "INSERT INTO Temperature1 VALUES (?, ?, ?)",last_index, "'"+row[self.pdData.columns[0]]+"'", row[self.pdData.columns[i]]
                    cursor.execute(insert_data_sql)
                conn.commit()

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("Test Successfully Submitted to the Database")
            x = msgBox.exec_()
            UIFunctions.declineData(self)
            

        except Exception as e:
            print(e)


    def uploadCSV(self):
        try:
            fname = QFileDialog.getOpenFileName(None, 'Open File', 'C:\\')
            print(fname[0])
            file = open(fname[0])
            type(file)

            csvreader = csv.reader(file)
            header = []
            header = ['Time'] + next(csvreader)
            print(header)


            rows = []
            timeInsert = datetime.datetime(1990,1,1,0,0,0)
            for row in csvreader:
                rows.append(row)

            for i in range(len(rows)):
                timeInsert += datetime.timedelta(seconds=1)
                rows[i] = [timeInsert]+ rows[i][:]
                
            self.pdData = pd.DataFrame(rows,columns=header)
            model = PandasModel(self.pdData)
            self.ui.data_table.setModel(model)
            self.ui.data_table.setColumnWidth(0,200)

            file.close()
        except:
            return



    def change_connectivity_page(self):
        if(self.ui.connection_type.currentText() == "Wireless"):
            self.ui.connectivity_page.setCurrentWidget(self.ui.wireless_page)
        elif(self.ui.connection_type.currentText() == "Wired"):
            self.ui.connectivity_page.setCurrentWidget(self.ui.wired_page)
    b = 0
    def connect_wireless(self):
        #os.system(f'''cmd /c "netsh wlan connect name=Formulate"''')
        #sleep(3)
        try:
            UIFunctions.disconnect_wired(self)
        except:
            print("")
            
        ip = '192.168.4.1'
        port = 8080
        self.conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            if(UIFunctions.b == 0):
                UIFunctions.b = 1
                self.ui.wifi_connect.setText("Disconnect")
                self.conn.connect((ip,port))
                self.ui.connection_status_wireless_label.setText("Connected")
                self.ui.wifi_name_label.setText("Formulate")
                self.ui.ip_address_label.setText(ip)
                self.isConnected = "Wireless"
                sleep(2)
                UIFunctions.ping(self)

            else:
                UIFunctions.disconnect_wireless(self)

        except Exception as e:
            print("Connection Failed")
            err_popup = QMessageBox()
            err_popup.setText("Connection Failed: Make sure to connect to Formulate Wifi")
            err_popup.setIcon(QMessageBox.Critical)
            print(e)
            x = err_popup.exec_()
            self.ui.connection_status_wireless_label.setText("Disconnected")
            self.ui.wifi_name_label.setText("---")
            self.ui.ip_address_label.setText("---")
            


    def disconnect_wireless(self):
        try:
            self.conn.close()
            self.ui.connection_status_wireless_label.setText("Disconnected")
            self.ui.wifi_name_label.setText("---")
            self.ui.ip_address_label.setText("---")
            UIFunctions.b = 0
            self.ui.wifi_connect.setText("Connect")
            self.ui.detect_sensors_list.setText("")
        except:
            return
    
    def disconnect_wired(self):
        try:
            self.ser.close()
            self.ui.connection_status_wired_label.setText("Disconnected")
            self.ui.board_name_label.setText("---")
            self.ui.com_port_label.setText("---")
            UIFunctions.a = 0
            self.ui.wired_connect.setText("Connect")
            self.ui.detect_sensors_list.setText("")
        except:
            return



    def view_dashboard(self):
        open("https://powerbi.microsoft.com/en-au/")


    def ping(self):
        # Ping the Arduino to get the currently programmed sensors
        sensorType = []
        sensorNumber = []
        sensorTypeName = []
        self.tableHeader = ['Time']

        if self.isConnected == "Wireless":
            self.conn.send('Q'.encode())
            for i in range(2):
                line = self.conn.recv(1024)  
                if line:
                    byteString = line.decode()
            self.conn.send('W'.encode())
        
        if self.isConnected == "Wired":
            self.ser.write(b'G')
            for i in range(2):
                line = self.ser.readline()   
                if line:
                    byteString = line.decode()
            self.ser.write(b'P')

        filteredByteString = byteString[1:len(byteString)-3].split(",")

        for i in filteredByteString:
            sensorType.append(i[0])         
            sensorNumber.append(i[1])

        A = {'sensorType': 'AccelerationX', 'unit': 'm/s^2'}
        B = {'sensorType': 'AccelerationY', 'unit': 'm/s^2'}
        C = {'sensorType': 'AccelerationZ', 'unit': 'm/s^2'}
        D = {'sensorType': 'Temperature', 'unit': '° celsius'}
        E = {'sensorType': 'Humidity', 'unit': '%'}
        converter = [A, B, C, D, E]
        inputLength = len(sensorType)

        for i in range(inputLength):
            capsAscii = ord(sensorType[i]) 
            sensorTypeName.append(converter[capsAscii-65]['sensorType'])

        for i in range(inputLength):
            self.tableHeader.append(sensorTypeName[i] + sensorNumber[i])

        display_sensors = self.tableHeader[1]
        for i in range(2,len(self.tableHeader)):
            display_sensors =  display_sensors + " | " + self.tableHeader[i]
        
        self.ui.detect_sensors_list.setText(display_sensors)
    '''
        headerData = pd.DataFrame(columns=self.tableHeader[1:])
        model = PandasModel(headerData)
        self.ui.detected_sensors_table.setModel(model)
'''

    def startTest(self):
        #Start button function, starts the test
        self.ui.startButton.setEnabled(False)
        self.ui.startButton.setStyleSheet("background-color: rgb(69, 83, 100);")
        self.ui.stopButton.setEnabled(True)
        self.ui.stopButton.setStyleSheet("background-color: rgb(200, 0, 0);")
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
                    self.ui.startButton.setStyleSheet("background-color: rgb(0, 170, 0);")
                    self.ui.stopButton.setEnabled(False)
                    self.ui.stopButton.setStyleSheet("background-color: rgb(69, 83, 100);")

                if line:
                    string = line.decode()
                    if string[0] == "(" and string[len(string)-3] == ")":
                        print(string)
                        filteredByteString = string[1:len(string)-3].split(",")
                        rowData =[now.strftime("%Y-%m-%d %H:%M:%S")]
                        for i in filteredByteString: 
                            rowData.append(i[2:]) 
                        self.data.append(rowData)
                        self.pdData = pd.DataFrame(self.data,columns=self.tableHeader)
                        model = PandasModel(self.pdData)
                        self.ui.data_table.setModel(model)
                        self.ui.data_table.setColumnWidth(0,200)
                
                    
                            
        
        if self.isConnected == "Wired":
            self.ser.write(b'G')
            while(self.run):
                try:
                    line = self.ser.readline()
                    now = datetime.datetime.now()   # read a byte
                except:
                    print("Connection Failed")
                    self.run = 0
                    UIFunctions.disconnect_wired(self)
                    UIFunctions.declineData(self)
                    self.ui.startButton.setEnabled(True)
                    self.ui.startButton.setStyleSheet("background-color: rgb(0, 170, 0);")
                    self.ui.stopButton.setEnabled(False)
                    self.ui.stopButton.setStyleSheet("background-color: rgb(69, 83, 100);")


                if line:
                    string = line.decode()
                    if string[0] == "(" and string[len(string)-3] == ")":
                        print(string)
                        filteredByteString = string[1:len(string)-3].split(",")
                        rowData =[now.strftime("%Y-%m-%d %H:%M:%S")]
                        for i in filteredByteString: 
                            rowData.append(i[2:]) 
                        self.data.append(rowData)
                        self.pdData = pd.DataFrame(self.data,columns=self.tableHeader)
                        model = PandasModel(self.pdData)
                        self.ui.data_table.setModel(model)
                        self.ui.data_table.setColumnWidth(0,200)
                


    def runProg(self):
        #Start Button threading function
        t1 = threading.Thread(target=lambda: UIFunctions.startTest(self))
        t1.start()


    def stopTest(self):
        #Stop Button Function
        self.ui.startButton.setEnabled(True)
        self.ui.startButton.setStyleSheet("background-color: rgb(0, 170, 0);")
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
        #Connects and disconnects to arduino
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


def connect_to_database():
    try :
        #conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:capstonetest850.database.windows.net,1433;Database=Capstone850;Uid=capmaster;Pwd=capstone132!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
        conn = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:capstonedb2.database.windows.net,1433;Database=CapstoneDB;Uid=capmaster;Pwd=capstone132!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
        cursor = conn.cursor()
        return conn, cursor
    except pyodbc.Error as err:
        print(err)