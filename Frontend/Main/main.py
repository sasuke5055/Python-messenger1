import sys
import asyncio
from PyQt5 import QtWidgets
from quamash import QEventLoop
from GuiClasses.Login_window import LoginWindow
from zmq.error import ZMQError
from config import getURL, getWSURL


def main():
    app = QtWidgets.QApplication(sys.argv)

    # create the event loop and set it in asyncio
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    # login_window = QtWidgets.QMainWindow()
    ui = LoginWindow([getURL(), getWSURL()])

    try:
        event_loop.run_forever()
    # catch ctrl-C event to allow for graceful closing
    except KeyboardInterrupt:
        pass

    app.deleteLater()
    event_loop.close()
    sys.exit()


if __name__ == '__main__':
    main()