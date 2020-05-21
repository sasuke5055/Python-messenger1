from PyQt5 import QtWidgets, uic, QtCore
from GuiClasses.Change_password_window import ChangePasswordWindow
import requests
from threading import Thread
import json
from GuiClasses.messaging import Messenger

# entries = ["Ania", "Asia", "Ala"]
# #TODO kluczami messages powinny być id konwersacji
messages = {}
# "Ala" : ["Ty: Hejka naklejka!"], "Rozmowa prywatna" : [], "druga rozmowa" : []}
username = "Ty"



def split_message(message, count=26):
    """split words to have at maximum 'count' characters """
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

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, token_id, user_id):
        super(MainWindow, self).__init__()
        self.token_id = token_id
        self.user_id = user_id
        self.conversation_ids = dict()
        self.initialised_conversations = []

        self.connect_to_socket()
        self.current_contact = None
        uic.loadUi('UiFiles/Main_window.ui', self)

        self.initUi()

        self.setup_contacts()
        self.show()

    def connect_to_socket(self):
        address = f"ws://127.0.0.1:8000/ws/chat/xd/"
        self.messenger = Messenger()
        self.messenger.subscribe_to_socket(address, self.token_id)
        self.messenger.message_signal.connect(self.refresh_messages)
        self.messenger.add_callback_new_message_received(self.append_new_message)

    def initUi(self):
        self.button_send_message = self.findChild(QtWidgets.QPushButton, 'button_send_message')
        self.button_send_message.clicked.connect(self.send_new_message)
        self.button_send_message.setStyleSheet(
            "QPushButton {"
            "  font-size: 11px;\n"
            "  text-align: center;\n"
            "  text-decoration: none;\n"
            "  outline: none;\n"
            "  color: black;\n"
            "  background-color: #008ae6;\n"
            "  border: none;\n"
            "  border-radius: 15px;\n"
            "  }\n"
            "QPushButton:hover { \n"
            "background-color: #1aa3ff\n"
            "}"
        )
        self.text_new_message = self.findChild(QtWidgets.QTextEdit, 'text_new_message')
        self.centralwidget = self.findChild(QtWidgets.QWidget, 'centralwidget')
        self.list_contacts = self.findChild(QtWidgets.QListWidget, 'list_contacts')
        self.list_contacts.itemClicked.connect(self.show_messages)
        self.list_messages = self.findChild(QtWidgets.QListWidget, 'list_messages')
        self.list_messages.setWordWrap(True)
        self.list_messages.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        # Menu setup
        self.action_change_pass = self.findChild(QtWidgets.QAction, 'action_change_pass')
        self.action_change_pass.triggered.connect(self.open_change_password_window)

    def setup_contacts(self):
        " show all contacs and groups of yours "
        for contact in self.get_contacts():
                new_item = QtWidgets.QListWidgetItem()
                new_item.setText(contact)
                self.list_contacts.addItem(new_item)


    def get_more_messages(self,e=1):
        """ get 'e' more messages from current conversation.   """
        contact = self.current_contact
        starting_pos = len(messages[contact]) or 0
        conversation_id = self.conversation_ids[contact]
        url = 'http://127.0.0.1:8000/chat/messages/'+str(conversation_id)
        print(url)
        headers = {'Authorization': 'Token '+self.token_id}
        r = requests.get(url, headers=headers, data = {'start': starting_pos, 'end': 1})
        d = list()
        temp_messages = list()
        data = r.json()['content']
        print(data)
        if contact not in messages:
            messages[contact] = []
        for message in data:
            content = message['content']
            author_id = message['author']['id']
            if author_id == self.user_id:
                message_prefix = "Ty: "
            else:
                author_name = message['author']['username']
                message_prefix = author_name + ": "

            temp_messages.append(message_prefix + content) 
            d.append((author_id, content))
        """return e more messages between you and given contact"""
        temp_messages.reverse()
        temp_messages.extend(messages[contact])
        """we need to create new cache and replace current one with it """
        messages[contact] = temp_messages
        self.show_messages()
        """ we then refresh the chat and scroll messages to top """
        self.list_messages.scrollToTop()


    def show_messages(self, item = None):
        """show messages between you and given contact named 'item'"""
        self.list_messages.clear()
        button_load_messages = QtWidgets.QPushButton("next")
        item_widget = QtWidgets.QListWidgetItem()
        widget = QtWidgets.QWidget()
        widget_layout =  QtWidgets.QVBoxLayout()
        widget_layout.addWidget(button_load_messages)
        widget_layout.addStretch()
        widget_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        widget.setLayout(widget_layout)
        item_widget.setSizeHint(widget.sizeHint())
        self.list_messages.addItem(item_widget)
        self.list_messages.setItemWidget(item_widget,widget)
        contact = item.text() if item is not None else self.current_contact
        if item is not None:
            messages.pop(self.current_contact,None)
            if self.current_contact in self.initialised_conversations:
                self.initialised_conversations.remove(self.current_contact)
        button_load_messages.clicked.connect(self.get_more_messages)
        self.current_contact = contact
        if contact not in self.initialised_conversations:
            print('CONTACT IS:', contact)
            self.get_messages(contact)
            contact_messages = messages[contact]
            self.initialised_conversations.append(contact)
        contact_messages = messages.get(contact,[])
        print(contact_messages)
        for message_info in contact_messages:
            sender = message_info.split(':')[0]
            message = message_info[len(sender)+2:]
            message = split_message(message,26)
            item_widget = QtWidgets.QListWidgetItem()
            widget_message = QtWidgets.QLabel(message)
            widget_message.setWordWrap(True)
            widget = QtWidgets.QWidget()
            if sender != username:
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

    @QtCore.pyqtSlot()
    def refresh_messages(self):
        print('I NEED TO REFRESH!')
        self.show_messages()

    def send_new_message(self):
        """send new message to contact. Usage: 'Ty: <message>' or '<contact_name>: <message>' for test purposes only"""
        text = self.text_new_message.toPlainText()
        if len(text) != 0:     
            # messages[self.current_contact].append(text)
            self.text_new_message.clear()
            conversation_id = self.conversation_ids[self.current_contact]
            self.messenger.publish_message(text, conversation_id)

    def open_change_password_window(self):
        self.ui = ChangePasswordWindow(self)
        self.setDisabled(True)

    def get_contacts(self):
        url = 'http://127.0.0.1:8000/chat/conversations/'
        headers = {'Authorization': 'Token '+self.token_id}
        r = requests.get(url, headers=headers)
        e = []
        data = r.json()['content']
        for x in data:
            self.conversation_ids[x['title']] = x['id']
            e.append(x['title'])
        print(self.conversation_ids)

        return e
    def get_messages(self, contact, start=0, end=2):
        if start == 0 and end == 2: 
            messages.pop(contact,None)
        conversation_id = self.conversation_ids[contact]
        url = 'http://127.0.0.1:8000/chat/messages/'+str(conversation_id)
        headers = {'Authorization': 'Token '+self.token_id}
        r = requests.get(url, headers=headers, data = {'start': start, 'end': end})
        d = list()
        data = r.json()['content']
        if contact not in messages:
            messages[contact] = []
        for message in data:
            content = message['content']
            author_id = message['author']['id']
            if author_id == self.user_id:
                message_prefix = "Ty: "
            else:
                author_name = message['author']['username']
                message_prefix = author_name + ": "

            messages[contact].append(message_prefix + content) 
            d.append((author_id, content))
        """return all messages between you and given contact"""
        messages[contact].reverse()
    

    def append_new_message(self, message):
        print('appending new message')
        content = message['content']
        author_id = int(message['author']['id'])
        conversation_id = int(message['conversation_id'])
        
        contact = next((title for title, id in self.conversation_ids.items() if id == conversation_id), None)
        if contact not in self.initialised_conversations:
            return
        print('OOOOOOOOOO', contact)
        print(self.conversation_ids.items())

        if author_id == self.user_id:
            message_prefix = "Ty: "
        else:
            author_name = message['author']['username']
            message_prefix = author_name + ": "

        print(message_prefix)

        messages[contact].append(message_prefix + content)

        
        





    
