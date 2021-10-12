import json
import re
import os
import res
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ui import Ui_profithelper
from sys import exit, argv
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont

settings_path = os.path.abspath('config.json')
with open(settings_path, 'r') as conf:
    settings = json.load(conf)


class MyHandler(FileSystemEventHandler):

    def on_created(self, event):
        with open(event.src_path, 'r') as f:
            lines = f.readlines()
            sell_price = float(lines[1].split(',')[0])
            sell_broker = (sell_price / 100) * float(settings['broker_tax'])
            sell_tax = (sell_price / 100) * float(settings['sell_tax'])
            sell = sell_price - sell_tax - sell_broker

            for i in lines:
                if re.search(r'\bTrue\b', i):
                    buy_price = float(i.split(',')[0])
                    buy_broker = (buy_price / 100) * float(settings['broker_tax'])
                    buy = buy_price + buy_broker
                    profit = sell - buy

                    ui.sell_price_value.setText(f'{sell:,.2f}'.replace(',', ' '))
                    ui.buy_price_value.setText(f'{buy:,.2f}'.replace(',', ' '))
                    ui.profit_value.setText(f'{profit:,.2f}'.replace(',', ' '))

                    if profit < 0:
                        ui.profit_value.setStyleSheet('color: #cc0000')
                    else:
                        ui.profit_value.setStyleSheet('color: #008000')
                    break


app = QtWidgets.QApplication(argv)

montserrat_regular_font = QFontDatabase.addApplicationFont(":/fonts/Montserrat-ExtraBoldItalic.ttf")
if montserrat_regular_font == -1:
    print('Шрифт somefont не установлен')

MainWindow = QtWidgets.QMainWindow()
MainWindow.setWindowFlag(Qt.WindowStaysOnTopHint)
MainWindow.setStyleSheet('background-color: #787878')
ui = Ui_profithelper()
ui.setupUi(MainWindow)
MainWindow.show()

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path=settings["logs_path"], recursive=False)
observer.start()

exit(app.exec_())
