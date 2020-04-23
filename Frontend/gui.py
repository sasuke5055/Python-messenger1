# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QBrush, QColor, QFont

entries = ["Ania", "Asia", "Ala"]
messages = {"Ania": ["Ty: Hejka  ", "Ty: Cześć", "Ania: Co tam?", "Ty: HIPOPOTAM XDXDXD", "Ty: Jestem super"], "Asia" : ["Asia: hallooo", "Ty: eloo"], 
"Ala" : ["Ty: Hejka naklejka!"]}

def get_contacts():
    return entries

def get_messages(contact):
    return messages[contact]

def split_message(message, count):
    return_message = ''
    words = message.split(' ')
    for w in words:
        if len(w) <= count:
            return_message = return_message + w + ' '
        else:
            while len(w) > count: 
                return_message = return_message + w[0:count]+' '
                w = w[count:] 
            return_message = return_message + w
    return return_message

class Ui_MainWindow(object):

    def show_messages(self, item = None):
    
        self.list_messages.clear()
        contact = item.text() if item is not None else self.current_contact
        self.current_contact = contact
        contact_messages = get_messages(contact)
        for message_info in contact_messages:
            sender = message_info.split(':')[0]
            message = message_info[len(sender)+2:]
            message = split_message(message,26)
            item_widget = QtWidgets.QListWidgetItem()
            widget_message = QtWidgets.QLabel(message)
            widget_message.setWordWrap(True)
            widget = QtWidgets.QWidget()
            if sender != "Ty":
                widget_message.setStyleSheet(
                 "max-width: 225px;\n"
                 "border-radius: 10px;\n"
                 "background: #ffcccc;\n"
                 "border: 5px solid #ffcccc;\n"
                 "font-size: 11px;"
                )
                sender_label = QtWidgets.QLabel(sender)
                widget_layout =  QtWidgets.QVBoxLayout()
                widget_layout.addWidget(sender_label)
                widget_layout.addWidget(widget_message)
                widget_layout.addStretch()
                widget_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                widget.setLayout(widget_layout)
                item_widget.setSizeHint(widget.sizeHint())
                self.list_messages.addItem(item_widget)
                self.list_messages.setItemWidget(item_widget,widget)
            else:
                widget_message.setStyleSheet(
                 "border-radius: 10px;\n"
                 "background: lightgray;\n"
                 "border: 5px solid lightgray;\n"
                 "margin-left: 200px;"
                 "font-size: 11px;"
                )
                widget_layout =  QtWidgets.QHBoxLayout()
                widget_layout.addWidget(widget_message) 
                widget_layout.addStretch()
                widget_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                widget.setLayout(widget_layout)
                item_widget.setSizeHint(widget.sizeHint())
                self.list_messages.addItem(item_widget)
                self.list_messages.setItemWidget(item_widget,widget)
            self.list_messages.scrollToBottom()

    def send_new_message(self):
        text = self.text_new_message.toPlainText()
        text = text
        if len(text) != 0:     
            messages[self.current_contact].append(text)
            self.show_messages()
            self.text_new_message.clear()



    def setupUi(self, MainWindow):
        self.current_contact = None 

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(651, 606)
        MainWindow.setStyleSheet("QPushButton {"
        "  font-size: 11px;\n"
        "  text-align: center;\n"
        "  text-decoration: none;\n"
        "  outline: none;\n"
        "  color: #fff;\n"
        "  background-color: #4CAF50;\n"
        "  border: none;\n"
        "  border-radius: 15px;\n"
        "  }\n"
        "QPushButton:hover { \n"
        "background-color: #3e8e41\n"
        "}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.list_contacts = QtWidgets.QListWidget(self.centralwidget)
        self.list_contacts.setGeometry(QtCore.QRect(10, 10, 141, 501))
        self.list_contacts.setObjectName("list_contacts")
        for contact in get_contacts():
            new_item = QtWidgets.QListWidgetItem()
            new_item.setText(contact)
            self.list_contacts.addItem(new_item)
        self.list_contacts.itemClicked.connect(self.show_messages)

        self.list_messages = QtWidgets.QListWidget(self.centralwidget)
        self.list_messages.setGeometry(QtCore.QRect(170, 10, 451, 341))
        self.list_messages.setObjectName("list_messages")
        self.list_messages.setWordWrap(True)
        self.list_messages.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list_messages.setStyleSheet("QlistWidget{ \n"
        "border: none;\n"
        "}\n"
 
        )
        self.text_new_message = QtWidgets.QTextEdit(self.centralwidget)
        self.text_new_message.setGeometry(QtCore.QRect(170, 370, 451, 141))
        self.text_new_message.setObjectName("text_new_message")
        self.button_send_message = QtWidgets.QPushButton(self.centralwidget)
        self.button_send_message.setGeometry(QtCore.QRect(490, 520, 131, 31))
        self.button_send_message.setObjectName("button_send_message")
        self.button_send_message.clicked.connect(self.send_new_message)
        self.button_send_message.setAutoDefault(True)
        self.button_send_message.setStyleSheet
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 651, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_send_message.setText(_translate("MainWindow", "Wyślij wiadomość"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
