import time
from threading import Thread
import json
import websocket
import zmq
from PyQt5 import QtCore
from vexmessage import create_vex_message, decode_vex_message



class Messenger(QtCore.QObject):
    message_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        websocket.enableTrace(True)
        self.callback_new_message_reveiced = []

    def add_callback_new_message_received(self, f):
        self.callback_new_message_reveiced.append(f)

    def on_message(self, data):
        data = json.loads(data)
        print(data)
        if(data['type'] == 'new_message'):
            for f in self.callback_new_message_reveiced:
                f(data)
            self.message_signal.emit()

                
            

    def on_error(self, *args):
        print('Errors:')
        print(args)

    def on_close(self):
        print("### closed ###")

    def subscribe_to_socket(self, address: str, token: str):
        headers = {'Authorization': 'Token ' + token}

        self.sub_socket = websocket.WebSocketApp(address,
                        header=headers,
                        on_message = self.on_message,
                        on_error = self.on_error,
                        on_close = self.on_close)

        self.thread = Thread(target=self.sub_socket.run_forever, daemon=True)
        self.thread.start()

    def publish_message(self, message, conversation_id):
        data = {
                'type': 'message',
                'content': message,
                'conversation_id': conversation_id
            }
    
        self.sub_socket.send(json.dumps(data))

