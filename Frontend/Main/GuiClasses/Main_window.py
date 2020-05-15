from PyQt5 import QtWidgets, uic, QtWebSockets
from .Change_password_window import ChangePasswordWindow
import requests
import json
from channels.generic.websocket import WebsocketConsumer
import websocket
import ssl
import time
from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtCore import QUrl, QCoreApplication, QTimer
from PyQt5.QtWidgets import QApplication

entries = ["Ania", "Asia", "Ala"]
messages = {"test": ["Ty: Mój stary to fanatyk wędkarstwa. Pół mieszkania zajebane wędkami najgorsze. Średnio raz w miesiącu ktoś wdepnie w leżący na ziemi haczyk czy kotwicę i trzeba wyciągać w szpitalu bo mają zadziory na końcu. W swoim 22 letnim życiu już z 10 razy byłem na takim zabiegu. Tydzień temu poszedłem na jakieś losowe badania to baba z recepcji jak mnie tylko zobaczyła to kazała buta ściągać xD bo myślała, że znowu hak w nodze. Druga połowa mieszkania zajebana Wędkarzem Polskim, Światem Wędkarza, Super Karpiem xD itp. Co tydzień ojciec robi objazd po wszystkich kioskach w mieście, żeby skompletować wszystkie wędkarskie tygodniki. Byłem na tyle głupi, że nauczyłem go into internety bo myślałem, że trochę pieniędzy zaoszczędzimy na tych gazetkach ale teraz nie dosyć, że je kupuje to jeszcze siedzi na jakichś forach dla wędkarzy i kręci gównoburze z innymi wędkarzami o najlepsze zanęty itp. Potrafi drzeć mordę do monitora albo wypierdolić klawiaturę za okno. Kiedyś ojciec mnie wkurwił to założyłem tam konto i go trolowałem pisząc w jego tematach jakieś losowe głupoty typu karasie jedzo guwno. Matka nie nadążała z gotowaniem bigosu na uspokojenie. Aha, ma już na forum rangę SUM, za najebanie 10k postów.Jak jest ciepło to co weekend zapierdala na ryby. Od jakichś 5 lat w każdą niedzielę jem rybę na obiad a ojciec pierdoli o zaletach jedzenia tego wodnego gówna. Jak się dostałem na studia to stary przez tydzień pie**olił że to dzięki temu, że jem dużo ryb bo zawierają fosfor i mózg mi lepiej pracuje.Co sobotę budzi ze swoim znajomym mirkiem całą rodzinę o 4 w nocy bo hałasują pakując wędki, robiąc kanapki itd.Przy jedzeniu zawsze pierdoli o rybach i za każdym razem temat schodzi w końcu na Polski Związek Wędkarski, ojciec sam się nakręca i dostaje strasznego bólu dupy durr niedostatecznie zarybiajo tylko kradno hurr, robi się przy tym cały czerwony i odchodzi od stołu klnąc i idzie czytać Wielką Encyklopedię Ryb Rzecznych żeby się uspokoić.W tym roku sam sobie kupił na święta ponton. Oczywiście do wigilii nie wytrzymał tylko już wczoraj go rozpakował i nadmuchał w dużym pokoju. Ubrał się w ten swój cały strój wędkarski i siedział cały dzień w tym pontonie na środku mieszkania. Obiad (karp) też w nim zjadł [cool][cześć]  ", "Ty: Cześć", "Ania: Co tam?", "Ty: HIPOPOTAM XDXDXD", "Ty: Jestem super"], "Asia" : ["Asia: hallooo", "Ty: eloo"], 
"Ala" : ["Ty: Hejka naklejka!"], "Rozmowa prywatna" : [], "druga rozmowa" : []}
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
        print(token_id)
        self.user_id = user_id
        self.conversation_ids = dict()
        print(token_id)
        self.current_contact = None
        uic.loadUi('UiFiles/Main_window.ui', self)
        self.conversation_list = []
        self.initUi()

        self.setup_contacts()
        self.show()

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
                
    def show_messages(self, item = None):
        """show messages between you and given contact named 'item'"""
        
        self.list_messages.clear()
        contact = item.text() if item is not None else self.current_contact
        self.current_contact = contact
        contact_messages = self.get_messages()
        print("AAAAA")
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

    def send_new_message(self):
        """send new message to contact. Usage: 'Ty: <message>' or '<contact_name>: <message>' for test purposes only"""
        text = self.text_new_message.toPlainText()
        if len(text) != 0:     
            messages[self.current_contact].append(text)
            self.show_messages()
            self.text_new_message.clear()

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
            self.conversation_list.append(x)
            # self.conversation_ids[x['title']] = x['id']
            e.append(x['title'])
        print(self.conversation_ids)
        return e

    def get_messages(self):
        contact = self.conversation_list[self.list_contacts.currentRow()]
        print(contact['id'])
        # websocket = websockets.WebSocketClientProtocol
        # with websockets.connect(f"ws://localhost:8000/chat/{contact['title']}") as websocket:
        #     websocket.send(json.dumps({
        #             'type': 'join_conversation',
        #             'conversation_id': f"{contact['id']}"
        #     }))
        # ws = websocket.create_connection(f"ws://localhost:8000/ws/chat/{contact['title']}/",
        #                       on_message = on_message,
        #                       on_error = on_error,
        #                       on_close = on_close)
        # time.sleep(5)
        # on_open(ws, contact)
        # app = QApplication(sys.argv)
        self.client = Client(contact)
        url = f"http://127.0.0.1:8000/chat/messages/{contact['id']}/"
        headers = {'Authorization': 'Token '+self.token_id}
        r = requests.get(url, headers=headers)
        d = list()
        data = r.json()['content']
        messages[contact['id']] = []
        for message in data:
            content = message['content']
            author_id = message['author']['id']
            if author_id == self.user_id:
                message_prefix = "Ty: "
            else:
                author_name = message['author']['username']
                message_prefix = author_name + ": "

            messages[contact['id']].append(message_prefix + content) 
            d.append((author_id, content))
        """return all messages between you and given contact"""
        messages[contact['id']].reverse()
        print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
        return messages[contact['id']]




class Client(QtCore.QObject):
    def __init__(self, contact):
        super().__init__()

        self.client =  QtWebSockets.QWebSocket("",QtWebSockets.QWebSocketProtocol.Version13,None)
        self.client.error.connect(self.error)
        self.contact = contact
        self.client.open(QUrl(f"ws://localhost:8000/ws/chat/{contact['title']}/"))
        print(self.client.connected)
        self.client.pong.connect(self.onPong)

    def do_ping(self):
        print("client: do_ping")
        self.client.ping(b"foo")

    def on_open(self):
        self.client.sendTextMessage(json.dumps({
                    'type': 'join_conversation',
                    'conversation_id': f"{self.contact['id']}"
            }))

    def send_message(self):
        print("client: send_message")
        self.client.sendTextMessage("asd")

    def onPong(self, elapsedTime, payload):
        print("onPong - time: {} ; payload: {}".format(elapsedTime, payload))

    def error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.client.errorString())

    def close(self):
        self.client.close()

def quit_app(client):
    print("timer timeout - exiting")
    QCoreApplication.quit()

def ping(client):
    client.do_ping()

def send_message(client):
    client.send_message()


# def on_message(ws, message):
#     print(message)

# def on_error(ws, error):
#     print(error)

# def on_close(ws):
#     print("### closed ###")

# def on_open(ws, contact):
#     ws.send(json.dumps({
#                     'type': 'join_conversation',
#                     'conversation_id': f"{contact['id']}"
#             }))
#     print("wysłąno")
#     # ws.close()
#     print("koniec")
    
#     return 


# class Websocket():
#     def __init__(self, )

# class Client(QtCore.QObject):
#     def __init__(self, parent):
#         super().__init__(parent)

#         self.client =  QtWebSockets.QWebSocket("",QtWebSockets.QWebSocketProtocol.Version13,None)
#         self.client.error.connect(self.error)

#         self.client.open(QUrl("ws://127.0.0.1:1302"))
#         self.client.pong.connect(self.onPong)

#     def do_ping(self):
#         print("client: do_ping")
#         self.client.ping(b"foo")

#     def send_message(self):
#         print("client: send_message")
#         self.client.sendTextMessage("asd")

#     def onPong(self, elapsedTime, payload):
#         print("onPong - time: {} ; payload: {}".format(elapsedTime, payload))

#     def error(self, error_code):
#         print("error code: {}".format(error_code))
#         print(self.client.errorString())

#     def close(self):
#         self.client.close()

    
# class ListenWebsocket(QtCore.QThread):
#     def __init__(self, parent=None, conversation_name):

#         super(ListenWebsocket, self).__init__(parent)

#         websocket.enableTrace(True)

#         self.WS = websocket.WebSocketApp(f"ws://localhost:8000/chat/{conversation_name}",
#                                 on_message = self.on_message,
#                                 on_error = self.on_error,
#                                 on_close = self.on_close) 

#     def run(self):
#         #ws.on_open = on_open

#         self.WS.run_forever()

#  if (data.type == 'new_notification')
#             {
#                 document.querySelector('#chat-log').value += 'new message in: ' + (data.conversation_id + '\n');
#             }
#             else if (data.type == 'new_message')
#             {
#                 document.querySelector('#chat-log').value += 'author: ' + data.author + ' timestamp: ' + data.timestamp + ' new message: ' + (data.content + '\n');
#             }


    # def on_message(self, data):
    #     if data.type == 'new_notification':
    #         print("new massage in: " + ())

    #     elif data.type == 'new_message':
    #         print(f"author: {data.author}, timestamp: {data.timestamp}, new message: {data.content} \n")


    # def on_error(self, ws, error):
    #     print(error)

    # def on_close(self, ws):
    #     print("### closed ###")

    # document.querySelector('#chat-message-conversation-id-submit').onclick = function(e) {
    #         const messageInputDom = document.querySelector('#chat-message-conversation-id');
    #         const conversation_id = messageInputDom.value;
    #         chatSocket.send(JSON.stringify({
    #             'type': 'join_conversation',
    #             'conversation_id': conversation_id
    #         }));
    #     };