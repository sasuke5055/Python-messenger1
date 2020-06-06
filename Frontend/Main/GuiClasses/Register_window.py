from PyQt5 import QtWidgets, uic, Qt
from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QLabel, QPushButton, QMessageBox
from SidePackage.Validation import validate_email, validate_password
from SidePackage.Error import pop_alert
import urllib.request
import urllib.parse
import requests

class RegisterWindow(QtWidgets.QMainWindow):
    def __init__(self, LoginWindow):
        super(RegisterWindow, self).__init__()
        uic.loadUi('UiFiles/Register_window.ui', self)
        self.LoginWindow = LoginWindow
        self.minimum_pass_len = 4

        self.initUi()

        self.show()

    def initUi(self):
         self.button_register = self.findChild(QtWidgets.QPushButton, 'button_register')
         self.lineEdit_login = self.findChild(QtWidgets.QLineEdit, 'lineEdit_login')
         self.lineEdit_pass = self.findChild(QtWidgets.QLineEdit, 'lineEdit_pass')
         self.lineEdit_pass2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_pass2')
         self.lineEdit_fname = self.findChild(QtWidgets.QLineEdit, 'lineEdit_fname')
         self.lineEdit_sname = self.findChild(QtWidgets.QLineEdit, 'lineEdit_sname')
         self.lineEdit_email = self.findChild(QtWidgets.QLineEdit, 'lineEdit_email')
         self.lineEdit_email2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_email2')

         self.button_register.pressed.connect(self.register_button_pressed)

    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.LoginWindow.setDisabled(False)

    def register_button_pressed(self):
        # Firstly check for empty labels
        if self.lineEdit_login.text() == "" or \
                self.lineEdit_pass.text() == "" or \
                self.lineEdit_pass2.text() == "" or \
                self.lineEdit_fname.text() == "" or \
                self.lineEdit_sname.text() == "" or \
                self.lineEdit_email.text() == "" or \
                self.lineEdit_email2.text() == "":
            pop_alert("Uzupełnij wszystkie pola")
            return

        # Check data
        if not self.check_password():
            self.lineEdit_pass.setText("")
            self.lineEdit_pass2.setText("")
            pop_alert("Podane hasła się różnią")
            return
        if not self.check_email():
            self.lineEdit_email.setText("")
            self.lineEdit_email2.setText("")
            pop_alert("Podane adresy email się różnią")
            return

        # Validate data
        if not validate_password(self.lineEdit_pass.text()):
            self.lineEdit_pass.setText("")
            self.lineEdit_pass2.setText("")
            pop_alert(f"Hasło nie spełnia warunków.\nPowinno składać się \nz minimum {self.minimum_pass_len} znaków")
            return
        if not validate_email(self.lineEdit_email.text()):
            self.lineEdit_email.setText("")
            self.lineEdit_email2.setText("")
            pop_alert("Podaj poprawne adres email")
            return
        
        self.send_request_to_server()
        # Todo: Czekaj na odpowiedź od serwera i wyrzuć powodzenie lub niepowodzenie
        self.close()

    def check_email(self):
        # Check if 2 emails are the same
        if not self.lineEdit_email.text() == self.lineEdit_email2.text():
            return False
        return True

    def check_password(self):
        # Check if 2 passwords are the same
        if not self.lineEdit_pass.text() == self.lineEdit_pass2.text():
            return False

        # Another conditions
        return True

    def send_request_to_server(self):
        # try for server present
        try:
            login = self.lineEdit_login.text()
            password = self.lineEdit_pass.text()
            first_name = self.lineEdit_fname.text()
            last_name = self.lineEdit_sname.text()
            email = self.lineEdit_sname.text()
            url = self.LoginWindow.URLs[0] + '/chat/rest-auth/registration/'
            payload = {'username': login, 'password1': password, 'password2': password}
            r = requests.post(url, data=payload)
        except:
            pop_alert("Błąd sieci, sprawdź połączenie.")
