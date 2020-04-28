from PyQt5.QtWidgets import QMessageBox


def pop_alert(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle("Uwaga!")
    msg.exec_()
