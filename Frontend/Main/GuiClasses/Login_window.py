from PyQt5 import QtWidgets, uic
import json


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        uic.loadUi('UiFiles/Login_window.ui', self)

        self.button_login = self.findChild(QtWidgets.QPushButton, 'button_login')
        self.lineEdit_username = self.findChild(QtWidgets.QLineEdit, 'lineEdit_username')
        self.lineEdit_password = self.findChild(QtWidgets.QLineEdit, 'lineEdit_password')
        self.checkBox_remember = self.findChild(QtWidgets.QCheckBox, 'checkBox_remember')

        self.button_login.pressed.connect(self.login_button_pressed)
        self.load_users_credentials()

        self.show()

    def login_button_pressed(self):
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()

        # Validate input data
        if not self.validate_data(username, password):
            self.lineEdit_username.setPlaceholderText("Podaj najpierw login i hasło!")
            return

        # remember user login data
        if self.checkBox_remember.isChecked():
            self.save_users_credentials(username, password)
        else:
            self.delete_users_credentials()

        # login using username and password
        print(f"Login user {username} with password {password}")
        print("Open new stage and than close this")
        self.open_main_window()
        self.close()

    def save_users_credentials(self, username, password):
        # Saves users credentials into json file
        with open("cred.entials", "w") as f:
            json.dump((username, password), f)
            f.close()

    def load_users_credentials(self):
        # Loads saved users credentials from file into lineEdits
        try:
            # Open file if exists
            with open("cred.entials", "r") as f:
                credentials = json.load(f)
                self.lineEdit_username.setText(credentials[0])
                self.lineEdit_password.setText(credentials[1])

                # If there was saved any data set checkBox saved
                if credentials[0] != "":
                    self.checkBox_remember.setChecked(True)
                f.close()

        # There is no such file
        except FileNotFoundError:
            pass
        # This File is empty
        except json.decoder.JSONDecodeError:
            pass

    def delete_users_credentials(self):
        # Empty the file with credentials
        open("cred.entials", "w").close()

    def open_main_window(self):
        # Open main window after login in
        # todo: Open main window
        print("There will open main window")

    def validate_data(self, login, password):
        # Checks if login/password is not empty
        if login and password:
            return True
        else:
            return False
