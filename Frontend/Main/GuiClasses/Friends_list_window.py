import requests
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from random import randint


class FriendsListWindow(QtWidgets.QMainWindow):
    def __init__(self, MainWindow, URLs):
        super(FriendsListWindow, self).__init__()
        uic.loadUi('UiFiles/Friends_list_window.ui', self)
        self.MainWindow = MainWindow
        self.URLs = URLs
        self.friends_list = []

        self.initUI()
        self.get_friends()
        self.show()

    def initUI(self):
        self.listWidget_friends = self.findChild(QtWidgets.QListWidget, 'listWidget_friends')
        self.listWidget_friends.itemClicked.connect(self.friend_clicked)
        self.listWidget_friends.itemDoubleClicked.connect(self.friend_double_clicked)

    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.MainWindow.setDisabled(False)

    def add_element(self, text):
        self.listWidget_friends.addItem(text)

    def remove_element(self):
        # Remove current element from list
        row = self.listWidget_friends.row(self.listWidget_friends.currentItem())
        self.listWidget_friends.takeItem(row)
        del self.friends_list[row]

    def get_friends(self):
        self.friends_list = []
        self.listWidget_friends.clear()
        url = self.URLs[0] + '/chat/contacts/'
        headers = {'Authorization': 'Token ' + self.MainWindow.token_id}
        r = requests.get(url, headers=headers)
        respond = r.json()['content']
        self.friends_list = respond['friends']
        self.friends_list.sort(key=lambda f: f['username'])

        print(self.friends_list)
        for f in self.friends_list:
            self.add_element(f['username'])
            print(f)

    def friend_clicked(self, item):
        # todo: ?????????????????????
        pass

    def friend_double_clicked(self, item):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Czy chcesz usunąć {item.text()} ze swoich znajomych?")
        msg.setInformativeText(f"Spowoduje to usunięcie ciebie ze znajomych użytkownika {item.text()}")
        msg.setWindowTitle("Usuwanie znajomego")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Abort)
        respond = msg.exec_()
        msg.show()

        if respond == 16384:
            self.remove_friend(item)

    def remove_friend(self, item):
        print(f"Usuwam {item.text()}")
        row = self.listWidget_friends.row(self.listWidget_friends.currentItem())
        username = self.friends_list[row]['username']

        url = self.URLs[0] + '/chat/friends/remove/'
        headers = {'Authorization': 'Token ' + self.MainWindow.token_id}
        r = requests.post(url, headers=headers, data={'username': username})

        if r:
            self.get_friends()

