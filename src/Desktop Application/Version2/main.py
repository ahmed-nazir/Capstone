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

        #Toggling menu
        self.ui.toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 250, True))

        #Logging in
        self.ui.sign_in.clicked.connect(lambda: UIFunctions.login_into_app(self))

        #Signing up
        self.ui.continue_sign_up.clicked.connect(lambda: UIFunctions.continue_signup(self))

        #Changing pages
        self.ui.home_menu.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.homepage))
        self.ui.view_test_menu.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.view_test_page))
        self.ui.submit_menu.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.submit_page))
        self.ui.login_menu.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.login_page))
        self.ui.sign_up.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.sign_up_page))
        self.ui.welcome_return.clicked.connect(lambda: self.ui.pages_widget.setCurrentWidget(self.ui.login_page))

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