from PyQt5 import QtWidgets, uic
from SidePackage.Validation import validate_email
from SidePackage.Error import pop_alert

class ForgotWindow(QtWidgets.QMainWindow):
    def __init__(self, LoginWindow):
        super(ForgotWindow, self).__init__()
        uic.loadUi('UiFiles/Forgot_password_window.ui', self)
        self.LoginWindow = LoginWindow
        self.initUI()
        self.show()

    def initUI(self):
        self.button_send_request = self.findChild(QtWidgets.QPushButton, 'button_send_request')
        self.lineEdit_email = self.findChild(QtWidgets.QLineEdit, 'lineEdit_email')
        self.button_send_request.pressed.connect(self.send_button_pressed)

    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.LoginWindow.setDisabled(False)

    def send_button_pressed(self):
        if not validate_email(self.lineEdit_email.text()):
            pop_alert("Podaj poprawnego maila!")
            return
        self.send_request()
        self.close()

    def send_request(self):
        # Todo: Send request to server
        # try for server present
        try:

            email = self.lineEdit_email.text()
        except:
            pop_alert("Błąd sieci, sprawdź połączenie.")
