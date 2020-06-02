import requests
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox, QSizePolicy
from random import randint
import time

class FriendsInvitationsWindows(QtWidgets.QMainWindow):
    def __init__(self, MainWindow, URLs):
        super(FriendsInvitationsWindows, self).__init__()
        uic.loadUi('UiFiles/Friends_invitations_window.ui', self)
        self.MainWindow = MainWindow
        self.URLs = URLs
        self.invitations_list = []

        self.initUI()
        self.key_manager = self.MainWindow.key_manager
        self.get_invitations()
        self.show()

    def initUI(self):
        self.listWidget_invitations = self.findChild(QtWidgets.QListWidget, 'listWidget_invitations')


    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.MainWindow.setDisabled(False)

    def add_element(self, text, index):
        def accept_creator():
            self.accept_invitation(index)

        def decline_creator():
            self.decline_invitation(index)

        item_widget = QtWidgets.QListWidgetItem()

        widget_message = QtWidgets.QLabel(text)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Ignore)

        buttonBox.button(QDialogButtonBox.Ok).clicked.connect(accept_creator)
        buttonBox.button(QDialogButtonBox.Ignore).clicked.connect(decline_creator)

        widget = QtWidgets.QWidget()

        widget_layout = QtWidgets.QHBoxLayout()

        widget_layout.addWidget(widget_message)
        widget_layout.addStretch()
        widget_layout.addWidget(buttonBox)

        widget.setLayout(widget_layout)
        item_widget.setSizeHint(widget.sizeHint())

        self.listWidget_invitations.addItem(item_widget)
        self.listWidget_invitations.setItemWidget(item_widget, widget)

    # Only for testing, to delete
    def remove_element(self):
        # Remove current element from list
        row = self.listWidget_invitations.row(self.listWidget_invitations.currentItem())
        self.listWidget_invitations.takeItem(row)
        del self.invitations_list[row]

    def get_invitations(self):
        self.listWidget_invitations.clear()
        self.users = []
        url = self.URLs[0] + '/chat/notifications/'
        headers = {'Authorization': 'Token ' + self.MainWindow.token_id}
        r = requests.get(url, headers=headers)
        respond = r.json()['content']

        self.invitations_list = respond
        self.invitations_list.sort(key=lambda f: f['timestamp'])
        print(self.invitations_list)
        for i in range(len(self.invitations_list)):
            f = self.invitations_list[i]
            self.add_element(f['sender_name'], i)

    def accept_invitation(self, index):
        item = self.invitations_list[index]
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Czy zaakceptować zaprosznie od {item['sender_name']}?")
        msg.setInformativeText(f"Ty i {item['sender_name']} staniecie się znajomymi")
        msg.setWindowTitle("Dodawanie znajomego")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Abort)
        respond = msg.exec_()
        msg.show()

        if respond == 16384:
            self.add_friend(index)

    def decline_invitation(self, index):
        item = self.invitations_list[index]
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Czy odrzucić zaprosznie od {item['sender_name']}?")
        msg.setWindowTitle("Odrzucanie zaproszenia")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Abort)
        respond = msg.exec_()
        msg.show()

        if respond == 16384:
            self.remove_invitation(index)

    def add_friend(self, index):
        

        print(f"Dodaje {index}")
        id = self.invitations_list[index]['id']
        self.MainWindow.send_friend_req_response(id, 'True')
        self.get_invitations()
        self.close()

    def remove_invitation(self, index):
        print(f"Usuwam {index}")
        id = self.invitations_list[index]['id']
        self.MainWindow.send_friend_req_response(id, 'False')
        self.get_invitations()
        self.close()


