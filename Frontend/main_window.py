from PyQt5 import QtWidgets, uic
import sys

entries = ["Ania", "Asia", "Ala"]
messages = {"Ania": ["Ty: Mój stary to fanatyk wędkarstwa. Pół mieszkania zajebane wędkami najgorsze. Średnio raz w miesiącu ktoś wdepnie w leżący na ziemi haczyk czy kotwicę i trzeba wyciągać w szpitalu bo mają zadziory na końcu. W swoim 22 letnim życiu już z 10 razy byłem na takim zabiegu. Tydzień temu poszedłem na jakieś losowe badania to baba z recepcji jak mnie tylko zobaczyła to kazała buta ściągać xD bo myślała, że znowu hak w nodze. Druga połowa mieszkania zajebana Wędkarzem Polskim, Światem Wędkarza, Super Karpiem xD itp. Co tydzień ojciec robi objazd po wszystkich kioskach w mieście, żeby skompletować wszystkie wędkarskie tygodniki. Byłem na tyle głupi, że nauczyłem go into internety bo myślałem, że trochę pieniędzy zaoszczędzimy na tych gazetkach ale teraz nie dosyć, że je kupuje to jeszcze siedzi na jakichś forach dla wędkarzy i kręci gównoburze z innymi wędkarzami o najlepsze zanęty itp. Potrafi drzeć mordę do monitora albo wypierdolić klawiaturę za okno. Kiedyś ojciec mnie wkurwił to założyłem tam konto i go trolowałem pisząc w jego tematach jakieś losowe głupoty typu karasie jedzo guwno. Matka nie nadążała z gotowaniem bigosu na uspokojenie. Aha, ma już na forum rangę SUM, za najebanie 10k postów.Jak jest ciepło to co weekend zapierdala na ryby. Od jakichś 5 lat w każdą niedzielę jem rybę na obiad a ojciec pierdoli o zaletach jedzenia tego wodnego gówna. Jak się dostałem na studia to stary przez tydzień pie**olił że to dzięki temu, że jem dużo ryb bo zawierają fosfor i mózg mi lepiej pracuje.Co sobotę budzi ze swoim znajomym mirkiem całą rodzinę o 4 w nocy bo hałasują pakując wędki, robiąc kanapki itd.Przy jedzeniu zawsze pierdoli o rybach i za każdym razem temat schodzi w końcu na Polski Związek Wędkarski, ojciec sam się nakręca i dostaje strasznego bólu dupy durr niedostatecznie zarybiajo tylko kradno hurr, robi się przy tym cały czerwony i odchodzi od stołu klnąc i idzie czytać Wielką Encyklopedię Ryb Rzecznych żeby się uspokoić.W tym roku sam sobie kupił na święta ponton. Oczywiście do wigilii nie wytrzymał tylko już wczoraj go rozpakował i nadmuchał w dużym pokoju. Ubrał się w ten swój cały strój wędkarski i siedział cały dzień w tym pontonie na środku mieszkania. Obiad (karp) też w nim zjadł [cool][cześć]  ", "Ty: Cześć", "Ania: Co tam?", "Ty: HIPOPOTAM XDXDXD", "Ty: Jestem super"], "Asia" : ["Asia: hallooo", "Ty: eloo"], 
"Ala" : ["Ty: Hejka naklejka!"]}

def get_contacts():
    "function made for testing purposes"
    return entries

def get_messages(contact):
    "return all messages between you and given contact"
    return messages[contact]

def split_message(message, count=26):
    "split words to have at maximum 'count' characters "
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

class Ui(QtWidgets.QMainWindow):
    def setup_contacts(self):
        " show all contacs and groups of yours "
        for contact in get_contacts():
                new_item = QtWidgets.QListWidgetItem()
                new_item.setText(contact)
                self.list_contacts.addItem(new_item)
                
    def show_messages(self, item = None):
        "show messages between you and given contact named 'item'" 
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
        "send new message to contact. Usage: 'Ty: <message>' or '<contact_name>: <message>' for test purposes only"
        text = self.text_new_message.toPlainText()
        text = text
        if len(text) != 0:     
            messages[self.current_contact].append(text)
            self.show_messages()
            self.text_new_message.clear()

    def __init__(self):
        super(Ui, self).__init__()
        self.current_contact = None
        uic.loadUi('basic.ui', self)

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
        self.text_new_mssage = self.findChild(QtWidgets.QTextEdit, 'text_new_mssage')
        self.centralwidget = self.findChild(QtWidgets.QWidget, 'centralwidget')
        self.list_contacts = self.findChild(QtWidgets.QListWidget, 'list_contacts')
        self.list_contacts.itemClicked.connect(self.show_messages)
        self.list_messages = self.findChild(QtWidgets.QListWidget, 'list_messages')
        self.list_messages.setWordWrap(True)
        self.list_messages.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        
        
        
        self.setup_contacts()
        self.show()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()