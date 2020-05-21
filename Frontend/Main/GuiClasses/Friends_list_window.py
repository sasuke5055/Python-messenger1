from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from SidePackage.Error import pop_alert
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
        self.add = self.findChild(QtWidgets.QPushButton, 'add')
        self.remove = self.findChild(QtWidgets.QPushButton, 'rem')

        self.add.pressed.connect(self.add_element_test)
        self.remove.pressed.connect(self.remove_element)
        self.listWidget_friends.itemClicked.connect(self.friend_clicked)
        self.listWidget_friends.itemDoubleClicked.connect(self.friend_double_clicked)

    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.MainWindow.setDisabled(False)

    def add_element_test(self):
        string = "ebebebbe " + str(randint(1, 1000))
        self.listWidget_friends.addItem(string)
        self.friends_list.append((string, len(self.friends_list)))

    def add_element(self, text):
        self.listWidget_friends.addItem(text)

    def remove_element(self):
        # Remove current element from list
        row = self.listWidget_friends.row(self.listWidget_friends.currentItem())
        self.listWidget_friends.takeItem(row)
        del self.friends_list[row]

    def get_friends(self):
        # todo: send request to server to get friends list (index + (string) name)
        self.friends_list = []
        self.friends_list.sort(key=lambda f: f[1])
        for f in self.friends_list:
            self.add_element(f[1])

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
        # todo: Send request to server to delete user, where id == id
        row = self.listWidget_friends.row(self.listWidget_friends.currentItem())
        id = self.friends_list[row][1]

        # request to server (id)
        respond = True
        if respond:
            self.remove_element()

