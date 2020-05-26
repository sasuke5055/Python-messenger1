from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from random import randint


class FriendsInvitationsWindows(QtWidgets.QMainWindow):
    def __init__(self, MainWindow, URLs):
        super(FriendsInvitationsWindows, self).__init__()
        uic.loadUi('UiFiles/Friends_invitations_window.ui', self)
        self.MainWindow = MainWindow
        self.URLs = URLs
        self.invitations_list = []

        self.initUI()
        self.get_invitations()
        self.show()

    def initUI(self):
        self.listWidget_invitations = self.findChild(QtWidgets.QListWidget, 'listWidget_invitations')

    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.MainWindow.setDisabled(False)

    def add_element(self, text):
        self.listWidget_invitations.addItem(text)

    def remove_element(self):
        # Remove current element from list
        row = self.listWidget_invitations.row(self.listWidget_invitations.currentItem())
        self.listWidget_invitations.takeItem(row)
        del self.invitations_list[row]

    def get_invitations(self):
        # todo: send request to server to get invitations (index + (string) name)
        self.invitations_list = []
        self.invitations_list.sort(key=lambda f: f[1])
        for f in self.invitations_list:
            self.add_element(f[1])

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
        row = self.listWidget_invitations.row(self.listWidget_invitations.currentItem())
        id = self.invitations_list[row][1]

        # request to server (id)
        respond = True
        if respond:
            self.remove_element()

