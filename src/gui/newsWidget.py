from PyQt6.QtWidgets import (
    QHBoxLayout,
    QComboBox,
    QLabel,
    QToolButton,
    QApplication,
    QWidget,
    QPlainTextEdit,
)

from PyQt6 import QtGui, QtCore
from database.news import NewsModel


class NewsWidget(QWidget):
    def __init__(self, news: NewsModel, parent=None, isIndent=False):
        super(NewsWidget, self).__init__(parent)

        self.setMaximumSize(700, 80)
        self.QHBoxLayout = QHBoxLayout()

        self.ticName = QLabel()
        self.ticName.setText(f"{news.ticker_name}")
        self.ticName.setMaximumSize(60, 80)
        self.ticName.setStyleSheet(
            "border: none;\n background: transparent;\n color: red;\n margin-left:10px;"
        )

        created_at_time = news.created_at.strftime("%m/%d %H:%M")
        self.created_at = QLabel()
        self.created_at.setText(f"{created_at_time}")
        self.created_at.setMaximumSize(80, 80)
        self.created_at.setStyleSheet(
            "border: none;\n background: transparent;\n color: red;\n"
        )

        self.desc = QLabel()
        self.desc.setWordWrap(True)
        self.desc.setText(f"{news.title}:{news.short_content}")
        self.desc.setFixedSize(400, 80)
        self.desc.setStyleSheet(
            "border: none;\n background: transparent;\n margin-right:40px; \n text=align: right;"
        )

        self.author = QLabel()
        self.author.setText(f"{news.author}")
        self.author.setFixedSize(120, 80)
        self.author.setStyleSheet(
            "border: none;\n background: transparent; \n margin-right:20px;"
        )

        self.page = QLabel()
        self.page.setText(f"{news.page}")
        self.page.setMaximumSize(50, 80)
        self.page.setStyleSheet(
            "border: none;\n background: transparent;\n color: rgb(166, 169, 169);"
        )

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

        self.QHBoxLayout.addWidget(self.created_at)
        self.QHBoxLayout.addWidget(self.indentLabel)
        self.QHBoxLayout.addWidget(self.ticName)
        self.QHBoxLayout.addWidget(self.desc, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.QHBoxLayout.addWidget(self.author, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.QHBoxLayout.addWidget(self.page)

        self.QHBoxLayout.setContentsMargins(10, 5, 10, 5)

        self.setLayout(self.QHBoxLayout)
        self.url = news.url


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    myApp = NewsWidget()
    myApp.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print("Closing Window...")
