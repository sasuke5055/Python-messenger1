import requests
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from SidePackage.Error import pop_alert


class FriendsSearchWindow(QtWidgets.QMainWindow):
    def __init__(self, MainWindow, URLs):
        super(FriendsSearchWindow, self).__init__()
        uic.loadUi('UiFiles/Friends_search_window.ui', self)
        self.MainWindow = MainWindow
        self.URLs = URLs
        self.users = []
        self.friends_list = []

        self.initUI()
        self.show()

    def initUI(self):
        self.listWidget_users = self.findChild(QtWidgets.QListWidget, 'listWidget_users')
        self.button_search = self.findChild(QtWidgets.QPushButton, 'button_search')
        self.lineEdit_to_search = self.findChild(QtWidgets.QLineEdit, 'lineEdit_to_search')

        self.button_search.pressed.connect(self.search_friends)
        self.listWidget_users.itemClicked.connect(self.user_clicked)
        self.listWidget_users.itemDoubleClicked.connect(self.user_double_clicked)

    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.MainWindow.setDisabled(False)

    def add_element(self, text):
        self.listWidget_users.addItem(text)

    def search_friends(self):
        self.users = []
        self.listWidget_users.clear()
        string = self.lineEdit_to_search.text()
        url = self.URLs[0] + '/chat/search/'
        headers = {'Authorization': 'Token ' + self.MainWindow.token_id}
        r = requests.get(url, headers=headers, data={'key': string})
        respond = r.json()['content']
        self.users = respond

        # Get your frieds list
        self.friends_list = []
        url = self.URLs[0] + '/chat/contacts/'
        headers = {'Authorization': 'Token ' + self.MainWindow.token_id}
        r = requests.get(url, headers=headers)
        respond1 = r.json()['content']
        self.friends_list = respond1['friends']

        self.users = [x for x in self.users if x['id'] not in list(map(lambda x: x['id'], self.friends_list))]

        for f in self.users:
            self.add_element(f['username'])

    def user_clicked(self, item):
        pass

    def user_double_clicked(self, item):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"Czy chcesz dodać {item.text()} do swoich znajomych?")
        msg.setInformativeText(f"Spowoduje to wysłanie zaproszenia do użytkownika {item.text()}")
        msg.setWindowTitle("Dodawanie znajomego")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Abort)
        respond = msg.exec_()
        msg.show()
        if respond == 16384:
            self.add_friend(item)

    def add_friend(self, item):
        row = self.listWidget_users.row(self.listWidget_users.currentItem())
        id = self.users[row]['id']
        self.MainWindow.send_friend_request(id)

