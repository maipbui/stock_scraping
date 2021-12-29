from PyQt6 import QtCore, QtGui, QtWidgets


class QCustomListWidget(QtWidgets.QListWidget):
    keyReleased = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyReleaseEvent(self, event):
        super(QCustomListWidget, self).keyPressEvent(event)
        self.keyReleased.emit(event.key())
