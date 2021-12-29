from PyQt6.QtWidgets import (
    QHBoxLayout,
    QComboBox,
    QLabel,
    QToolButton,
    QApplication,
    QWidget,
    QListWidgetItem,
)

from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QThread

from PyQt6 import QtGui, QtCore
from scrapper.ticker import Ticker
from alarm.email_alarm import send_notification


class RefreshPriceWorker(QObject):
    progress = pyqtSignal()

    def run(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.process)
        self._timer.start(1000)

    def stop(self):
        self._timer.stop()
        print("timer stop")

    def process(self):
        self.progress.emit()
        QThread.sleep(1)


class AlarmWidget(QWidget):
    def __init__(
        self,
        ticker: Ticker,
        parent=None,
        targetPrice="100",
        isUpBound=True,
        isIndent=False,
    ):
        super(AlarmWidget, self).__init__(parent)

        self.setMaximumSize(700, 40)
        self.QHBoxLayout = QHBoxLayout()

        self.ticker = ticker
        if ticker.company_name == None:
            raise Exception(f"ticker {ticker.name} is not valid")
        company_names = ticker.company_name.split(" ")
        if len(company_names) > 2:
            company_name = " ".join(company_names[:2])
        else:
            company_name = ticker.company_name

        self.ticName = QLabel()
        self.ticName.setText(f"{ticker.name}/{company_name}")
        self.ticName.setMaximumSize(150, 60)
        self.ticName.setStyleSheet(
            "border: none;\n background: transparent;\n color: blue;"
        )

        self.ticCurPriceLabel = QLabel()
        self.ticCurPriceLabel.setText("Price:")
        self.ticCurPriceLabel.setMaximumSize(50, 60)
        self.ticCurPriceLabel.setStyleSheet("border: none;\n background: transparent;")

        self.ticCurPrice = QLabel()
        self.ticCurPrice.setText("$")
        self.ticCurPrice.setMaximumSize(120, 60)
        self.ticCurPrice.setStyleSheet("color: green;\n border: none;")

        self.targetPriceLabel = QLabel()
        self.targetPriceLabel.setText("Target:")
        self.targetPriceLabel.setMaximumSize(50, 60)
        self.targetPriceLabel.setStyleSheet("border: none;\n background: transparent;")

        self.targetPrice = QLabel()
        self.targetPrice.setText(f"${targetPrice}")
        self.targetPrice.setMaximumSize(60, 60)
        self.targetPrice.setStyleSheet(
            "color: black;\nborder: none;\n background: transparent;"
        )

        self.typeBound = QToolButton()
        self.typeBound.setStyleSheet(
            "border: None;\n background-color: rgb(255, 255, 255);"
        )
        self.isUpBound = isUpBound
        icon_name = "up-arrow.png" if self.isUpBound else "down-arrow.png"
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(f"src/gui/icons/{icon_name}"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.typeBound.setIcon(icon)

        self.isBell = True
        self.aBellButton = QToolButton()
        self.aBellButton.setStyleSheet(
            "border: None;\nbackground-color: rgb(255, 255, 255)"
        )
        icon_name = "bell.png" if self.isBell else "bell-crossed.png"
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(f"src/gui/icons/{icon_name}"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.aBellButton.setIcon(icon)

        self.indentLabel = QToolButton()
        self.indentLabel.setStyleSheet(
            "border: None;\n background-color: rgb(255, 255, 255);"
        )
        self.isIndent = isIndent
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap("src/gui/icons/right.png"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.indentLabel.setIcon(icon)
        self.indentLabel.setEnabled(False)
        self.indentLabel.setHidden(True)

        self.QHBoxLayout.addWidget(self.indentLabel)
        self.QHBoxLayout.addWidget(self.ticName)
        self.QHBoxLayout.addWidget(self.ticCurPriceLabel)
        self.QHBoxLayout.addWidget(
            self.ticCurPrice, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.QHBoxLayout.addWidget(self.targetPriceLabel)
        self.QHBoxLayout.addWidget(
            self.targetPrice, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.QHBoxLayout.addWidget(self.typeBound, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.QHBoxLayout.addWidget(self.aBellButton)
        self.setLayout(self.QHBoxLayout)
        self.QHBoxLayout.setContentsMargins(10, 0, 10, 0)
        self.typeBound.clicked.connect(self.typeBellClickedHandler)
        self.aBellButton.clicked.connect(self.aBellButtonClickedHandler)

        self.set_price()

    def typeBellClickedHandler(self):
        self.isUpBound = not self.isUpBound

        icon_name = "up-arrow.png" if self.isUpBound else "down-arrow.png"
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(f"src/gui/icons/{icon_name}"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.typeBound.setIcon(icon)

    def aBellButtonClickedHandler(self):
        self.isBell = not self.isBell
        icon_name = "bell.png" if self.isBell else "bell-crossed.png"
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(f"src/gui/icons/{icon_name}"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.aBellButton.setIcon(icon)

    def set_price(self):
        try:
            price = self.ticker.price
        except Exception as e:
            print(e)
            raise Exception(f"price of {self.ticker.name} is not available")
        self.ticCurPrice.setText(
            f"${price.current_price} ({price.price_change_percentage})%"
        )
        if price.price_change == 0:
            self.ticCurPrice.setStyleSheet("color: black;")
        elif price.price_change > 0:
            self.ticCurPrice.setStyleSheet("color: green;")
        else:
            self.ticCurPrice.setStyleSheet("color: red;")

        targetPrice = float(self.targetPrice.text()[1:])
        if self.isBell:
            if price.current_price >= targetPrice and self.isUpBound:
                subject = f"{self.ticker.name} went above ${targetPrice}"
                message = f"{self.ticker.name} went above ${targetPrice}"
                self.send_email(subject, message)
                self.aBellButtonClickedHandler()
                self.targetPrice.setStyleSheet("color: blue;")

            elif price.current_price <= targetPrice and not self.isUpBound:
                subject = f"{self.ticker.name} went below ${targetPrice}"
                message = f"{self.ticker.name} went below ${targetPrice}"
                self.send_email(subject, message)
                self.aBellButtonClickedHandler()
                self.targetPrice.setStyleSheet("color: blue;")

    def send_email(self, subject, message):
        send_notification(subject=subject, message=message)

    def price_update_start(self):
        self.thread = QThread()
        self.worker = RefreshPriceWorker()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.set_price)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.worker.stop)
        self.thread.start()

    def price_update_end(self):
        self.thread.quit()
        self.thread.wait()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    myApp = AlarmWidget()
    myApp.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print("Closing Window...")
