import sys

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from gui.mainWindow import Ui_MainWindow
from gui.alarmWidget import AlarmWidget
from scrapper.ticker import Ticker, TickerModel

from database.tool import Base, session, engine

from database.news import NewsModel
from gui.newsWidget import NewsWidget
from PyQt6.QtCore import (
    QTimer,
    pyqtSignal,
    QObject,
    QThread,
    QRegularExpression as QRegExp,
)
from PyQt6.QtGui import QRegularExpressionValidator as QRegExpValidator
from scrapper import web_scrapper, twitter_scrapper

import webbrowser

import datetime

from sqlalchemy import and_

import yaml


class RefreshNews(QObject):
    progress = pyqtSignal(list)
    progressed = pyqtSignal()

    def run(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.process)
        self._timer.start(120000)

    def stop(self):
        self._timer.stop()
        print("timer stop")

    def process(self):
        with open("src/resources.yml", "r") as f:
            cfg = yaml.load(f.read(), Loader=yaml.FullLoader)
        tickers = cfg["tickers"]
        self.progress.emit(tickers)
        QThread.sleep(2)
        self.progressed.emit()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # setup UI
        self.setupUi(self)
        self.aTicButton.clicked.connect(self.aTicButtonClickedHandler)
        self.aTicListWidget.itemClicked.connect(self.aTicListWidgetClickedHandler)
        self.aTicListWidget.keyReleased.connect(self.aTicListWidgetKeyPressed)

        self.nTicListWidget.itemClicked.connect(self.nTicListWidgetClickedHandler)
        self.nTicListWidget.itemDoubleClicked.connect(
            self.nTicListWidgetDoubleClickedHandler
        )

        self.newsListWidget.itemClicked.connect(self.newsListWidgetClickedHandler)
        self.newsListWidget.itemDoubleClicked.connect(
            self.newsListWidgetDoubleClickedHandler
        )

        self.setup_nTicNameComboBox()
        self.nTicNameComboBox.textActivated.connect(
            self.nTicNameComboBoxtextActivatedHandler
        )
        self.runRefreshNews()

        regexp = QRegExp(r"[A-Z]{0,5}")
        validator = QRegExpValidator(regexp)
        self.aTicNameLineBox.setValidator(validator)

    def nTicListWidgetDoubleClickedHandler(self, item):
        newsWidget: NewsWidget = self.nTicListWidget.itemWidget(item)
        webbrowser.open(newsWidget.url)

    def newsListWidgetDoubleClickedHandler(self, item):
        newsWidget: NewsWidget = self.newsListWidget.itemWidget(item)
        webbrowser.open(newsWidget.url)

    def runRefreshNews(self):
        self.thread = QThread()
        self.worker = RefreshNews()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(web_scrapper.run)
        self.worker.progress.connect(twitter_scrapper.run)
        self.worker.progressed.connect(self.refreshListWidgets)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.worker.stop)
        self.thread.start()

    def refreshListWidgets(self):
        self.nTicNameComboBoxtextActivatedHandler(self.nTicNameComboBox.currentText())
        self.refreshNewsListWidget()

    def refreshNewsListWidget(self):
        hours_limit = 2
        created_at = datetime.datetime.now() - datetime.timedelta(hours=hours_limit)
        created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")

        news_list = (
            session.query(NewsModel)
            .filter(
                NewsModel.created_at >= created_at,
            )
            .order_by(NewsModel.created_at.desc())
            .all()
        )

        for news in news_list:
            widget: NewsWidget = NewsWidget(news=news)
            widget.desc.setFixedSize(300, 80)
            # widget.ticName.setHidden(True)
            itemN = QListWidgetItem()
            itemN.setSizeHint(widget.sizeHint())
            self.newsListWidget.addItem(itemN)
            self.newsListWidget.setItemWidget(itemN, widget)

    def setup_nTicNameComboBox(self):
        self.nTicNameComboBox.clear()
        tickers = session.query(TickerModel).all()
        ticker_names = ["----"] + [ticker.name for ticker in tickers]
        self.nTicNameComboBox.addItems(ticker_names)

    def nTicNameComboBoxtextActivatedHandler(self, ticker_name):

        for _ in range(self.nTicListWidget.count()):
            self.nTicListWidget.takeItem(0)

        days_limit = 2
        created_at = datetime.datetime.now() - datetime.timedelta(days=days_limit)
        created_at = created_at.strftime("%Y-%m-%d")

        if ticker_name == "----":
            return

        news_list = (
            session.query(NewsModel)
            .filter(
                and_(
                    NewsModel.ticker_name == ticker_name,
                    NewsModel.created_at >= created_at,
                )
            )
            .order_by(NewsModel.created_at.desc())
            .all()
        )

        for news in news_list:
            widget = NewsWidget(news=news)
            widget.ticName.setHidden(True)
            itemN = QListWidgetItem()
            itemN.setSizeHint(widget.sizeHint())
            self.nTicListWidget.addItem(itemN)
            self.nTicListWidget.setItemWidget(itemN, widget)

    def nTicListWidgetClickedHandler(self):
        try:
            last_index = self.nTicListWidget.lastRowIndex
            last_item = self.nTicListWidget.item(last_index)
            newsWidget = self.nTicListWidget.itemWidget(last_item)
            newsWidget.indentLabel.setHidden(True)
        except Exception as e:
            print(e)

        row_index = self.nTicListWidget.currentRow()
        rowItem = self.nTicListWidget.item(row_index)
        newsWidget: NewsWidget = self.nTicListWidget.itemWidget(rowItem)
        newsWidget.indentLabel.setHidden(False)
        self.nTicListWidget.lastRowIndex = row_index

    def newsListWidgetClickedHandler(self):
        try:
            last_index = self.newsListWidget.lastRowIndex
            last_item = self.newsListWidget.item(last_index)
            newsWidget = self.newsListWidget.itemWidget(last_item)
            newsWidget.indentLabel.setHidden(True)
        except Exception as e:
            print(e)

        row_index = self.newsListWidget.currentRow()
        rowItem = self.newsListWidget.item(row_index)
        newsWidget: NewsWidget = self.newsListWidget.itemWidget(rowItem)
        newsWidget.indentLabel.setHidden(False)
        self.newsListWidget.lastRowIndex = row_index

    def aTicButtonClickedHandler(self):
        ticker_name = self.aTicNameLineBox.text()
        targetPrice = self.aTicValSpinBox.value()
        bound = self.aTicComboBox.currentText()
        isUpBound = True if bound.lower() == "up" else False
        ticker = Ticker(name=ticker_name)
        try:
            widget = AlarmWidget(
                ticker=ticker,
                targetPrice=targetPrice,
                isUpBound=isUpBound,
            )
        except Exception as e:
            print(e)
            return
        itemN = QListWidgetItem()
        itemN.setSizeHint(widget.sizeHint())
        self.aTicListWidget.addItem(itemN)
        self.aTicListWidget.setItemWidget(itemN, widget)
        widget.price_update_start()

    def aTicListWidgetClickedHandler(self):
        try:
            last_index = self.aTicListWidget.lastRowIndex
            last_item = self.aTicListWidget.item(last_index)
            alarmWidget = self.aTicListWidget.itemWidget(last_item)
            alarmWidget.indentLabel.setHidden(True)
        except Exception as e:
            print(e)

        row_index = self.aTicListWidget.currentRow()
        rowItem = self.aTicListWidget.item(row_index)
        alarmWidget: AlarmWidget = self.aTicListWidget.itemWidget(rowItem)
        alarmWidget.indentLabel.setHidden(False)
        self.aTicListWidget.lastRowIndex = row_index

    def aTicListWidgetKeyPressed(self, key):
        if key == Qt.Key.Key_Backspace:
            row_index = self.aTicListWidget.currentRow()
            rowItem = self.aTicListWidget.item(row_index)
            rowItemWidget: AlarmWidget = self.aTicListWidget.itemWidget(rowItem)
            rowItemWidget.price_update_end()
            self.aTicListWidget.lastRowIndex = None
            self.aTicListWidget.takeItem(row_index)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CTA App")
    w = MainWindow()
    w.setStyleSheet(
        """
            QMainWindow
            {
            background-color: rgb(255, 255, 255);\n
            }\n
            QListWidget::item:selected
            {
            background: rgb(255, 255, 255);
            }
        """
    )
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
