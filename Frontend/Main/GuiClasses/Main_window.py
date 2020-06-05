from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QFont
from SidePackage.Error import pop_alert
import time
from .Change_password_window import ChangePasswordWindow
from .Friends_list_window import FriendsListWindow
from .Friends_search_window import FriendsSearchWindow
from .Friends_invitations_window import FriendsInvitationsWindows
from .Groups_window import GroupsWindow

import requests
from .messaging import Messenger
from .Managers.KeyManager import KeyManager

# TODO kluczami messages powinny być id konwersacji
messages = {}
username = "Ty"
flag = 17843 

def split_message(message, count=26):
    """split words to have at maximum 'count' characters """
    return_message = ''
    words = message.split(' ')
    for w in words:
        if len(w) <= count:
            return_message = return_message + w + ' '
        else:
            while len(w) > count:
                return_message = return_message + w[0:count] + ' '
                w = w[count:]
            return_message = return_message + w
    return return_message


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, token_id, user_id, URLs):
        super(MainWindow, self).__init__()
        self.token_id = token_id
        self.user_id = user_id
        self.URLs = URLs
        self.conversation_ids = dict()
        #TODO: WYWALIĆ INITIALISED
        self.initialised_conversations = []

        self.connect_to_socket()
        self.current_contact = None
        uic.loadUi('UiFiles/Main_window.ui', self)

        self.initUi()

        self.key_manager = KeyManager(user_id)

        self.setup_contacts()
        self.show()

    


    def connect_to_socket(self):
        address = self.URLs[1] + "/ws/chat/xd/"
        self.messenger = Messenger()
        self.messenger.subscribe_to_socket(address, self.token_id)
        self.messenger.message_signal.connect(self.refresh_messages)
        self.messenger.key_received_signal.connect(self.on_key_receive)
        self.messenger.message_signal.connect(self.f_req_response)
        self.messenger.add_callback_new_message_received(self.append_new_message)
        self.messenger.add_callback_new_key_request(self.handle_key_request)
        self.messenger.add_callback_new_key_response(self.handle_key_response)
        self.messenger.add_callback_new_friend_request(self.handle_friend_request)
        self.messenger.add_callback_friend_req_response(self.friend_req_repsponse)
        self.messenger.add_callback_conversation_created(self.new_conversation_created)
        self.messenger.add_callback_new_group_created(self.handle_responses)
        
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
        # Profile menu
        self.action_change_pass = self.findChild(QtWidgets.QAction, 'action_change_pass')
        self.action_change_pass.triggered.connect(self.open_change_password_window)

        # Friends menu
        self.action_friens_list = self.findChild(QtWidgets.QAction, 'action_friens_list')
        self.action_find_friends = self.findChild(QtWidgets.QAction, 'action_find_friends')
        self.action_invitations_list = self.findChild(QtWidgets.QAction, 'action_invitations_list')
        self.action_new_conversation = self.findChild(QtWidgets.QAction, 'action_nowa_konwersacja')
        self.action_friens_list.triggered.connect(self.open_friends_list_window)
        self.action_find_friends.triggered.connect(self.open_friends_search_window)
        self.action_invitations_list.triggered.connect(self.open_fiends_invitations_windows)
        self.action_new_conversation.triggered.connect(self.open_groups_windows)
    def setup_contacts(self):
        " show all contacs and groups of yours "
        self.list_contacts.clear()
        for contact in self.get_contacts():
            new_item = QtWidgets.QListWidgetItem()
            new_item.setText(contact)
            self.list_contacts.addItem(new_item)

    def set_contact_bold(self, id, bool):
        # Todo:
        pass

    def show_messages(self, item=None):
        """make sending message possible"""
        self.list_messages.clear()
        self.button_send_message.setEnabled(True)
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

        """show messages between you and given contact named 'item'"""
        contact = item.text() if item is not None else self.current_contact
        if item is not None:
            messages.pop(self.current_contact,None)
            if self.current_contact in self.initialised_conversations:
                self.initialised_conversations.remove(self.current_contact)
        button_load_messages.clicked.connect(self.get_more_messages)

        self.current_contact = contact

        conversation_id = self.conversation_ids[contact]
        print(conversation_id)
        self.request_key(conversation_id)
        print(self.key_manager.contains_conversation(conversation_id))
        if not self.key_manager.contains_conversation(conversation_id):  # send a request for the RSA key
            self.request_key(conversation_id)
            pop_alert("Poczekaj na wygenerowanie")
            return
            # TODO we must wait for the key from conversation admin, leave this function/tell user about it

        if contact not in self.initialised_conversations:
            print('CONTACT IS:', contact)
            self.get_messages(contact)
            contact_messages = messages[contact]
            self.initialised_conversations.append(contact)
        contact_messages = messages.get(contact, [])
        for message_info in contact_messages:
            sender = message_info.split(':')[0]
            message = message_info[len(sender) + 2:]
            message = split_message(message, 26)
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
                widget_layout = QtWidgets.QVBoxLayout()
                widget_layout.addWidget(sender_label)
                widget_layout.addWidget(widget_message)
                widget_layout.addStretch()
                widget_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                widget.setLayout(widget_layout)
                item_widget.setSizeHint(widget.sizeHint())
                self.list_messages.addItem(item_widget)
                self.list_messages.setItemWidget(item_widget, widget)
            else:
                widget_message.setStyleSheet(
                    "border-radius: 10px;\n"
                    "background: lightgray;\n"
                    "border: 5px solid lightgray;\n"
                    "margin-left: 200px;"
                    "font-size: 11px;"
                )
                widget_layout = QtWidgets.QHBoxLayout()
                widget_layout.addWidget(widget_message)
                widget_layout.addStretch()
                widget_layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
                widget.setLayout(widget_layout)
                item_widget.setSizeHint(widget.sizeHint())
                self.list_messages.addItem(item_widget)
                self.list_messages.setItemWidget(item_widget, widget)
            self.list_messages.scrollToBottom()

    @QtCore.pyqtSlot()
    def refresh_messages(self):
        print('I NEED TO REFRESH!')
        self.show_messages()

    @QtCore.pyqtSlot()
    def on_key_receive(self):
        # TODO this is invoked when we receive a new key
        pass

    @QtCore.pyqtSlot()
    def f_req_response(self):

        pass

    def handle_key_request(self, data):  # current user is an admin, and we should send the key
        global flag
        # TODO notify user about it and let him decide
        print('NEW KEY REQUEST!')
        print()
        # request data
        conversation_id = data['conversation_id']
        dh_external_key = int(data['dh_key'])
        user_id = data['user_id']

        dh_local = self.key_manager.initialise_dh(conversation_id)  # initialise diffie hellman
        dh_local_key = dh_local.gen_public_key()  # we send this key with our message
        dh_local.gen_private_key(dh_external_key)  # dh_local can now encrypt our rsa key

        rsa_key = self.key_manager.get_key(conversation_id)
        if rsa_key == None and conversation_id not in self.key_manager.currently_generating_keys:  # serious error, rsa keys should be added just after creating the new conversation
            # raise Exception("Admin doesn't have key!")
            # TODO delete code below
            self.key_manager.start_generating_key(conversation_id)
            new_key = self.key_manager.generate_key()
            self.key_manager.add_key(conversation_id, new_key)
            rsa_key = self.key_manager.get_key(conversation_id)
            self.setup_contacts()

        encrypted_rsa_key = dh_local.encrypt_key(rsa_key['rsa_key'])  # this is a dictionary    
        encrypted_flag    = dh_local.encrypt_message(flag)
        self.messenger.send_key_response(conversation_id, user_id, dh_local_key, encrypted_rsa_key, encrypted_flag)

    def handle_key_response(self, data):
        global flag
        print('NEW KEY RESPONSE!')
        print()
        conversation_id = data['conversation_id']
        if not self.key_manager.contains_conversation(conversation_id):
            dh_key = int(data['dh_key'])
            encrypted_rsa_key = data['rsa_key']

            dh = self.key_manager.get_dh(conversation_id)
            dh.gen_private_key(dh_key)  # now dh can decrypt RSA key

            encrypted_flag = int(data['flag'])
            decrypted_flag = dh.decrypt_message(encrypted_flag)
            if flag == decrypted_flag:
                decrypted_rsa_key = dh.decrypt_key(encrypted_rsa_key)  # this is rsa.PrivateKey object
                self.key_manager.add_key(conversation_id, decrypted_rsa_key)            
                self.setup_contacts()
            else:
                print('INCORRECT DIFFIE HELLMAN ENCODING')

    def request_key(self, conversation_id):
        print('IM REQUESTING A KEY')
        dh = self.key_manager.initialise_dh(conversation_id)
        dh_key = dh.gen_public_key()
        self.messenger.send_key_request(conversation_id, dh_key)

    def send_new_message(self):
        """send new message to contact. Usage: 'Ty: <message>' or '<contact_name>: <message>' for test purposes only"""
        text = self.text_new_message.toPlainText()
        if len(text) != 0:
            self.text_new_message.clear()
            conversation_id = self.conversation_ids[self.current_contact]

            rsa_manager = self.key_manager.get_rsa_manager(conversation_id)
            if rsa_manager != None:
                text = rsa_manager.encrypt(text)
                self.messenger.publish_message(text, conversation_id)

    def get_contacts(self):
        self.conversation_ids.clear()
        url = self.URLs[0] + '/chat/conversations/'
        headers = {'Authorization': 'Token ' + self.token_id}
        r = requests.get(url, headers=headers)
        e = []
        data = r.json()['content']
        for x in data:
            self.conversation_ids[x['title']] = x['id']
            e.append(x['title'])
        print(self.conversation_ids)

        return e

    def get_messages(self, contact,start=0,end=2):
        if start == 0 and end == 2: 
            messages.pop(contact,None)

        conversation_id = self.conversation_ids[contact]
        rsa_manager = self.key_manager.get_rsa_manager(conversation_id)
        if rsa_manager is None:
            print("RSA NONE!"*100)

        url = self.URLs[0] + '/chat/messages/' + str(conversation_id)
        headers = {'Authorization': 'Token ' + self.token_id}
        r = requests.get(url, headers=headers, data={'start':start, 'end':end})
        d = list()
        data = r.json()['content']
        if contact not in messages:
            messages[contact] = []
        for message in data:
            content = str(message['content'])

            print('XDDD')
            print(type(content))
            if rsa_manager != None:
                content = rsa_manager.decrypt(content)
            print(type(content))

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
        return messages[contact]

    def get_more_messages(self,e=1):
        """ get 'e' more messages from current conversation.   """
        contact = self.current_contact
        
        print("XDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        starting_pos = len(messages[contact]) or 0
        conversation_id = self.conversation_ids[contact]
        url = self.URLs[0]+'/chat/messages/'+str(conversation_id)
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
            content = self.decode_message(message,conversation_id)
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
        
    def decode_message(self,message,conversation_id):
        content = message['content']
        print(message)

        rsa_manager = self.key_manager.get_rsa_manager(conversation_id)
        if rsa_manager != None:
            content = rsa_manager.decrypt(content)
        return content

    def append_new_message(self, message):
        author_id = int(message['author']['id'])
        conversation_id = int(message['conversation_id'])
        content = self.decode_message(message,conversation_id)

        contact = next((title for title, id in self.conversation_ids.items() if id == conversation_id), None)
        if contact not in self.initialised_conversations:
            return

        if author_id == self.user_id:
            message_prefix = "Ty: "
        else:
            author_name = message['author']['username']
            message_prefix = author_name + ": "

        messages[contact].append(message_prefix + content)

    def open_change_password_window(self):
        self.ui = ChangePasswordWindow(self, self.URLs)
        self.setDisabled(True)

    def open_friends_list_window(self):
        self.ui = FriendsListWindow(self, self.URLs)
        self.setDisabled(True)

    def open_friends_search_window(self):
        self.ui = FriendsSearchWindow(self, self.URLs)
        self.setDisabled(True)

    def open_fiends_invitations_windows(self):
        self.ui = FriendsInvitationsWindows(self, self.URLs)
        self.setDisabled(True)

    def open_groups_windows(self):
        self.ui = GroupsWindow(self,self.URLs)
        self.setDisabled(True)
        

    # Todo: Przyszło zaproszenie
    def handle_friend_request(self, data):
        print(data)
        request_id = int(data['request_id'])
        sender_name = data['sender']
        timestamp = data['timestamp']
        pop_alert("Nowe Zaproszenie!")

        # TODO akceptacja/odrzucenie requesta na https
        # TODO możee po prostu robić powiadomienie i weźmiesz sobie ostatniego requesta z bazy

    def send_friend_request(self, id):
        self.messenger.send_friend_request(id)


    def handle_responses(self, data):
        print("XD"*100)
        admin_name = data['admin']
        title = data['title']
        pop_alert(f"{admin_name} Cię dodał do grupy {title}!")
        self.setup_contacts()
        

    def friend_req_repsponse(self, data):
        friend_name = data['sender']
        if data['response'] == 'True':
            pop_alert(f"{friend_name} Cię dodał do znajomych!")
            self.setup_contacts()


        else:
            pop_alert(f"{friend_name} Cię odrzucił")
        

    def send_friend_req_response(self, req_id, response):
        self.messenger.send_f_req_response(req_id, response)

    
    def new_conversation_created(self, data):
        conversation_id = data['conversation_id']
        print(f"ADMIN GENERUJE KLUCZ DO {conversation_id}")
        self.key_manager.start_generating_key(conversation_id)
        new_key = self.key_manager.generate_key()
        self.key_manager.add_key(conversation_id, new_key)

        self.setup_contacts()
