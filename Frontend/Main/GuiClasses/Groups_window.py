import requests
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox, QSizePolicy
from random import randint

class GroupsWindow(QtWidgets.QMainWindow):
    def __init__(self, MainWindow, URLs):
        super(GroupsWindow, self).__init__()
        uic.loadUi('UiFiles/Conversations_window.ui', self)
        self.MainWindow = MainWindow
        self.URLs = URLs
        self.invitations_list = []
        self.user_id = self.MainWindow.user_id
        self.initUI()
        self.key_manager = self.MainWindow.key_manager
        self.get_friends()
        self.listView_friends.setModel(self.model)
        self.show()

    def initUI(self):
        self.listView_friends = self.findChild(QtWidgets.QListView, 'listView_friends')
        self.lineEdit_name    = self.findChild(QtWidgets.QLineEdit, 'lineEdit_name')
        self.buttonBox        = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        self.model = QtGui.QStandardItemModel(self.listView_friends)
        self.buttonBox.accepted.connect(self.get_checked_friends)
        self.buttonBox.rejected.connect(self.close)
    def closeEvent(self, event):
        # Unlock login window when closing this window
        self.MainWindow.setDisabled(False)

    def add_element(self, text):
        item = QtGui.QStandardItem(text)
        item.setCheckable(True)
        self.model.appendRow(item)


    def get_checked_friends(self):
        conversation_name = self.lineEdit_name.text()
        checked_ids = []
        for i in range(len(self.friends_list)):
            if self.model.item(i).checkState():
                checked_ids.append(self.friends_list[i]['id'])
        self.MainWindow.messenger.create_group(conversation_name, self.user_id, checked_ids)
        self.close()

    def get_friends(self):
        self.friends_list = []
        url = self.URLs[0] + '/chat/contacts/'
        headers = {'Authorization': 'Token ' + self.MainWindow.token_id}
        r = requests.get(url, headers=headers)
        respond = r.json()['content']
        self.friends_list = respond['friends']
        self.friends_list.sort(key=lambda f: f['username'])

        for f in self.friends_list:
            usr = f['username']
            self.add_element(f['username'])

