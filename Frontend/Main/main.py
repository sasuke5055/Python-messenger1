
from PyQt5 import QtWidgets
from GuiClasses.Login_window import LoginWindow

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Login_window = QtWidgets.QMainWindow()
    ui = LoginWindow()
    sys.exit(app.exec_())
