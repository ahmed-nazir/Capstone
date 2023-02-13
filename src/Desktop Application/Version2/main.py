import codecs
import hashlib
import platform
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PyQt5.QtWidgets import *
import sys

#Importing Main Mindow class from GUI file
from ui_main import Ui_MainWindow

#Importing UI functions
from ui_functions import *


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Setting up pages
        UIFunctions.setup_page(self, 'add new sensor')
        UIFunctions.setup_page(self, 'login page')
        UIFunctions.setup_page(self, 'sign up page')

        #Toggling menu
        #self.ui.toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 250, True))

        #Logging in
        self.ui.sign_in_button.clicked.connect(lambda: UIFunctions.login_into_app(self))

        #Signing up
        self.ui.continue_sign_up.clicked.connect(lambda: UIFunctions.continue_signup(self))

        #Add new sensor
        self.ui.submit_new_sensor.clicked.connect(lambda: UIFunctions.submit_new_sensor(self))

        #submit_test
        self.ui.submit_test_button.clicked.connect(lambda: UIFunctions.move_to_submit_test(self))

        #Upload image
        self.ui.upload_image_button.clicked.connect(lambda: UIFunctions.browse_and_display_pictures(self))

        #Upload test data/info
        self.ui.upload_test_info_button.clicked.connect(lambda: UIFunctions.upload_test_info(self))

        #Changing pages
        #Login page
        self.ui.sign_up_button.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.sign_up_page))
        self.ui.sign_in_as_guest_button.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.homepage))
        self.ui.account_menu_button.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.login_page))
        #Signup page
        self.ui.login_return_button.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.login_page))
        #Homepage
        self.ui.start_test_button.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.view_test_page))
        self.ui.home_menu_button.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.homepage))
        #View test page
        self.ui.decline_test_button.clicked.connect(lambda: UIFunctions.declineData(self))
        #Submit test 
        
        
        #Change connectivity page
        self.ui.connection_type.currentTextChanged.connect(lambda: UIFunctions.change_connectivity_page(self))

        #Connect to wifi button
        self.ui.wifi_connect.clicked.connect(lambda: UIFunctions.connect_wireless(self))
        
        #Connect dashboard button
        self.ui.view_dashboard_button.clicked.connect(lambda: UIFunctions.view_dashboard(self))

        #Connect detect senor button
        #self.ui.detect_sensors.clicked.connect(lambda: UIFunctions.ping(self))

        #Connect start button
        self.ui.startButton.clicked.connect(lambda: UIFunctions.runProg(self))

        #Stop test button
        self.ui.stopButton.clicked.connect(lambda: UIFunctions.stopTest(self))

        #self.ui.decline_test_button.clicked.connect(lambda: UIFunctions.declineData(self))

        self.ui.com_port_select.activated.connect(lambda: UIFunctions.select_com(self))

    
        self.ui.wired_connect.clicked.connect(lambda: UIFunctions.connect_wired(self))

        self.ui.uploadCSVButton.clicked.connect(lambda: UIFunctions.uploadCSV(self))

        self.show()

    

    def changeText(self):
        if self.ui.home_menu.text() == '':
            self.ui.home_menu.setText('  Home')
            self.ui.view_test_menu.setText('  View')
            self.ui.submit_menu.setText('  Submit')
            self.ui.login_menu.setText('  Login')
        else:
            self.ui.home_menu.setText('')
            self.ui.view_test_menu.setText('')
            self.ui.submit_menu.setText('')
            self.ui.login_menu.setText('')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())