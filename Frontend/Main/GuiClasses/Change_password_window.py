import requests
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from SidePackage.Validation import validate_password
from SidePackage.Error import pop_alert


class ChangePasswordWindow(QtWidgets.QMainWindow):
    def __init__(self, MainWindow, URLs):
        super(ChangePasswordWindow, self).__init__()
        uic.loadUi('UiFiles/Change_password_window.ui', self)
        self.MainWindow = MainWindow
        self.minimum_pass_len = 4
        self.URLs = URLs

        self.initUI()
        self.show()

    def initUI(self):
        self.button_confirm = self.findChild(QtWidgets.QPushButton, 'button_confirm')
        self.lineEdit_old_pass = self.findChild(QtWidgets.QLineEdit, 'lineEdit_old_pass')
        self.lineEdit_new_pass1 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_new_pass1')
        self.lineEdit_new_pass2 = self.findChild(QtWidgets.QLineEdit, 'lineEdit_new_pass2')

        self.button_confirm.pressed.connect(self.confirm_button_pressed)

    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.MainWindow.setDisabled(False)

    def confirm_button_pressed(self):
        # Check old pass
        if not self.check_old_password():
            self.lineEdit_old_pass.setText("")
            self.lineEdit_new_pass1.setText("")
            self.lineEdit_new_pass2.setText("")
            pop_alert("Błędne hasło")
            return
        # Validate and check new password
        if not self.check_password():
            self.lineEdit_new_pass1.setText("")
            self.lineEdit_new_pass2.setText("")
            pop_alert("Podane hasła się różnią")
            return
        if not validate_password(self.lineEdit_new_pass1.text()):
            self.lineEdit_new_pass1.setText("")
            self.lineEdit_new_pass2.setText("")
            pop_alert(f"Hasło nie spełnia warunków.\nPowinno składać się \nz minimum {self.minimum_pass_len} znaków")
            return

        self.send_request()
        self.close()

    def check_old_password(self):
        # Check if user inserted correct old password
        old_password = self.lineEdit_old_pass.text()
        return True

    def check_password(self):
        # Check if 2 passwords are the same
        if not self.lineEdit_new_pass1.text() == self.lineEdit_new_pass2.text():
            return False

        # Another conditions
        return True

    def send_request(self):
        # Todo: Send request to server
        new_password = self.lineEdit_new_pass2.text()

        url = self.URLs[0] + '/chat/password/change/'
        headers = {'Authorization': 'Token ' + self.MainWindow.token_id}
        r = requests.post(url, headers=headers, data={'new_passw': new_password})

    def pop_alert(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Uwaga!")
        msg.exec_()
